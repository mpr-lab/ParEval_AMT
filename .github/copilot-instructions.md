# ParEval_AMT Copilot Instructions

## Project Overview

ParEval_AMT is an HPC benchmark for evaluating LLMs' ability to write parallel C++ code. It extends the original [ParEval](https://github.com/parallelcodefoundry/ParEval) benchmark with support for HPX (1.5.1 and 1.10.0), Legion, and HPX→Legion translation. The workflow has three phases: **generate** → **clean** → **evaluate (drivers)** → **analyze**.

Parallelism models under test: `serial`, `omp`, `mpi`, `mpi+omp`, `kokkos`, `cuda`, `hip`, `hpx`.

## Environment Setup

```sh
# Clone with submodules
git clone --recurse-submodules git@github.com:mpr-lab/ParEval_AMT.git

# On Unity HPC cluster
module load cuda/12.1
module load conda/latest
conda env create --file environment.yml
conda activate hpc_llm

# Python deps (alternative, use uv)
pip install uv
uv add -r requirements_AMT.txt
# Or activate the shared Unity venv:
source /work/pi_mrobson_smith_edu/pareval/.venv/bin/activate

# HPX environments on Unity (must source before running HPX drivers)
source /work/pi_mrobson_smith_edu/.hpx_tcmalloc_1.5.1   # HPX 1.5.1
source /work/pi_mrobson_smith_edu/.hpx_1_10_0            # HPX 1.10.0
```

Build the C++ driver object files before running evaluations:
```sh
cd drivers/cpp && make
```

## Key Commands

### Generation
```sh
# Local HuggingFace model
python generate/generate.py \
  --prompts prompts/generation-prompts.json \
  --model <hf-model-or-path> \
  --output outputs.json \
  --num_samples_per_prompt 50 \
  --prompted   # recommended: append _solution_ comment like StarCoder paper

# OpenAI / Gemini API
python generate/generate-openai.py --help
python generate/generate-gemini.py --help

# Claude Batch API pipeline (see claude/README.md for full 8-stage process)
python claude/make_request.py ../prompts/fft.json ../prompts/sort.json \
  --out-dir claude/ --max-tokens 2048 --thinking-budget 1400
```

### Evaluate generated outputs
```sh
# Run all (from drivers/)
python drivers/run-all.py generated-outputs.json -o results.json --yes-to-all

# Single problem type, HPX only
python drivers/run-all.py generated-outputs.json \
  --include-models hpx \
  --problem-type stencil \
  --build-timeout 30 --run-timeout 45 \
  --log-build-errors --log-runs

# Dry run (no execution, for testing setup)
python drivers/run-all.py generated-outputs.json --dry
```

### Analysis
```sh
# Convert results JSON → CSV
python analysis/create-dataframe.py results.json -o results.csv

# Compute pass@k, efficiency@k, speedup@k, build@k
python analysis/metrics.py results.csv -k 1 5 10 -o metrics.csv

# Scaling metrics
python analysis/metrics-scaling.py results.csv -o scaling.csv
```

## Architecture

```
prompts/*.json          → prompt dataset (input)
generate/               → LLM code generation (local, OpenAI, Gemini, Claude)
claude/                 → 8-stage Claude Batch API pipeline (see claude/README.md)
clean_prompts/          → output cleaning scripts (strip markdown, extract function bodies)
drivers/run-all.py      → compile & run generated code, produce results JSON
analysis/               → compute metrics from results CSV
srun_generate/          → SLURM job scripts for generation on Unity
run_driver/             → SLURM job scripts for driver execution on Unity
```

### Prompt / Output JSON Schema

Prompts (`prompts/generation-prompts.json`):
```json
[{
  "problem_type": "stencil",
  "language": "cpp",
  "name": "17_problem_name",
  "parallelism_model": "hpx",
  "prompt": "/* ... */\nvoid foo(int x) {"
}]
```

Generated outputs add an `outputs` array (list of generated code strings) and `temperature`, `prompted` fields.

### Driver Organization

- `drivers/cpp/benchmarks/<problem-type>/<problem-name>/<model>.<ext>` — test logic per problem
- `drivers/cpp/models/<model>-driver.<ext>` — `main()` for each execution model
- Naming and spelling of model keys must exactly match the parallelism model strings above (used as dict keys)
- `drivers/build-configs.json` — per-model compiler flags (`g++`, `mpicxx`, `nvcc`, `hipcc`, `c++` for HPX)
- `drivers/launch-configs.json` — per-model SLURM srun launch templates and thread/process parameter sweeps

## Key Conventions

### OMP thread count
OMP executables receive thread count as the **first CLI argument**, not via `OMP_NUM_THREADS`. The launcher does not use a shell, so environment variable injection like `OMP_NUM_THREADS=4 ./a.out` does not work:
```sh
./a.out 4   # correct for OMP binaries
```

### HPX thread count
HPX executables receive `--hpx:threads={num_threads}` as a CLI argument.

### MPI correctness
The correct result must be returned on **rank 0**. Initial data distribution varies by problem.

### Scratch directory for MPI
`/tmp` is node-local on most clusters. Use `--scratch-dir` pointing to a shared filesystem when running MPI benchmarks:
```sh
python run-all.py outputs.json --scratch-dir /work/.../scratch
```

### Adding a new LLM
Define an inference config in `generate/utils.py`. Existing examples cover HuggingFace pipeline models, chat templates, and stopping criteria.

### Cleaning generated outputs
Raw LLM output contains markdown fences, `#include` lines, and prose. Use:
- `clean_prompts/clean_output_bulk.py -i <dir>` — general bulk cleaner
- `claude/clean_claude.py` — extracts first C++ function body via brace-matching (Claude outputs)
- `claude/clean_geometry.py` — lighter cleaner (removes fences and `#include` only)

### Caching and resuming generation
Pass `--cache <file>.jsonl` to `generate.py` to cache incremental results. Resume by re-running the same command (already-completed prompts are skipped). Use `--restart` to force regeneration.

### API keys
Set via environment variables before running API-based generation:
```sh
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="..."
```

### Kokkos build
Kokkos source lives under `tpl/kokkos/kokkos`. Build and install to `tpl/kokkos/build/` (where Makefiles look for includes and `.a` files):
```sh
cmake -B builddir -DCMAKE_CXX_COMPILER=g++ -DCMAKE_BUILD_TYPE=Release \
  -DKokkos_ENABLE_OPENMP=ON -DKokkos_ARCH_NATIVE=ON ...
cmake --build builddir
cmake --install builddir --prefix tpl/kokkos/build
```

### Claude batch pipeline
The `claude/` directory implements an 8-stage pipeline: generate requests → expand for pass@k → submit to Anthropic → retrieve → convert to eval JSON → clean → split by problem type → run on Unity via SLURM. See `claude/README.md` for the full command reference.

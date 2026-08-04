# ParEval AMT — Copilot Instructions

## Overview

ParEval AMT is a benchmark for evaluating LLMs' ability to write and translate parallel C++ code. It extends the original [ParEval](https://github.com/parallelcodefoundry/ParEval) benchmark to include **HPX** and **Legion** generation, as well as **HPX → Legion translation**.

The three-stage workflow is:
1. **Generate** — use an LLM to produce code samples from prompts
2. **Clean** — post-process raw LLM output to extract compilable code
3. **Drive** — compile, run, and benchmark the generated code, then compute metrics

## Environment Setup

Runs on the **Unity HPC cluster**. Key environment setup:

```sh
# Clone with submodules (tpl/kokkos)
git clone --recurse-submodules git@github.com:mpr-lab/ParEval_AMT.git

# Conda environment
module load conda/latest
conda env create --file environment.yml
conda activate hpc_llm

# For CUDA support
module load cuda/12.1

# HPX environments (two versions tested)
source /work/pi_mrobson_smith_edu/.hpx_tcmalloc_1.5.1   # HPX 1.5.1
source /work/pi_mrobson_smith_edu/.hpx_1_10_0            # HPX 1.10.0

# Python deps (if not using conda env)
pip install uv && uv add -r requirements_AMT.txt

# Pre-built venv on Unity
source /work/pi_mrobson_smith_edu/pareval/.venv/bin/activate
```

Build C++ drivers before running evaluations:
```sh
cd drivers/cpp && make
```

## Stage 1: Generate

Scripts in `generate/` and `srun_generate/` (SLURM wrappers per problem type).

```sh
# Local/HuggingFace model
python generate/generate.py \
  --prompts prompts/transform.json \
  --model <model-path-or-hf-handle> \
  --output outputs/transform_results.json \
  --cache outputs/transform_cache.jsonl \
  --num_samples_per_prompt 50 \
  --temperature 0.2 --top_p 0.95 --do_sample --prompted

# OpenAI API
python generate/generate-openai.py \
  -m gpt-4-1106-preview \
  -p prompts/transform.json \
  -o outputs/transform_gpt4.json

# Gemini API
python generate/generate-gemini.py ...

# Translation task (HPX -> Legion)
python generate/translate-openai.py ...
```

`--prompted` appends `_solution_` comments (StarCoder-style) and almost always improves results — use it.

New LLMs require an inference config entry in `generate/utils.py`.

## Stage 2: Clean

Run from the `clean_prompts/` directory.

```sh
# Inspect raw output
python clean_prompts/parse_to_txt.py /path/to/output.json

# Clean a directory of JSON outputs (standard C++)
python clean_prompts/clean_output_bulk.py -i /path/to/dir/of/jsons
# → writes cleaned/ subdirectory

# Python outputs
python clean_prompts/clean_output_bulk_python.py -i /path/to/cache/hpc-coder.json

# Markdown-wrapped Python (e.g., magicoder)
python clean_prompts/clean_output_bulk_python_markdown.py -i /path/to/magicoder.json
```

## Stage 3: Drive & Analyze

```sh
# Run all models for a problem set
cd drivers
python run-all.py /path/to/cleaned/outputs.json \
  -o results.json \
  --launch-configs launch-configs.json \
  --build-configs build-configs.json \
  --problem-sizes problem-sizes.json \
  --scratch-dir /path/to/shared/scratch   # required for MPI (shared FS)

# Filter to specific parallelism model
python run-all.py outputs.json --include-models hpx
python run-all.py outputs.json --include-models serial omp

# Single problem
python run-all.py outputs.json --problem 17_transform_gemm

# Dry run (check setup without executing)
python run-all.py outputs.json --dry
```

**Do not run `run-all.py` on a login node** without `--dry`.

OMP drivers take thread count as the first CLI argument (e.g., `./a.out 4`), not via `OMP_NUM_THREADS`.

### Combining and analyzing results

```sh
# Combine multiple driver result JSONs
python clean_prompts/combine_runs.py /path/to/problem/dir/

# Convert JSON results → CSV
python clean_prompts/create-dataframe_bulk.py /path/to/dir/of/jsons/

# Compute pass@k, build@k, speedup@k metrics
python clean_prompts/metrics_from_dir.py /path/to/dir/of/jsons/ \
  -n 100 \
  --problem-size /work/pi_mrobson_smith_edu/ParEval_amt/drivers/problem-sizes.json
# → data.csv

# Graphing
python analysis/runtimes.py /path/to/dir/of/csvs/
python analysis/specific_runtimes.py /path/to/dir/of/jsons/
```

## Data Formats

**Prompt JSON** (input to generate):
```json
[{
  "problem_type": "stencil",
  "language": "cpp",
  "name": "17_problem_name",
  "parallelism_model": "serial",
  "prompt": "/* ... */\nvoid foo(int x) {"
}]
```

**Output JSON** (generate → clean → drive): each entry adds `outputs` (list of code strings), then driver appends `is_valid`, `did_build`, runtime fields per output.

## Key Conventions

- **Parallelism models**: `serial`, `omp`, `mpi`, `mpi+omp`, `kokkos`, `cuda`, `hip`, `hpx`. These strings are used as exact keys throughout code and file naming.
- **Driver naming**: benchmarks follow `benchmarks/<problem-type>/<problem-name>/<model>.<ext>`; model drivers follow `models/<model>-driver.<ext>`.
- **Two HPX versions** (1.5.1 and 1.10.0) are tested separately and require different source environments.
- **MPI correctness** is checked on rank 0 only; initial data distribution varies by problem.
- **Generation caching**: `--cache` (JSONL) enables resumable generation; `--restore_from` restores from a JSON file with matching prompts.
- Problem categories: `fft`, `futures_promises`, `geometry`, `graph`, `histogram`, `dense_la` (la), `locking_contention`, `reduce`, `scan`, `search`, `sort`, `stencil`, `transform`.

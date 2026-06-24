# Chapel Driver Harness

This directory contains the Chapel language driver harness for ParEval_AMT, enabling evaluation of LLM-generated Chapel parallel code using the same infrastructure as the C++ drivers.

## Overview

Each benchmark under `benchmarks/<problem_type>/<name>/driver.chpl` is a complete self-contained Chapel program that:

1. Defines a **serial baseline** (`correct*` proc) for validation
2. Validates the **LLM-generated proc** against the baseline (two trials, element-wise comparison)
3. Times both the generated and baseline implementations over multiple iterations
4. Prints output in the format expected by the Python evaluation harness

## Directory Structure

```
drivers/chapel/
├── README.md                          # This file
├── __init__.py                        # Python package marker
├── chapel_driver_wrapper.py           # Python wrapper: compile, run, parse results
└── benchmarks/
    ├── dense_la/       {00..04}
    ├── fft/            {05..09}
    ├── geometry/       {10..14}
    ├── graph/          {15..19}
    ├── histogram/      {20..24}
    ├── reduce/         {25..29}
    ├── scan/           {30..34}
    ├── search/         {35..39}
    ├── sort/           {40..44}
    ├── sparse_la/      {45..49}
    ├── stencil/        {50..54}
    ├── transform/      {55..59}
    ├── locking_contention/ {60..64}
    └── futures_promises/   {65..69}
```

70 `driver.chpl` files total (14 problem types × 5 problems each).

## How It Works

### Compilation

The Python wrapper compiles the driver together with the LLM-generated file:

```sh
chpl --fast driver.chpl generated-code.chpl -o a.out
```

### Runtime

```sh
./a.out --problemSize=<N> --numThreadsPerLocale=<T>
```

Both `problemSize` and `numThreadsPerLocale` are Chapel `config const` variables, overridden on the command line.

### Expected Output Format

```
Validation: PASS
Time: 0.001234
BestSequential: 0.000567
```

`Time` and `BestSequential` are only printed when validation passes. The Python harness parses these three lines regardless of order.

## Running Evaluations

```sh
cd drivers/

# Run all Chapel benchmarks in a generated-outputs JSON
python run-all.py your_outputs.json --include-models chapel

# Specific problem type only
python run-all.py your_outputs.json --include-models chapel --problem-type stencil

# With custom timeouts and logging
python run-all.py your_outputs.json \
  --include-models chapel \
  --build-timeout 60 \
  --run-timeout 120 \
  --log-build-errors --log-runs

# Dry run (no execution)
python run-all.py your_outputs.json --include-models chapel --dry
```

## Generated Output JSON Format

Your generated outputs JSON must have:

```json
{
  "language": "chapel",
  "parallelism_model": "chapel",
  "problem_type": "stencil",
  "name": "52_stencil_1d_jacobi_3-point_stencil",
  "outputs": ["proc jacobi1D(...) { ... }", "..."]
}
```

## Configuration Files Modified

| File | Change |
|---|---|
| `drivers/build-configs.json` | Added `"chapel": {"CHPL": "chpl", "CHPLFLAGS": "--fast"}` |
| `drivers/launch-configs.json` | Added `chapel` entry; thread sweep 1,2,4,8,16,32,64 via `--numThreadsPerLocale` |
| `drivers/problem-sizes.json` | Added `"chapel"` key to all 60 benchmarks (same sizes as HPX) |
| `drivers/driver_wrapper.py` | Registered `.chpl` extension, `driver` file base, `ChapelValidator` |
| `drivers/cpp/parallel_validation.py` | Added `ChapelValidator` (checks for `forall`, `coforall`, `cobegin`, `begin`, `on Locales`) |
| `drivers/run-all.py` | Imported `ChapelDriverWrapper`, registered under `"chapel"` key |

## Chapel Parallelism Keywords Validated

The `ChapelValidator` requires generated code to contain at least one of:

- `forall` — parallel loop
- `coforall` — concurrent task per iteration
- `cobegin` — concurrent statement block
- `begin ` — fire-and-forget task
- `on Locales` — multi-locale execution

## Chapel-Specific Notes

### Thread Count
Chapel executables receive thread count via `--numThreadsPerLocale={T}`, not via environment variables.

### Problem Size
Problem size is a `config const` overridden at runtime: `./a.out --problemSize=262144`

### Type Mapping from C++
| C++ | Chapel |
|---|---|
| `std::vector<double>` | `[] real` (0-indexed) |
| `std::complex<double>` | `complex(128)` (`.re`, `.im`) |
| `size_t` / `int` | `int` (64-bit by default) |
| `struct` | `record` |
| `std::sort` | `use Sort; sort(arr, comparator=...)` |
| Timer | `use Time; var sw: stopwatch; sw.restart(); ...; sw.elapsed()` |
| RNG | `use Random; var rs = new randomStream(real, seed=N); rs.fill(arr)` |

## Environment

Chapel must be installed and `chpl` available on `PATH`. On Unity HPC:

```sh
module load chapel   # or add chpl to PATH manually
```

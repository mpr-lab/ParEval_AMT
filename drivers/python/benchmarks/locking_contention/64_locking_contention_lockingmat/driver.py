#!/usr/bin/env python3
"""charm4py benchmark driver for 64_locking_contention_lockingmat

Sparse matrix row accumulation with locking semantics.
The function under test accumulates two sparse input vectors into one row of a
sparse matrix represented as sorted column-index / coefficient lists.

Function signature:
    locking_mat_add(matrix, target_row, in1_idx, in1_coef, in2_idx, in2_coef)
      -> list of updated row coefficients

Where matrix is a dict:
    {
      'rows':        list of global row ids stored locally (sorted),
      'row_indices': list of lists of sorted column indices per row,
      'row_coefs':   list of lists of coefficients per row,
    }
"""
import argparse, importlib.util, random, time, bisect
from charm4py import charm

PROBLEM_SIZE = 1 << 9  # matches C++ default; must be >= 4
NITER = 3
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def make_matrix(problem_size):
    """Build a SimpleMatrix-equivalent Python dict with one row of `problem_size` entries."""
    problem_size = max(4, problem_size)
    idx_row = list(range(problem_size))   # column indices 0..problem_size-1
    coef_row = [0.0] * problem_size
    return {
        'rows': [0],
        'row_indices': [idx_row],
        'row_coefs': [coef_row],
    }


def reset_matrix(matrix):
    for coefs in matrix['row_coefs']:
        for i in range(len(coefs)):
            coefs[i] = 0.0


def make_inputs(problem_size):
    """Build in1 and in2 as in the C++ init(), clamped to available columns."""
    problem_size = max(4, problem_size)
    clamp = lambda d: min(d, problem_size - 1)
    in1_idx  = [clamp(1), clamp(4)]
    in1_coef = [1.5, 2.5]
    in2_idx  = [clamp(0), clamp(8), clamp(2)]
    in2_coef = [0.5, 1.0, 3.0]
    return in1_idx, in1_coef, in2_idx, in2_coef


def correct_fn(matrix, target_row, in1_idx, in1_coef, in2_idx, in2_coef):
    """Serial reference: accumulate in1 and in2 into the target row."""
    rows = matrix['rows']
    pos = bisect.bisect_left(rows, target_row)
    if pos >= len(rows) or rows[pos] != target_row:
        return []

    row_idx = matrix['row_indices'][pos]
    row_coefs = matrix['row_coefs'][pos]

    def accumulate(idxs, coefs):
        for col, val in zip(idxs, coefs):
            p = bisect.bisect_left(row_idx, col)
            if p < len(row_idx) and row_idx[p] == col:
                row_coefs[p] += val

    accumulate(in1_idx, in1_coef)
    accumulate(in2_idx, in2_coef)
    return list(row_coefs)


def validate(gen_fn):
    tol = 1e-12
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        matrix = make_matrix(PROBLEM_SIZE)
        in1_idx, in1_coef, in2_idx, in2_coef = make_inputs(PROBLEM_SIZE)

        # Reference
        reset_matrix(matrix)
        expected = correct_fn(matrix, 0, in1_idx, in1_coef, in2_idx, in2_coef)

        # Trial — use a fresh matrix so coefs start at 0
        matrix2 = make_matrix(PROBLEM_SIZE)
        try:
            result = gen_fn(matrix2, 0, in1_idx, in1_coef, in2_idx, in2_coef)
        except Exception:
            return False

        if len(list(result)) != len(expected):
            return False
        for a, b in zip(result, expected):
            if abs(a - b) > tol:
                return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "locking_mat_add")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return

    try:
        is_valid = validate(gen_fn)
    except Exception as _ve:
        print(f"Validation: FAIL")
        print(f"Runtime error: {_ve}", flush=True)
        charm.exit()
        return
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return

    in1_idx, in1_coef, in2_idx, in2_coef = make_inputs(PROBLEM_SIZE)

    t = 0.0
    for _ in range(opts.niter):
        matrix = make_matrix(PROBLEM_SIZE)
        t0 = time.perf_counter()
        gen_fn(matrix, 0, in1_idx, in1_coef, in2_idx, in2_coef)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        matrix = make_matrix(PROBLEM_SIZE)
        t0 = time.perf_counter()
        correct_fn(matrix, 0, in1_idx, in1_coef, in2_idx, in2_coef)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)

    charm.exit()


charm.start(main)

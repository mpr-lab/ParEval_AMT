#!/usr/bin/env python3
"""charm4py benchmark driver for 45_sparse_la_sparse_solve"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

N_BENCH = 256
N_VAL = 16
SPARSITY = 0.1
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def make_sparse_matrix(N, sparsity):
    """Generate a random sparse NxN matrix in COO format as list of dicts."""
    mat = []
    for i in range(N):
        for j in range(N):
            if random.random() < sparsity:
                mat.append({'row': i, 'column': j, 'value': random.uniform(-10.0, 10.0)})
    return mat


def correct_solve(A, b, N):
    """Gaussian elimination to solve Ax=b."""
    matrix = [[0.0] * N for _ in range(N)]
    for e in A:
        matrix[e['row']][e['column']] = e['value']
    b_copy = list(b)
    x = [0.0] * N

    for i in range(N):
        max_el = abs(matrix[i][i])
        max_row = i
        for k in range(i + 1, N):
            if abs(matrix[k][i]) > max_el:
                max_el = abs(matrix[k][i])
                max_row = k
        matrix[i], matrix[max_row] = matrix[max_row], matrix[i]
        b_copy[i], b_copy[max_row] = b_copy[max_row], b_copy[i]

        for k in range(i + 1, N):
            if matrix[i][i] == 0.0:
                continue
            c = -matrix[k][i] / matrix[i][i]
            for j in range(i, N):
                if i == j:
                    matrix[k][j] = 0.0
                else:
                    matrix[k][j] += c * matrix[i][j]
            b_copy[k] += c * b_copy[i]

    for i in range(N - 1, -1, -1):
        if matrix[i][i] == 0.0:
            x[i] = 0.0
        else:
            x[i] = b_copy[i] / matrix[i][i]
        for k in range(i - 1, -1, -1):
            b_copy[k] -= matrix[k][i] * x[i]
    return x


def make_system(N):
    """Build a random linear system Ax=b (x is known, b derived from it)."""
    A = make_sparse_matrix(N, SPARSITY)
    x_true = [random.uniform(-10.0, 10.0) for _ in range(N)]
    b = [0.0] * N
    for e in A:
        b[e['row']] += e['value'] * x_true[e['column']]
    return A, b, N


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        A, b, N = make_system(N_VAL)
        x_ref = correct_solve(A, b, N)
        x_test = gen_fn(A, list(b), N)
        if x_test is None or len(x_test) != N:
            return False
        if not all(abs(a - b_) < 1e-4 for a, b_ in zip(x_ref, x_test)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "solveLinearSystem")
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

    A, b, N = make_system(N_BENCH)
    t = 0.0
    for _ in range(opts.niter):
        b_copy = list(b)
        t0 = time.perf_counter()
        gen_fn(A, b_copy, N)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        b_copy = list(b)
        t0 = time.perf_counter()
        correct_solve(A, b_copy, N)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

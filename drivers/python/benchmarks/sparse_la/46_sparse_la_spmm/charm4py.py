#!/usr/bin/env python3
"""charm4py benchmark driver for 46_sparse_la_spmm"""
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


def make_sparse_matrix_coo(rows, cols, sparsity):
    """Generate a random sparse matrix in COO format (row x cols dimensions)."""
    mat = []
    for i in range(rows):
        for j in range(cols):
            if random.random() < sparsity:
                mat.append({'row': i, 'column': j, 'value': random.uniform(-1.0, 1.0)})
    return mat


def correct_spmm(A, X, M, K, N):
    """Compute Y = A*X where A is MxK sparse and X is KxN sparse; Y is dense MxN."""
    Y = [0.0] * (M * N)
    for a in A:
        for x in X:
            if a['column'] == x['row']:
                Y[a['row'] * N + x['column']] += a['value'] * x['value']
    return Y


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        M = K = N = N_VAL
        A = make_sparse_matrix_coo(M, K, SPARSITY)
        X = make_sparse_matrix_coo(K, N, SPARSITY)
        Y_ref = correct_spmm(A, X, M, K, N)
        Y_test = [0.0] * (M * N)
        gen_fn(A, X, Y_test, M, K, N)
        if not all(abs(a - b) < 1e-4 for a, b in zip(Y_ref, Y_test)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "spmm")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return

    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return

    M = N_BENCH
    K = N_BENCH // 4
    N = N_BENCH // 2
    A = make_sparse_matrix_coo(M, K, SPARSITY)
    X = make_sparse_matrix_coo(K, N, SPARSITY)

    t = 0.0
    for _ in range(opts.niter):
        Y = [0.0] * (M * N)
        t0 = time.perf_counter()
        gen_fn(A, X, Y, M, K, N)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        correct_spmm(A, X, M, K, N)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

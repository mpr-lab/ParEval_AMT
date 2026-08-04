#!/usr/bin/env python3
"""charm4py benchmark driver for 49_sparse_la_sparse_lu_decomp"""
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


def correct_lu_factorize(A, N):
    """LU factorization without pivoting; returns L and U as flat row-major lists."""
    full = [[0.0] * N for _ in range(N)]
    for e in A:
        full[e['row']][e['column']] = e['value']

    L = [0.0] * (N * N)
    U = [0.0] * (N * N)

    for i in range(N):
        for j in range(N):
            if j >= i:
                U[i * N + j] = full[i][j]
                for k in range(i):
                    U[i * N + j] -= L[i * N + k] * U[k * N + j]
            if i > j:
                denom = U[j * N + j]
                if denom == 0.0:
                    L[i * N + j] = 0.0
                else:
                    L[i * N + j] = full[i][j] / denom
                    for k in range(j):
                        L[i * N + j] -= L[i * N + k] * U[k * N + j] / denom
        L[i * N + i] = 1.0
    return L, U


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        N = N_VAL
        A = make_sparse_matrix(N, SPARSITY)
        L_ref, U_ref = correct_lu_factorize(A, N)
        L_test = [0.0] * (N * N)
        U_test = [0.0] * (N * N)
        gen_fn(A, L_test, U_test, N)
        if not all(abs(a - b) < 1e-4 for a, b in zip(L_ref, L_test)):
            return False
        if not all(abs(a - b) < 1e-4 for a, b in zip(U_ref, U_test)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "luFactorize")
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

    N = N_BENCH
    A = make_sparse_matrix(N, SPARSITY)

    t = 0.0
    for _ in range(opts.niter):
        L = [0.0] * (N * N)
        U = [0.0] * (N * N)
        t0 = time.perf_counter()
        gen_fn(A, L, U, N)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        correct_lu_factorize(A, N)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

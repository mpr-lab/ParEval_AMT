#!/usr/bin/env python3
"""charm4py benchmark driver for 47_sparse_la_spmv"""
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


def make_sparse_matrix(M, N, sparsity):
    """Generate a random sparse MxN matrix in COO format as list of dicts."""
    mat = []
    for i in range(M):
        for j in range(N):
            if random.random() < sparsity:
                mat.append({'row': i, 'column': j, 'value': random.uniform(-1.0, 1.0)})
    return mat


def correct_spmv(alpha, A, x, beta, y, M, N):
    """Compute y = alpha*A*x + beta*y."""
    result = [beta * yi for yi in y]
    for e in A:
        if e['row'] < M and e['column'] < N:
            result[e['row']] += alpha * e['value'] * x[e['column']]
    return result


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        M = N = N_VAL
        A = make_sparse_matrix(M, N, SPARSITY)
        x = [random.uniform(-1.0, 1.0) for _ in range(N)]
        y_init = [random.uniform(-1.0, 1.0) for _ in range(M)]
        alpha = random.uniform(-1.0, 1.0)
        beta = random.uniform(-1.0, 1.0)
        y_ref = correct_spmv(alpha, A, x, beta, y_init, M, N)
        y_test = list(y_init)
        gen_fn(alpha, A, x, beta, y_test, M, N)
        if not all(abs(a - b) < 1e-4 for a, b in zip(y_ref, y_test)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "spmv")
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

    M = N = N_BENCH
    A = make_sparse_matrix(M, N, SPARSITY)
    x = [random.uniform(-1.0, 1.0) for _ in range(N)]
    y_init = [random.uniform(-1.0, 1.0) for _ in range(M)]
    alpha = random.uniform(-1.0, 1.0)
    beta = random.uniform(-1.0, 1.0)

    t = 0.0
    for _ in range(opts.niter):
        y = list(y_init)
        t0 = time.perf_counter()
        gen_fn(alpha, A, x, beta, y, M, N)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        correct_spmv(alpha, A, x, beta, y_init, M, N)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

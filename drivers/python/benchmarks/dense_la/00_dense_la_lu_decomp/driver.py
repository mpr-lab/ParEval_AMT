#!/usr/bin/env python3
"""charm4py benchmark driver for 00_dense_la_lu_decomp"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

N_BENCH = 256
N_VAL = 16
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def rand_matrix(n):
    return [random.uniform(-10.0, 10.0) for _ in range(n * n)]


def correct_lu(A, N):
    for k in range(N):
        for i in range(k + 1, N):
            factor = A[i * N + k] / A[k * N + k]
            A[i * N + k] = factor
            for j in range(k + 1, N):
                A[i * N + j] -= factor * A[k * N + j]


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        A = rand_matrix(N_VAL)
        ref = A.copy()
        correct_lu(ref, N_VAL)
        tst = A.copy()
        gen_fn(tst, N_VAL)
        if not all(abs(a - b) < 1e-6 for a, b in zip(ref, tst)):
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
    A_base = rand_matrix(N_BENCH)
    t = 0.0
    for _ in range(opts.niter):
        A = A_base.copy(); t0 = time.perf_counter(); gen_fn(A, N_BENCH); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        A = A_base.copy(); t0 = time.perf_counter(); correct_lu(A, N_BENCH); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

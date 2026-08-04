#!/usr/bin/env python3
"""charm4py benchmark driver for 04_dense_la_gemv"""
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


def correct_gemv(A, x, y, M, N):
    for i in range(M):
        y[i] = sum(A[i * N + j] * x[j] for j in range(N))


def validate(gen_fn):
    M, N = N_VAL, N_VAL
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        A = [random.uniform(-10.0, 10.0) for _ in range(M * N)]
        x = [random.uniform(-10.0, 10.0) for _ in range(N)]
        ref = [0.0] * M
        correct_gemv(A, x, ref, M, N)
        tst = [0.0] * M
        gen_fn(A, x, tst, M, N)
        if not all(abs(a - b) < 1e-6 for a, b in zip(ref, tst)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "gemv")
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
    M, N = N_BENCH // 2, N_BENCH
    A_base = [random.uniform(-10.0, 10.0) for _ in range(M * N)]
    x_base = [random.uniform(-10.0, 10.0) for _ in range(N)]
    t = 0.0
    for _ in range(opts.niter):
        y = [0.0] * M
        t0 = time.perf_counter(); gen_fn(A_base, x_base, y, M, N); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        y = [0.0] * M
        t0 = time.perf_counter(); correct_gemv(A_base, x_base, y, M, N); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

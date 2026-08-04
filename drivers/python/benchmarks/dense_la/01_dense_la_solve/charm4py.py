#!/usr/bin/env python3
"""charm4py benchmark driver for 01_dense_la_solve"""
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


def rand_linear_system(N):
    A = [random.uniform(-10.0, 10.0) for _ in range(N * N)]
    x_true = [random.uniform(-10.0, 10.0) for _ in range(N)]
    b = [sum(A[i * N + j] * x_true[j] for j in range(N)) for i in range(N)]
    return A, b


def correct_solve(A, b, N):
    A = A.copy()
    b = b.copy()
    x = [0.0] * N
    for i in range(N - 1):
        pivot = A[i * N + i]
        if pivot == 0:
            return x
        for j in range(i + 1, N):
            factor = A[j * N + i] / pivot
            for k in range(i, N):
                A[j * N + k] -= factor * A[i * N + k]
            b[j] -= factor * b[i]
    for i in range(N - 1, -1, -1):
        s = sum(A[i * N + j] * x[j] for j in range(i + 1, N))
        x[i] = (b[i] - s) / A[i * N + i]
    return x


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        A, b = rand_linear_system(N_VAL)
        ref = correct_solve(A, b, N_VAL)
        tst = [0.0] * N_VAL
        gen_fn(A, b, tst, N_VAL)
        if not all(abs(a - b_) < 1e-6 for a, b_ in zip(ref, tst)):
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
    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return
    A_base, b_base = rand_linear_system(N_BENCH)
    t = 0.0
    for _ in range(opts.niter):
        x = [0.0] * N_BENCH
        t0 = time.perf_counter(); gen_fn(A_base, b_base, x, N_BENCH); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); correct_solve(A_base, b_base, N_BENCH); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

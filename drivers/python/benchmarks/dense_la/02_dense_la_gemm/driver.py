#!/usr/bin/env python3
"""charm4py benchmark driver for 02_dense_la_gemm"""
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


def rand_matrix(rows, cols):
    return [random.uniform(-1.0, 1.0) for _ in range(rows * cols)]


def correct_gemm(A, B, C, M, K, N):
    for i in range(M):
        for k in range(K):
            for j in range(N):
                C[i * N + j] += A[i * K + k] * B[k * N + j]


def validate(gen_fn):
    M, K, N = N_VAL, N_VAL, N_VAL
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        A = rand_matrix(M, K)
        B = rand_matrix(K, N)
        ref = [0.0] * (M * N)
        correct_gemm(A, B, ref, M, K, N)
        tst = [0.0] * (M * N)
        gen_fn(A, B, tst, M, K, N)
        if not all(abs(a - b) < 1e-6 for a, b in zip(ref, tst)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "gemm")
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
    M, K, N = N_BENCH, N_BENCH // 4, N_BENCH // 2
    A_base = rand_matrix(M, K)
    B_base = rand_matrix(K, N)
    t = 0.0
    for _ in range(opts.niter):
        C = [0.0] * (M * N)
        t0 = time.perf_counter(); gen_fn(A_base, B_base, C, M, K, N); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        C = [0.0] * (M * N)
        t0 = time.perf_counter(); correct_gemm(A_base, B_base, C, M, K, N); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

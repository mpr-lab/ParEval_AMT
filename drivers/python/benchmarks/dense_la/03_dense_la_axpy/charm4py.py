#!/usr/bin/env python3
"""charm4py benchmark driver for 03_dense_la_axpy"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

N_BENCH = 1 << 16  # 65536 elements (equivalent to 256*256)
N_VAL = 256
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def correct_axpy(alpha, x, y, z):
    for i in range(len(x)):
        z[i] = alpha * x[i] + y[i]


def validate(gen_fn):
    alpha = 2.0
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        x = [random.uniform(-1.0, 1.0) for _ in range(N_VAL)]
        y = [random.uniform(-1.0, 1.0) for _ in range(N_VAL)]
        ref = [0.0] * N_VAL
        correct_axpy(alpha, x, y, ref)
        tst = [0.0] * N_VAL
        gen_fn(alpha, x, y, tst)
        if not all(abs(a - b) < 1e-6 for a, b in zip(ref, tst)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "axpy")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return
    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return
    alpha = 2.0
    x_base = [random.uniform(-1.0, 1.0) for _ in range(N_BENCH)]
    y_base = [random.uniform(-1.0, 1.0) for _ in range(N_BENCH)]
    t = 0.0
    for _ in range(opts.niter):
        z = [0.0] * N_BENCH
        t0 = time.perf_counter(); gen_fn(alpha, x_base, y_base, z); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        z = [0.0] * N_BENCH
        t0 = time.perf_counter(); correct_axpy(alpha, x_base, y_base, z); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

#!/usr/bin/env python3
"""charm4py benchmark driver for 52_stencil_1d_jacobi_3-point_stencil"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

PROBLEM_SIZE = 1 << 20
VAL_SIZE = 1024
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def correct_fn(inp, out):
    n = len(inp)
    for i in range(n):
        s = inp[i]
        if i > 0:
            s += inp[i - 1]
        if i < n - 1:
            s += inp[i + 1]
        out[i] = s / 3.0


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        inp = [random.uniform(-100.0, 100.0) for _ in range(VAL_SIZE)]
        ref = [0.0] * VAL_SIZE
        correct_fn(inp, ref)
        tst = [0.0] * VAL_SIZE
        gen_fn(inp, tst)
        for i in range(1, VAL_SIZE - 1):
            if abs(tst[i] - ref[i]) > 1e-4:
                return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "jacobi1D")
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

    inp = [random.uniform(-100.0, 100.0) for _ in range(PROBLEM_SIZE)]
    out = [0.0] * PROBLEM_SIZE
    t = 0.0
    for _ in range(opts.niter):
        o = out.copy(); t0 = time.perf_counter(); gen_fn(inp, o); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        o = out.copy(); t0 = time.perf_counter(); correct_fn(inp, o); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

#!/usr/bin/env python3
"""charm4py benchmark driver for 33_scan_reverse_prefix_sum"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

PROBLEM_SIZE = 1 << 20
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def correct_fn(x, output):
    """Inclusive prefix sum of the reversed x into output."""
    n = len(x)
    total = 0
    for i in range(n):
        total += x[n - 1 - i]
        output[i] = total


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        x = [random.randint(-100, 100) for _ in range(1024)]
        ref = [0] * 1024
        correct_fn(x, ref)
        tst = [0] * 1024
        gen_fn(x, tst)
        if ref != tst:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "reversePrefixSum")
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
    data = [random.randint(-100, 100) for _ in range(PROBLEM_SIZE)]
    output = [0] * PROBLEM_SIZE
    t = 0.0
    for _ in range(opts.niter):
        d = data.copy(); o = output.copy()
        t0 = time.perf_counter(); gen_fn(d, o); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        d = data.copy(); o = output.copy()
        t0 = time.perf_counter(); correct_fn(d, o); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

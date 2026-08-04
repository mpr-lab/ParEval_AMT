#!/usr/bin/env python3
"""charm4py benchmark driver for 39_search_xor_contains"""
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


def correct_fn(x, y, val):
    return (val in x) ^ (val in y)


def validate(gen_fn):
    for i in range(MAX_VALIDATION_ATTEMPTS):
        x = [random.randint(-100, 100) for _ in range(1024)]
        y = [random.randint(-100, 100) for _ in range(1024)]
        val = random.randint(-100, 100)
        if i == 1:
            x[random.randint(0, len(x) - 1)] = val
            y[random.randint(0, len(y) - 1)] = val
        correct = correct_fn(x, y, val)
        test = gen_fn(x, y, val)
        if correct != test:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "xorContains")
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
    x = [random.randint(-10000, 10000) for _ in range(PROBLEM_SIZE)]
    y = [random.randint(-10000, 10000) for _ in range(PROBLEM_SIZE)]
    val = random.randint(0, 1000)
    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); gen_fn(x, y, val); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); correct_fn(x, y, val); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

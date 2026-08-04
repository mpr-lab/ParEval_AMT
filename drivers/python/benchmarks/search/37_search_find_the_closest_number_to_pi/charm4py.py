#!/usr/bin/env python3
"""charm4py benchmark driver for 37_search_find_the_closest_number_to_pi"""
import argparse
import importlib.util
import math
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


def correct_fn(x):
    return min(range(len(x)), key=lambda i: abs(x[i] - math.pi))


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        data = [random.uniform(100.0, 1000.0) for _ in range(1024)]
        data[random.randint(0, len(data) - 1)] = 10.0
        correct = correct_fn(data)
        test = gen_fn(data)
        if correct != test:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "findClosestToPi")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return
    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return
    data = [random.uniform(-10000.0, 10000.0) for _ in range(PROBLEM_SIZE)]
    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); gen_fn(data); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); correct_fn(data); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

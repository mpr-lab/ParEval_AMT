#!/usr/bin/env python3
"""charm4py benchmark driver for 38_search_find_the_first_even_number"""
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


def correct_fn(x):
    for i, v in enumerate(x):
        if v % 2 == 0:
            return i
    return len(x)


def make_data(n, force_even=True):
    x = [2 * random.randint(1, 100) + 1 for _ in range(n)]  # all odd
    if force_even:
        lo, hi = n // 4, 3 * n // 4
        x[random.randint(lo, hi - 1)] += 1
        x[random.randint(lo, hi - 1)] += 1
    return x


def validate(gen_fn):
    for i in range(MAX_VALIDATION_ATTEMPTS):
        if i == 1:
            x = [2 * random.randint(1, 50) + 1 for _ in range(1024)]
            for j in range(20):
                x[j] = 2 * random.randint(1, 50) + 1
        else:
            x = [random.randint(1, 100) for _ in range(1024)]
        correct = correct_fn(x)
        test = gen_fn(x)
        if correct != test:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "findFirstEven")
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
    data = make_data(PROBLEM_SIZE)
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

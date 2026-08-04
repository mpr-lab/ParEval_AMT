#!/usr/bin/env python3
"""charm4py benchmark driver for 40_sort_sort_an_array_of_complex_numbers_by_magnitude"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

PROBLEM_SIZE = 1 << 16
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path: str, fn_name: str):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def correct_sortComplexByMagnitude(x: list) -> None:
    x.sort(key=lambda c: abs(c))


def validate(gen_fn) -> bool:
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        data = [complex(random.uniform(-100, 100), random.uniform(-100, 100)) for _ in range(1024)]
        correct = data[:]
        test = data[:]
        correct_sortComplexByMagnitude(correct)
        gen_fn(test)
        for a, b in zip(correct, test):
            if abs(a - b) > 1e-6:
                return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "sortComplexByMagnitude")
    except Exception as e:
        print("Validation: FAIL")
        print(f"Error: {e}", flush=True)
        charm.exit()
        return

    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit()
        return

    data = [complex(random.uniform(-100, 100), random.uniform(-100, 100)) for _ in range(PROBLEM_SIZE)]

    total = 0.0
    for _ in range(opts.niter):
        d = data[:]
        t0 = time.perf_counter()
        gen_fn(d)
        total += time.perf_counter() - t0
    print(f"Time: {total / opts.niter:.6f}", flush=True)

    total_best = 0.0
    for _ in range(opts.niter):
        d = data[:]
        t0 = time.perf_counter()
        correct_sortComplexByMagnitude(d)
        total_best += time.perf_counter() - t0
    print(f"BestSequential: {total_best / opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

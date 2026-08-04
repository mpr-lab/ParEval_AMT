#!/usr/bin/env python3
"""charm4py benchmark driver for 44_sort_sort_non-zero_elements"""
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


def make_data_with_zeroes(n: int) -> list:
    result = []
    for _ in range(n):
        val = random.randint(-(2**31), 2**31 - 1)
        if random.randint(0, 4) != 0:
            val = 0
        result.append(val)
    return result


def correct_sortIgnoreZero(x: list) -> None:
    non_zero = sorted(v for v in x if v != 0)
    idx = 0
    for i in range(len(x)):
        if x[i] != 0:
            x[i] = non_zero[idx]
            idx += 1


def validate(gen_fn) -> bool:
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        data = make_data_with_zeroes(1024)
        correct = data[:]
        test = data[:]
        correct_sortIgnoreZero(correct)
        gen_fn(test)
        if correct != test:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "sortIgnoreZero")
    except Exception as e:
        print("Validation: FAIL")
        print(f"Error: {e}", flush=True)
        charm.exit()
        return

    try:
        is_valid = validate(gen_fn)
    except Exception as e:
        print(f"Validation: FAIL")
        print(f"Runtime error during validation: {e}", flush=True)
        charm.exit()
        return
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit()
        return

    data = make_data_with_zeroes(PROBLEM_SIZE)

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
        correct_sortIgnoreZero(d)
        total_best += time.perf_counter() - t0
    print(f"BestSequential: {total_best / opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

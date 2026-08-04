#!/usr/bin/env python3
"""charm4py benchmark driver for 42_sort_sorted_ranks"""
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


def correct_ranks(x: list, ranks: list) -> None:
    indices = sorted(range(len(x)), key=lambda i: x[i])
    for rank, idx in enumerate(indices):
        ranks[idx] = rank


def validate(gen_fn) -> bool:
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        x = [random.uniform(-100, 100) for _ in range(1024)]
        correct = [0] * len(x)
        test = [0] * len(x)
        correct_ranks(x, correct)
        gen_fn(x[:], test)
        if correct != test:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "ranks")
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

    data = [random.uniform(-100, 100) for _ in range(PROBLEM_SIZE)]

    total = 0.0
    for _ in range(opts.niter):
        d = data[:]
        r = [0] * PROBLEM_SIZE
        t0 = time.perf_counter()
        gen_fn(d, r)
        total += time.perf_counter() - t0
    print(f"Time: {total / opts.niter:.6f}", flush=True)

    total_best = 0.0
    for _ in range(opts.niter):
        d = data[:]
        r = [0] * PROBLEM_SIZE
        t0 = time.perf_counter()
        correct_ranks(d, r)
        total_best += time.perf_counter() - t0
    print(f"BestSequential: {total_best / opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

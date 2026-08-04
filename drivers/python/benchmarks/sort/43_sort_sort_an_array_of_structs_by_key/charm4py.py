#!/usr/bin/env python3
"""charm4py benchmark driver for 43_sort_sort_an_array_of_structs_by_key"""
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


def make_results(n: int) -> list:
    return [
        {"startTime": random.randint(0, 100), "duration": random.randint(1, 10), "value": random.uniform(-1.0, 1.0)}
        for _ in range(n)
    ]


def correct_sortByStartTime(results: list) -> None:
    results.sort(key=lambda r: r["startTime"])


def validate(gen_fn) -> bool:
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        data = make_results(1024)
        correct = [r.copy() for r in data]
        test = [r.copy() for r in data]
        correct_sortByStartTime(correct)
        gen_fn(test)
        for a, b in zip(correct, test):
            if a["startTime"] != b["startTime"] or a["duration"] != b["duration"] or a["value"] != b["value"]:
                return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "sortByStartTime")
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

    data = make_results(PROBLEM_SIZE)

    total = 0.0
    for _ in range(opts.niter):
        d = [r.copy() for r in data]
        t0 = time.perf_counter()
        gen_fn(d)
        total += time.perf_counter() - t0
    print(f"Time: {total / opts.niter:.6f}", flush=True)

    total_best = 0.0
    for _ in range(opts.niter):
        d = [r.copy() for r in data]
        t0 = time.perf_counter()
        correct_sortByStartTime(d)
        total_best += time.perf_counter() - t0
    print(f"BestSequential: {total_best / opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

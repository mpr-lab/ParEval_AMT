#!/usr/bin/env python3
"""charm4py benchmark driver for 36_search_check_if_array_contains_value"""
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


def correct_fn(x, target):
    return target in x


def validate(gen_fn):
    for i in range(MAX_VALIDATION_ATTEMPTS):
        data = [random.randint(-50, 50) for _ in range(1024)]
        if i == 1:
            target = data[random.randint(0, len(data) - 1)]
        else:
            target = random.randint(-100, 100)
        correct = correct_fn(data, target)
        test = gen_fn(data, target)
        if correct != test:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "contains")
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
    data = [random.randint(-50, 50) for _ in range(PROBLEM_SIZE)]
    target = random.randint(-100, 100)
    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); gen_fn(data, target); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); correct_fn(data, target); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

#!/usr/bin/env python3
"""charm4py benchmark driver for 59_transform_map_function"""
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


def is_power_of_two(x):
    return x > 0 and (x & (x - 1)) == 0


def correct_fn(x, mask):
    for i in range(len(x)):
        mask[i] = is_power_of_two(x[i])


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        data = [random.randint(1, 1025) for _ in range(1024)]
        ref_mask = [False] * 1024
        correct_fn(data, ref_mask)
        tst_mask = [False] * 1024
        gen_fn(data, tst_mask)
        if ref_mask != tst_mask:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "mapPowersOfTwo")
    except Exception as e:
        print("Validation: FAIL"); charm.exit(); return
    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return
    data = [random.randint(1, 1025) for _ in range(PROBLEM_SIZE)]
    t = 0.0
    for _ in range(opts.niter):
        mask = [False] * PROBLEM_SIZE
        t0 = time.perf_counter(); gen_fn(data, mask); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        mask = [False] * PROBLEM_SIZE
        t0 = time.perf_counter(); correct_fn(data, mask); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

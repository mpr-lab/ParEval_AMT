#!/usr/bin/env python3
"""charm4py benchmark driver for 57_transform_inverse_offset"""
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
    for i in range(len(x)):
        x[i] = 1.0 - 1.0 / x[i]


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        # avoid zero to prevent division by zero
        data = [random.uniform(-50.0, 50.0) for _ in range(1024)]
        data = [v if v != 0.0 else 1.0 for v in data]
        ref = data.copy()
        correct_fn(ref)
        tst = data.copy()
        gen_fn(tst)
        if not all(abs(a - b) < 1e-5 for a, b in zip(ref, tst)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "oneMinusInverse")
    except Exception as e:
        print("Validation: FAIL"); charm.exit(); return
    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return
    data = [random.uniform(-50.0, 50.0) for _ in range(PROBLEM_SIZE)]
    data = [v if v != 0.0 else 1.0 for v in data]
    t = 0.0
    for _ in range(opts.niter):
        d = data.copy(); t0 = time.perf_counter(); gen_fn(d); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        d = data.copy(); t0 = time.perf_counter(); correct_fn(d); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

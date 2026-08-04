#!/usr/bin/env python3
"""charm4py benchmark driver for 61_locking_contention_parll_hist"""
import argparse, importlib.util, random, time
from charm4py import charm

PROBLEM_SIZE = 1 << 16
NITER = 3
MAX_VALIDATION_ATTEMPTS = 2
BINS = 64


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def correct_fn(data, bins):
    if bins == 0:
        return []
    histogram = [0] * bins
    for value in data:
        b = int(value * bins)
        if b >= bins:
            b = bins - 1
        histogram[b] += 1
    return histogram


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        data = [random.random() for _ in range(1 << 14)]
        expected = correct_fn(data, BINS)
        try:
            result = gen_fn(data, BINS)
        except Exception:
            return False
        if list(result) != expected:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "parallel_histogram")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return

    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return

    data = [random.random() for _ in range(PROBLEM_SIZE)]

    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); gen_fn(data, BINS); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); correct_fn(data, BINS); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)

    charm.exit()


charm.start(main)

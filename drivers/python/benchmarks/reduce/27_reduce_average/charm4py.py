#!/usr/bin/env python3
"""charm4py benchmark driver for 27_reduce_average"""
import argparse, importlib.util, random, time
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
    return sum(x) / len(x)


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        x = [random.uniform(0.0, 100.0) for _ in range(1024)]
        expected = correct_fn(x)
        try:
            result = gen_fn(x)
        except Exception:
            return False
        if abs(expected - result) > 1e-4:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "average")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return

    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return

    data = [random.uniform(0.0, 100.0) for _ in range(PROBLEM_SIZE)]

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

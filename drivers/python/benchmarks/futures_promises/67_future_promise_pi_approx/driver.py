#!/usr/bin/env python3
"""charm4py benchmark driver for 67_future_promise_pi_approx"""
import argparse
import importlib.util
import math
import time
from charm4py import charm

NITER = 3
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 31
    return x


def sample_unit(index, seed):
    v = splitmix64(index + seed)
    return (v >> 11) * (1.0 / (1 << 53))


def monte_carlo_serial(total_samples, seed):
    hits = 0
    for i in range(total_samples):
        x = sample_unit(2 * i, seed)
        y = sample_unit(2 * i + 1, seed)
        if x * x + y * y <= 1.0:
            hits += 1
    return {"hits": hits, "samples": total_samples}


def pi_estimate(result):
    s = result["samples"] if isinstance(result, dict) else result.samples
    h = result["hits"] if isinstance(result, dict) else result.hits
    return 4.0 * h / s if s > 0 else 0.0


def validate(gen_fn):
    total_samples = 100_000
    seed = 12345
    ref = monte_carlo_serial(total_samples, seed)
    ref_pi = pi_estimate(ref)
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        try:
            result = gen_fn(total_samples, 10_000, seed)
        except Exception:
            return False
        result_pi = pi_estimate(result)
        if abs(result_pi - ref_pi) > 0.05:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "monte_carlo_parallel")
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

    total_samples = 40_000_000
    chunk_size = 250_000
    seed = 0xBADC0FFEE

    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        gen_fn(total_samples, chunk_size, seed)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        monte_carlo_serial(total_samples, seed)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

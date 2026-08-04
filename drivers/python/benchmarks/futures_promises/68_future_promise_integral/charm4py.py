#!/usr/bin/env python3
"""charm4py benchmark driver for 68_future_promise_integral"""
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


def monte_carlo_integral_serial(total_samples, a, b, seed, f):
    acc = 0.0
    for i in range(total_samples):
        u = sample_unit(i, seed)
        x = a + (b - a) * u
        acc += f(x)
    return {"accumulator": acc, "samples": total_samples}


def integral_estimate(result, a, b):
    s = result["samples"] if isinstance(result, dict) else result.samples
    acc = result["accumulator"] if isinstance(result, dict) else result.accumulator
    return (b - a) * acc / s if s > 0 else 0.0


def validate(gen_fn):
    total_samples = 50_000
    a, b = 0.0, math.pi
    seed = 42
    f = math.sin
    ref = monte_carlo_integral_serial(total_samples, a, b, seed, f)
    ref_est = integral_estimate(ref, a, b)
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        try:
            result = gen_fn(total_samples, 5_000, a, b, seed, f)
        except Exception:
            return False
        est = integral_estimate(result, a, b)
        if abs(est - ref_est) > 0.05:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "monte_carlo_integral_parallel")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return
    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return

    total_samples = 20_000_000
    chunk_size = 250_000
    a, b = 0.0, math.pi
    seed = 42
    f = math.sin

    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        gen_fn(total_samples, chunk_size, a, b, seed, f)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        monte_carlo_integral_serial(total_samples, a, b, seed, f)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

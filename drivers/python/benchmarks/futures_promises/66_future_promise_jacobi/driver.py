#!/usr/bin/env python3
"""charm4py benchmark driver for 66_future_promise_jacobi"""
import argparse
import importlib.util
import time
from charm4py import charm

NITER = 3
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def jacobi_serial(tiles, points_per_tile, iterations, left_bc, right_bc, initial, rhs):
    total = tiles * points_per_tile
    current = list(initial)
    nxt = [0.0] * total
    for _ in range(iterations):
        for i in range(total):
            left = left_bc if i == 0 else current[i - 1]
            right = right_bc if i + 1 == total else current[i + 1]
            nxt[i] = 0.5 * (left + right - rhs[i])
        current, nxt = nxt, current
    return current


def validate(gen_fn):
    tiles, pts = 2, 4
    iterations = 3
    left_bc, right_bc = 1.0, 0.0
    total = tiles * pts
    for attempt in range(MAX_VALIDATION_ATTEMPTS):
        initial = [float(attempt) * 0.1] * total
        rhs = [0.0] * total
        ref = jacobi_serial(tiles, pts, iterations, left_bc, right_bc, initial, rhs)
        try:
            result = gen_fn(tiles, pts, iterations, left_bc, right_bc, initial, rhs)
        except Exception:
            return False
        if len(result) != len(ref):
            return False
        if not all(abs(a - b) < 1e-6 for a, b in zip(ref, result)):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "jacobi_parallel")
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

    tiles, pts, iterations = 8, 1024, 100
    left_bc, right_bc = 12.0, 30.0
    total = tiles * pts
    initial = [0.0] * total
    rhs = [0.0] * total

    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        gen_fn(tiles, pts, iterations, left_bc, right_bc, initial, rhs)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        jacobi_serial(tiles, pts, iterations, left_bc, right_bc, initial, rhs)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

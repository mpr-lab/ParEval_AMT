#!/usr/bin/env python3
"""charm4py benchmark driver for 65_future_promise_heat_dist"""
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


def correct_parallel_heat(initial, np_, nx, nt, k, dt, dx):
    total = np_ * nx
    coeff = k * dt / (dx * dx)

    def heat(left, mid, right):
        return mid + coeff * (left - 2.0 * mid + right)

    U0 = list(initial)
    U1 = [0.0] * total
    for t in range(nt):
        current = U0 if t % 2 == 0 else U1
        nxt = U1 if t % 2 == 0 else U0
        for i in range(total):
            left = total - 1 if i == 0 else i - 1
            right = (i + 1) % total
            nxt[i] = heat(current[left], current[i], current[right])
    return U0 if nt % 2 == 0 else U1


def validate(gen_fn):
    np_, nx, nt = 4, 4, 3
    k, dt, dx = 0.5, 0.1, 1.0
    total = np_ * nx
    for attempt in range(MAX_VALIDATION_ATTEMPTS):
        initial = [float(attempt * total + i) for i in range(total)]
        ref = correct_parallel_heat(initial, np_, nx, nt, k, dt, dx)
        try:
            result = gen_fn(initial, np_, nx, nt, k, dt, dx)
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
        gen_fn = load_fn(opts.generated, "parallel_heat")
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

    np_, nx, nt = 32, 32, 64
    k, dt, dx = 0.5, 0.01, 1.0
    total = np_ * nx
    initial = [float(i) for i in range(total)]

    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        gen_fn(initial, np_, nx, nt, k, dt, dx)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        correct_parallel_heat(initial, np_, nx, nt, k, dt, dx)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

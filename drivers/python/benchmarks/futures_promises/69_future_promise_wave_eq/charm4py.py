#!/usr/bin/env python3
"""charm4py benchmark driver for 69_future_promise_wave_eq"""
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


def wave_serial(initial, np_, nx, nt, c, dt, dx):
    total = np_ * nx
    prev = list(initial)
    curr = list(initial)
    nxt = [0.0] * total
    coeff = (c * dt / dx) ** 2
    for _ in range(nt):
        for i in range(total):
            left = total - 1 if i == 0 else i - 1
            right = 0 if i + 1 == total else i + 1
            nxt[i] = (2.0 * curr[i] - prev[i]
                      + coeff * (curr[left] - 2.0 * curr[i] + curr[right]))
        prev, curr, nxt = curr, nxt, prev
    return curr


def validate(gen_fn):
    np_, nx, nt = 3, 4, 3
    c, dt, dx = 1.0, 0.1, 0.25
    total = np_ * nx
    for attempt in range(MAX_VALIDATION_ATTEMPTS):
        initial = [math.sin(2.0 * math.pi * i * dx + attempt * 0.1)
                   for i in range(total)]
        ref = wave_serial(initial, np_, nx, nt, c, dt, dx)
        try:
            result = gen_fn(initial, np_, nx, nt, c, dt, dx)
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
        gen_fn = load_fn(opts.generated, "wave_parallel")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return
    is_valid = validate(gen_fn)
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}", flush=True)
    if not is_valid:
        charm.exit(); return

    np_, nx, nt = 8, 32, 100
    c, dt, dx = 1.0, 0.01, 0.05
    total = np_ * nx
    initial = [math.sin(2.0 * math.pi * i * dx) for i in range(total)]

    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        gen_fn(initial, np_, nx, nt, c, dt, dx)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        wave_serial(initial, np_, nx, nt, c, dt, dx)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

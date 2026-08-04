#!/usr/bin/env python3
"""charm4py benchmark driver for 13_geometry_closest_pair_2d"""
import argparse
import importlib.util
import random
import time
import math
from charm4py import charm

PROBLEM_SIZE = 1 << 14
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def _correct_closest_pair(points):
    n = len(points)
    if n < 2:
        return 0.0
    min_dist = float('inf')
    for i in range(n - 1):
        for j in range(i + 1, n):
            d = math.sqrt((points[j]['x'] - points[i]['x'])**2 +
                          (points[j]['y'] - points[i]['y'])**2)
            if d < min_dist:
                min_dist = d
    return min_dist


def _make_points(n):
    return [{'x': random.uniform(-1000.0, 1000.0), 'y': random.uniform(-1000.0, 1000.0)}
            for _ in range(n)]


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        points = _make_points(256)
        correct = _correct_closest_pair(points)
        test = gen_fn(points)
        if abs(correct - test) > 1e-4:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "closestPair")
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
    points = _make_points(PROBLEM_SIZE)
    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        gen_fn(list(points))
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter()
        _correct_closest_pair(list(points))
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

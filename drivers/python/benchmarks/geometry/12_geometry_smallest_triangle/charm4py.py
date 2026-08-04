#!/usr/bin/env python3
"""charm4py benchmark driver for 12_geometry_smallest_triangle"""
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


def _correct_smallest_area(points):
    n = len(points)
    if n < 3:
        return 0.0
    min_area = float('inf')
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            for k in range(j + 1, n):
                a, b, c = points[i], points[j], points[k]
                area = 0.5 * abs(a['x'] * (b['y'] - c['y']) +
                                 b['x'] * (c['y'] - a['y']) +
                                 c['x'] * (a['y'] - b['y']))
                if area < min_area:
                    min_area = area
    return min_area


def _make_points(n):
    return [{'x': random.uniform(-1000.0, 1000.0), 'y': random.uniform(-1000.0, 1000.0)}
            for _ in range(n)]


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        points = _make_points(256)
        correct = _correct_smallest_area(points)
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
        gen_fn = load_fn(opts.generated, "smallestArea")
    except Exception:
        print("Validation: FAIL"); charm.exit(); return
    is_valid = validate(gen_fn)
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
        _correct_smallest_area(list(points))
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

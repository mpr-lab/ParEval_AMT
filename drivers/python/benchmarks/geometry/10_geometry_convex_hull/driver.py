#!/usr/bin/env python3
"""charm4py benchmark driver for 10_geometry_convex_hull"""
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


def _correct_convex_hull(points, hull):
    """Andrew's monotone chain convex hull. Fills hull list in-place."""
    n = len(points)
    if n < 3:
        hull[:] = list(points)
        return
    pts = sorted(points, key=lambda p: (p['x'], p['y']))

    def cross(o, a, b):
        return (b['x'] - o['x']) * (a['y'] - o['y']) - (b['y'] - o['y']) * (a['x'] - o['x'])

    upper, lower = [], []
    for p in pts:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) >= 0:
            upper.pop()
        upper.append(p)
    for p in reversed(pts):
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) >= 0:
            lower.pop()
        lower.append(p)
    result = upper[:-1] + lower[:-1]
    hull[:] = result


def _make_points(n):
    return [{'x': random.uniform(-1000.0, 1000.0), 'y': random.uniform(-1000.0, 1000.0)}
            for _ in range(n)]


def _hull_equal(a, b, tol=1e-6):
    if len(a) != len(b):
        return False
    sa = sorted(a, key=lambda p: (p['x'], p['y']))
    sb = sorted(b, key=lambda p: (p['x'], p['y']))
    return all(abs(pa['x'] - pb['x']) < tol and abs(pa['y'] - pb['y']) < tol
               for pa, pb in zip(sa, sb))


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        points = _make_points(256)
        correct = []
        _correct_convex_hull(points, correct)
        test = []
        gen_fn(list(points), test)
        if not _hull_equal(correct, test):
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "convexHull")
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
        hull = []
        t0 = time.perf_counter()
        gen_fn(list(points), hull)
        t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        hull = []
        t0 = time.perf_counter()
        _correct_convex_hull(list(points), hull)
        tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

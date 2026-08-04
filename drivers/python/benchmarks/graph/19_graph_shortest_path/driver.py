#!/usr/bin/env python3
"""charm4py benchmark driver for 19_graph_shortest_path"""
import argparse
import importlib.util
import random
import time
from charm4py import charm

N_BENCH = 1024
N_VAL = 64
NITER = 5
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def rand_connected_undirected_graph(N):
    """Generate a random connected undirected graph (adjacency matrix, row-major)."""
    A = [0] * (N * N)
    nodes = list(range(N))
    random.shuffle(nodes)
    # Ensure connectivity via a random spanning path
    for i in range(N - 1):
        u, v = nodes[i], nodes[i + 1]
        A[u * N + v] = 1
        A[v * N + u] = 1
    # Add random extra edges
    for i in range(N):
        num_extra = random.randint(0, N // 4)
        for _ in range(num_extra):
            j = random.randint(0, N - 1)
            if j != i:
                A[i * N + j] = 1
                A[j * N + i] = 1
    return A


def correct_shortest_path(A, N, source, dest):
    from collections import deque
    visited = [False] * N
    queue = deque([(source, 0)])
    visited[source] = True
    while queue:
        cur, dist = queue.popleft()
        if cur == dest:
            return dist
        for i in range(N):
            if A[cur * N + i] and not visited[i]:
                visited[i] = True
                queue.append((i, dist + 1))
    return -1


def normalize(val):
    if val is None or val < 0 or val == 2**31 - 1:
        return -1
    return val


def validate(gen_fn):
    for _ in range(MAX_VALIDATION_ATTEMPTS):
        A = rand_connected_undirected_graph(N_VAL)
        source = random.randint(0, N_VAL - 1)
        dest = random.randint(0, N_VAL - 1)
        while dest == source:
            dest = random.randint(0, N_VAL - 1)
        expected = normalize(correct_shortest_path(A, N_VAL, source, dest))
        result = normalize(gen_fn(A, N_VAL, source, dest))
        if result != expected:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])
    try:
        gen_fn = load_fn(opts.generated, "shortestPathLength")
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
    A = rand_connected_undirected_graph(N_BENCH)
    source = random.randint(0, N_BENCH - 1)
    dest = random.randint(0, N_BENCH - 1)
    while dest == source:
        dest = random.randint(0, N_BENCH - 1)
    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); gen_fn(A, N_BENCH, source, dest); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)
    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); correct_shortest_path(A, N_BENCH, source, dest); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)
    charm.exit()


charm.start(main)

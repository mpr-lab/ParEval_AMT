#!/usr/bin/env python3
"""charm4py benchmark driver for 62_locking_contention_bfs"""
import argparse, importlib.util, random, time
from collections import deque
from charm4py import charm

PROBLEM_SIZE = 512
NITER = 3
MAX_VALIDATION_ATTEMPTS = 2


def load_fn(path, fn_name):
    spec = importlib.util.spec_from_file_location("generated", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def build_grid_graph(rows, cols):
    """Build undirected grid graph as adjacency list (dict node -> list of neighbors)."""
    graph = {i: [] for i in range(rows * cols)}
    for r in range(rows):
        for c in range(cols):
            u = r * cols + c
            if c + 1 < cols:
                v = r * cols + (c + 1)
                graph[u].append(v)
                graph[v].append(u)
            if r + 1 < rows:
                v = (r + 1) * cols + c
                graph[u].append(v)
                graph[v].append(u)
    return graph


def correct_fn(graph, source):
    """BFS returning list of level sizes."""
    n = len(graph)
    if source not in graph:
        return []
    visited = set()
    visited.add(source)
    frontier = deque([source])
    level_sizes = []
    while frontier:
        level_count = len(frontier)
        level_sizes.append(level_count)
        for _ in range(level_count):
            u = frontier.popleft()
            for v in graph[u]:
                if v not in visited:
                    visited.add(v)
                    frontier.append(v)
    return level_sizes


def validate(gen_fn):
    for attempt in range(MAX_VALIDATION_ATTEMPTS):
        dim = 256 + attempt * 2
        graph = build_grid_graph(dim, dim)
        source = (attempt * 7) % (dim * dim)
        expected = correct_fn(graph, source)
        try:
            result = gen_fn(graph, source)
        except Exception:
            return False
        if list(result) != expected:
            return False
    return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True)
    parser.add_argument("--niter", type=int, default=NITER)
    opts = parser.parse_args(args[1:])

    try:
        gen_fn = load_fn(opts.generated, "bfs_next_level_counts")
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

    import math
    dim = max(4, int(math.sqrt(PROBLEM_SIZE)))
    graph = build_grid_graph(dim, dim)
    source = 0

    t = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); gen_fn(graph, source); t += time.perf_counter() - t0
    print(f"Time: {t/opts.niter:.6f}", flush=True)

    tb = 0.0
    for _ in range(opts.niter):
        t0 = time.perf_counter(); correct_fn(graph, source); tb += time.perf_counter() - t0
    print(f"BestSequential: {tb/opts.niter:.6f}", flush=True)

    charm.exit()


charm.start(main)

use Time, Random, Math;
config const problemSize: int = 1 << 18;
const NITER = 5;

proc correctShortestPathLength(A: [] int, N: int, source: int, dest: int): int {
  var dist: [0..<N] int = -1;
  var queue: [0..<N] int;
  var qHead = 0; var qTail = 0;
  dist[source] = 0; queue[qTail] = source; qTail += 1;
  while qHead < qTail {
    var v = queue[qHead]; qHead += 1;
    if v == dest then return dist[v];
    for u in 0..<N {
      if A[v*N+u] == 1 && dist[u] == -1 {
        dist[u] = dist[v] + 1; queue[qTail] = u; qTail += 1;
      }
    }
  }
  return dist[dest];
}

proc makeConnectedGraph(ref A: [] int, N: int, rs: randomStream(int)) {
  A = 0;
  for i in 0..<N-1 { A[i*N+(i+1)] = 1; A[(i+1)*N+i] = 1; }
  for i in 0..<N { for j in i+2..<N { if rs.next() % 4 == 0 { A[i*N+j] = 1; A[j*N+i] = 1; } } }
}

proc doValidate(): bool {
  const testN = 64;
  for trial in 0..1 {
    var A: [0..<testN*testN] int;
    var rs = new randomStream(int, seed=trial+1);
    makeConnectedGraph(A, testN, rs);
    const src = 0; const dst = testN/2;
    if correctShortestPathLength(A, testN, src, dst) != shortestPathLength(A, testN, src, dst) then return false;
  }
  return true;
}

proc main() {
  const N = (sqrt(problemSize:real)):int;
  var A: [0..<N*N] int;
  var rs = new randomStream(int, seed=42);
  makeConnectedGraph(A, N, rs);
  const src = 0; const dst = N/2;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = shortestPathLength(A, N, src, dst); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctShortestPathLength(A, N, src, dst); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

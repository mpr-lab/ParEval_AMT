use Time, Random, Math;
config const problemSize: int = 1 << 18;
const NITER = 5;

proc correctLargestComponent(A: [] int, N: int): int {
  var visited: [0..<N] bool = false;
  var queue: [0..<N] int;
  var maxSize = 0;
  for start in 0..<N {
    if !visited[start] {
      var qHead = 0; var qTail = 0;
      queue[qTail] = start; qTail += 1; visited[start] = true;
      var size = 0;
      while qHead < qTail {
        var v = queue[qHead]; qHead += 1; size += 1;
        for u in 0..<N { if A[v*N+u] == 1 && !visited[u] { visited[u] = true; queue[qTail] = u; qTail += 1; } }
      }
      if size > maxSize then maxSize = size;
    }
  }
  return maxSize;
}

proc makeGraph(ref A: [] int, N: int, rs: randomStream(int)) {
  A = 0;
  for i in 0..<N { for j in i+1..<N { if rs.rand() % 3 == 0 { A[i*N+j] = 1; A[j*N+i] = 1; } } }
}

proc doValidate(): bool {
  const testN = 64;
  for trial in 0..1 {
    var A: [0..<testN*testN] int;
    var rs = new randomStream(int, seed=trial+1);
    makeGraph(A, testN, rs);
    if correctLargestComponent(A, testN) != largestComponent(A, testN) then return false;
  }
  return true;
}

proc main() {
  const N = (sqrt(problemSize:real)):int;
  var A: [0..<N*N] int;
  var rs = new randomStream(int, seed=42);
  makeGraph(A, N, rs);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = largestComponent(A, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctLargestComponent(A, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

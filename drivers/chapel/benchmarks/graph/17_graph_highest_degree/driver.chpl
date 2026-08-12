use Time, Random, Math;
config const problemSize: int = 1 << 18;
const NITER = 5;

proc correctMaxDegree(A: [] int, N: int): int {
  var maxDeg = 0;
  for i in 0..<N { var deg = 0; for j in 0..<N { deg += A[i*N+j]; } if deg > maxDeg then maxDeg = deg; }
  return maxDeg;
}

proc makeGraph(ref A: [] int, N: int, rs: randomStream(int)) {
  A = 0;
  for i in 0..<N { for j in i+1..<N { if rs.next() % 3 == 0 { A[i*N+j] = 1; A[j*N+i] = 1; } } }
}

proc doValidate(): bool {
  const testN = 64;
  for trial in 0..1 {
    var A: [0..<testN*testN] int;
    var rs = new randomStream(int, seed=trial+1);
    makeGraph(A, testN, rs);
    if correctMaxDegree(A, testN) != maxDegree(A, testN) then return false;
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
  for it in 0..<NITER { sw.restart(); var r = maxDegree(A, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctMaxDegree(A, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

use Time, Random, Math;
config const problemSize: int = 1 << 18;
const NITER = 5;

proc correctGemm(A: [] real, B: [] real, ref C: [] real, M: int, K: int, N: int) {
  for i in 0..<M {
    for j in 0..<N {
      var s = 0.0;
      for k in 0..<K { s += A[i*K+k] * B[k*N+j]; }
      C[i*N+j] = s;
    }
  }
}

proc doValidate(): bool {
  const testN = 32;
  for trial in 0..1 {
    var A: [0..<testN*testN] real;
    var B: [0..<testN*testN] real;
    var Cref: [0..<testN*testN] real = 0.0;
    var Cgen: [0..<testN*testN] real = 0.0;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(A); rs.fill(B);
    correctGemm(A, B, Cref, testN, testN, testN);
    gemm(A, B, Cgen, testN, testN, testN);
    for i in 0..<testN*testN { if abs(Cref[i] - Cgen[i]) > 1e-9 then return false; }
  }
  return true;
}

proc main() {
  const N = (sqrt(problemSize:real)):int;
  var A: [0..<N*N] real;
  var B: [0..<N*N] real;
  var C: [0..<N*N] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(A); rs.fill(B);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { C = 0.0; sw.restart(); gemm(A, B, C, N, N, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { C = 0.0; sw.restart(); correctGemm(A, B, C, N, N, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

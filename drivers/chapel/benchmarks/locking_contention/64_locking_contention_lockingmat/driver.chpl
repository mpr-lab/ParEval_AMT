use Time, Random;
config const problemSize: int = 1 << 9;
const NITER = 5;

proc correctLockingMatMul(A: [] real, B: [] real, ref C: [] real, N: int) {
  C = 0.0;
  for i in 0..<N do for k in 0..<N do for j in 0..<N do C[i*N+j] += A[i*N+k] * B[k*N+j];
}

proc doValidate(): bool {
  const n = 32;
  for trial in 0..1 {
    var A, B: [0..<n*n] real; var rs = new randomStream(real, seed=trial+1); rs.fill(A); rs.fill(B);
    var Cc, Ct: [0..<n*n] real;
    correctLockingMatMul(A, B, Cc, n); lockingMatMul(A, B, Ct, n);
    for i in Cc.domain do if abs(Cc[i]-Ct[i]) > 1e-8 then return false;
  }
  return true;
}

proc main() {
  const N = problemSize; var A, B, C: [0..<N*N] real;
  var rs = new randomStream(real, seed=42); rs.fill(A); rs.fill(B);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch; var computeTotal = 0.0;
  for i in 0..<NITER { C = 0.0; sw.restart(); lockingMatMul(A, B, C, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);
  var bestTotal = 0.0;
  for i in 0..<NITER { C = 0.0; sw.restart(); correctLockingMatMul(A, B, C, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

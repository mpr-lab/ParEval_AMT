use Time, Random, Math;
config const problemSize: int = 1 << 18;
const NITER = 5;

proc correctLuFactorize(ref A: [] real, N: int) {
  for k in 0..<N {
    for i in k+1..<N {
      A[i*N+k] /= A[k*N+k];
      for j in k+1..<N { A[i*N+j] -= A[i*N+k] * A[k*N+j]; }
    }
  }
}

proc doValidate(): bool {
  const testN = 32;
  for trial in 0..1 {
    var A: [0..<testN*testN] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(A);
    for i in 0..<testN { A[i*testN+i] += testN:real; }
    var Aref = A; var Agen = A;
    correctLuFactorize(Aref, testN);
    luFactorize(Agen, testN);
    for idx in 0..<testN*testN { if abs(Aref[idx] - Agen[idx]) > 1e-9 then return false; }
  }
  return true;
}

proc main() {
  const N = (sqrt(problemSize:real)):int;
  var A: [0..<N*N] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(A);
  for i in 0..<N { A[i*N+i] += N:real; }
  const Aorig = A;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { A = Aorig; sw.restart(); luFactorize(A, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { A = Aorig; sw.restart(); correctLuFactorize(A, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

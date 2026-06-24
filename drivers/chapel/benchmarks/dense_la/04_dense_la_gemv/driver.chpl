use Time, Random, Math;
config const problemSize: int = 1 << 18;
const NITER = 5;

proc correctGemv(A: [] real, x: [] real, ref y: [] real, M: int, N: int) {
  for i in 0..<M {
    var s = 0.0;
    for j in 0..<N { s += A[i*N+j] * x[j]; }
    y[i] = s;
  }
}

proc doValidate(): bool {
  const testN = 128;
  for trial in 0..1 {
    var A: [0..<testN*testN] real; var x: [0..<testN] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(A); rs.fill(x);
    var yref: [0..<testN] real = 0.0; var ygen: [0..<testN] real = 0.0;
    correctGemv(A, x, yref, testN, testN);
    gemv(A, x, ygen, testN, testN);
    for i in 0..<testN { if abs(yref[i] - ygen[i]) > 1e-9 then return false; }
  }
  return true;
}

proc main() {
  const N = (sqrt(problemSize:real)):int;
  var A: [0..<N*N] real; var x: [0..<N] real; var y: [0..<N] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(A); rs.fill(x);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { y = 0.0; sw.restart(); gemv(A, x, y, N, N); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { y = 0.0; sw.restart(); correctGemv(A, x, y, N, N); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

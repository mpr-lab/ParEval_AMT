use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctAxpy(alpha: real, x: [] real, y: [] real, ref z: [] real) {
  for i in z.domain { z[i] = alpha * x[i] + y[i]; }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var xv: [0..<n] real; var yv: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(xv); rs.fill(yv);
    const alpha = 2.5;
    var zref: [0..<n] real = 0.0; var zgen: [0..<n] real = 0.0;
    correctAxpy(alpha, xv, yv, zref);
    axpy(alpha, xv, yv, zgen);
    for i in 0..<n { if abs(zref[i] - zgen[i]) > 1e-12 then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var xv: [0..<n] real; var yv: [0..<n] real; var z: [0..<n] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(xv); rs.fill(yv);
  const alpha = 2.5;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { z = 0.0; sw.restart(); axpy(alpha, xv, yv, z); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { z = 0.0; sw.restart(); correctAxpy(alpha, xv, yv, z); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

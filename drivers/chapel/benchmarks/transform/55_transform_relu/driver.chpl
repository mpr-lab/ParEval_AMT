use Time, Random;
config const problemSize: int = 1 << 21;
const NITER = 5;

proc correctRelu(ref x: [] real) {
  for i in x.domain do if x[i] < 0.0 then x[i] = 0.0;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var a: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(a);
    for i in a.domain do a[i] = a[i] * 200.0 - 100.0;
    var b = a;
    correctRelu(b);
    relu(a);
    for i in a.domain do if abs(a[i] - b[i]) > 1e-12 then return false;
  }
  return true;
}

proc main() {
  var x: [0..<problemSize] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(x);
  for i in x.domain do x[i] = x[i] * 200.0 - 100.0;
  const orig = x;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER {
    x = orig;
    sw.restart(); relu(x); sw.stop();
    computeTotal += sw.elapsed();
  }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER {
    x = orig;
    sw.restart(); correctRelu(x); sw.stop();
    bestTotal += sw.elapsed();
  }
  writeln("BestSequential: ", bestTotal / NITER);
}

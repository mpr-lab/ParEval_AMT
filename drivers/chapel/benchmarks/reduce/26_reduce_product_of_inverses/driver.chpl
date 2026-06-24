use Time, Random;
config const problemSize: int = 1 << 23;
const NITER = 5;

proc correctProductWithInverses(x: [] real): real {
  var r = 1.0;
  for v in x do r *= 1.0 / v;
  return r;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var a: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(a);
    for i in a.domain do a[i] = a[i] * 8.0 + 1.0;
    const correct = correctProductWithInverses(a);
    const test    = productWithInverses(a);
    if abs(correct - test) > abs(correct) * 1e-6 + 1e-12 then return false;
  }
  return true;
}

proc main() {
  var x: [0..<problemSize] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(x);
  for i in x.domain do x[i] = x[i] * 8.0 + 1.0;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = productWithInverses(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = correctProductWithInverses(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

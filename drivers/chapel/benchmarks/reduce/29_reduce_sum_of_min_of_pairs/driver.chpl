use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctSumOfMinimumElements(x: [] real, y: [] real): real {
  var r = 0.0;
  for i in x.domain do r += min(x[i], y[i]);
  return r;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var a, b: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(a); rs.fill(b);
    for i in a.domain { a[i] = a[i]*200-100; b[i] = b[i]*200-100; }
    const correct = correctSumOfMinimumElements(a, b);
    const test    = sumOfMinimumElements(a, b);
    if abs(correct - test) > abs(correct) * 1e-6 + 1e-10 then return false;
  }
  return true;
}

proc main() {
  var x, y: [0..<problemSize] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(x); rs.fill(y);
  for i in x.domain { x[i] = x[i]*200-100; y[i] = y[i]*200-100; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = sumOfMinimumElements(x, y); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = correctSumOfMinimumElements(x, y); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

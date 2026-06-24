use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctAverage(x: [] real): real {
  return (+ reduce x) / x.size;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var a: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1);
    rs.fill(a);
    for i in a.domain do a[i] = a[i] * 200.0 - 100.0;
    if abs(correctAverage(a) - average(a)) > 1e-6 then return false;
  }
  return true;
}

proc main() {
  var x: [0..<problemSize] real;
  var rs = new randomStream(real, seed=42);
  rs.fill(x);
  for i in x.domain do x[i] = x[i] * 200.0 - 100.0;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = average(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = correctAverage(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

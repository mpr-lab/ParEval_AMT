use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctSumOfPrefixSum(x: [] real): real {
  var ps = 0.0; var total = 0.0;
  for v in x { ps += v; total += ps; }
  return total;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1); rs.fill(x);
    if abs(correctSumOfPrefixSum(x) - sumOfPrefixSum(x)) > 1e-6 then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] real;
  var rs = new randomStream(real, seed=42); rs.fill(x);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = sumOfPrefixSum(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctSumOfPrefixSum(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

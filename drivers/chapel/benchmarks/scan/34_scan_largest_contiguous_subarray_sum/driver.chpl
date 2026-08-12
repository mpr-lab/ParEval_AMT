use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctMaximumSubarray(x: [] int): int {
  var maxSum = x[0]; var curSum = x[0];
  for i in 1..<x.size {
    if curSum + x[i] > x[i] then curSum += x[i]; else curSum = x[i];
    if curSum > maxSum then maxSum = curSum;
  }
  return maxSum;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    for i in x.domain { x[i] = (rs.rand() % 201) - 100; }
    if correctMaximumSubarray(x) != maximumSubarray(x) then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] int;
  var rs = new randomStream(int, seed=42);
  for i in x.domain { x[i] = (rs.rand() % 201) - 100; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = maximumSubarray(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctMaximumSubarray(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

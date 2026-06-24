use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctPrefixSum(x: [] real, ref output: [] real) {
  output[0] = x[0];
  for i in 1..<x.size { output[i] = output[i-1] + x[i]; }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] real; var oref: [0..<n] real; var ogen: [0..<n] real;
    var rs = new randomStream(real, seed=trial+1); rs.fill(x);
    correctPrefixSum(x, oref); prefixSum(x, ogen);
    for i in 0..<n { if abs(oref[i] - ogen[i]) > 1e-9 then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] real; var output: [0..<n] real;
  var rs = new randomStream(real, seed=42); rs.fill(x);

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); prefixSum(x, output); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); correctPrefixSum(x, output); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

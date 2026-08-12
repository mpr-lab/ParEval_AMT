use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctReversePrefixSum(x: [] int, ref output: [] int) {
  const n = x.size;
  output[n-1] = x[n-1];
  for i in 1..<n { output[n-1-i] = output[n-i] + x[n-1-i]; }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] int; var oref: [0..<n] int; var ogen: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    for i in x.domain { x[i] = rs.next() % 100; }
    correctReversePrefixSum(x, oref); reversePrefixSum(x, ogen);
    for i in 0..<n { if oref[i] != ogen[i] then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] int; var output: [0..<n] int;
  var rs = new randomStream(int, seed=42);
  for i in x.domain { x[i] = rs.next() % 100; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); reversePrefixSum(x, output); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); correctReversePrefixSum(x, output); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

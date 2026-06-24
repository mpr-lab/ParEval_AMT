use Time, Random;
config const problemSize: int = 1 << 22;
const NITER = 5;

proc correctParallelHistogram(data: [] int, ref bins: [] int) {
  bins = 0;
  for v in data do bins[v % 256] += 1;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var d: [0..<n] int; var rs = new randomStream(int, seed=trial+1); rs.fill(d);
    for i in d.domain do d[i] = ((d[i] % 256) + 256) % 256;
    var bc, bt: [0..<256] int;
    correctParallelHistogram(d, bc); parallelHistogram(d, bt);
    for i in bc.domain do if bc[i] != bt[i] then return false;
  }
  return true;
}

proc main() {
  var data: [0..<problemSize] int; var rs = new randomStream(int, seed=42); rs.fill(data);
  for i in data.domain do data[i] = ((data[i] % 256) + 256) % 256;
  var bins: [0..<256] int;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch; var computeTotal = 0.0;
  for i in 0..<NITER { bins = 0; sw.restart(); parallelHistogram(data, bins); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);
  var bestTotal = 0.0;
  for i in 0..<NITER { bins = 0; sw.restart(); correctParallelHistogram(data, bins); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

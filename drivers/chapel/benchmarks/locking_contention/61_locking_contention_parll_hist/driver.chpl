use Time, Random;
config const problemSize: int = 1 << 22;
const NITER = 5;

proc correctParallelHistogramBytes(data: [] uint(8), ref bins: [] int) {
  bins = 0;
  for v in data do bins[v:int] += 1;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var d: [0..<n] uint(8); var rs = new randomStream(int, seed=trial+1);
    for i in d.domain do d[i] = (abs(rs.getNext()) % 256):uint(8);
    var bc, bt: [0..<256] int;
    correctParallelHistogramBytes(d, bc); parallelHistogramBytes(d, bt);
    for i in bc.domain do if bc[i] != bt[i] then return false;
  }
  return true;
}

proc main() {
  var data: [0..<problemSize] uint(8); var rs = new randomStream(int, seed=42);
  for i in data.domain do data[i] = (abs(rs.getNext()) % 256):uint(8);
  var bins: [0..<256] int;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch; var computeTotal = 0.0;
  for i in 0..<NITER { bins = 0; sw.restart(); parallelHistogramBytes(data, bins); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);
  var bestTotal = 0.0;
  for i in 0..<NITER { bins = 0; sw.restart(); correctParallelHistogramBytes(data, bins); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

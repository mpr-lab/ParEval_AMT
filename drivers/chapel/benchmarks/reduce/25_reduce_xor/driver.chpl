use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctReduceLogicalXOR(x: [] bool): bool {
  var r = false;
  for v in x do r = r ^ v;
  return r;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var a: [0..<n] bool;
    var rs = new randomStream(int, seed=trial+1);
    for i in a.domain do a[i] = (rs.next() % 2) == 1;
    if correctReduceLogicalXOR(a) != reduceLogicalXOR(a) then return false;
  }
  return true;
}

proc main() {
  var x: [0..<problemSize] bool;
  var rs = new randomStream(int, seed=42);
  for i in x.domain do x[i] = (rs.next() % 2) == 1;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = reduceLogicalXOR(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for i in 0..<NITER { sw.restart(); var r = correctReduceLogicalXOR(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

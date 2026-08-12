use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctContains(x: [] int, target: int): bool {
  for v in x { if v == target then return true; }
  return false;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    for i in x.domain { x[i] = rs.next() % 1000; }
    const target = 42;
    if correctContains(x, target) != contains(x, target) then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] int;
  var rs = new randomStream(int, seed=42);
  for i in x.domain { x[i] = rs.next() % 1000; }
  const target = 42;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = contains(x, target); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctContains(x, target); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctFindFirstEven(x: [] int): int {
  for i in x.domain { if x[i] % 2 == 0 then return i; }
  return -1;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    for i in x.domain { x[i] = rs.getNext() % 1000; }
    if correctFindFirstEven(x) != findFirstEven(x) then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] int;
  var rs = new randomStream(int, seed=42);
  for i in x.domain { x[i] = rs.getNext() % 1000; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = findFirstEven(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctFindFirstEven(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

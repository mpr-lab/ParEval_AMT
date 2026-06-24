use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

proc correctXorContains(x: [] int, y: [] int, val: int): bool {
  var inX = false; for v in x { if v == val then inX = true; }
  var inY = false; for v in y { if v == val then inY = true; }
  return inX ^ inY;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] int; var y: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    for i in x.domain { x[i] = rs.getNext() % 100; }
    for i in y.domain { y[i] = rs.getNext() % 100; }
    const val = 42;
    if correctXorContains(x, y, val) != xorContains(x, y, val) then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] int; var y: [0..<n] int;
  var rs = new randomStream(int, seed=42);
  for i in x.domain { x[i] = rs.getNext() % 100; }
  for i in y.domain { y[i] = rs.getNext() % 100; }
  const val = 42;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = xorContains(x, y, val); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctXorContains(x, y, val); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

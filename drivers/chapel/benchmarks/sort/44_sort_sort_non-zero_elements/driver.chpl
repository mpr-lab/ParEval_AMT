use Time, Random, Sort;
config const problemSize: int = 1 << 22;
const NITER = 5;

proc correctSortIgnoreZero(ref x: [] int) {
  const n = x.size;
  var count = 0;
  for v in x { if v != 0 then count += 1; }
  var nz: [0..<count] int;
  var idx = 0;
  for v in x { if v != 0 { nz[idx] = v; idx += 1; } }
  sort(nz);
  idx = 0;
  for i in x.domain { if x[i] != 0 { x[i] = nz[idx]; idx += 1; } }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] int;
    var rs = new randomStream(int, seed=trial+1);
    for i in x.domain { var v = rs.getNext() % 201 - 100; x[i] = if v == 0 then 1 else v; }
    for i in 0..<n/5 { x[i*5] = 0; }
    var xref = x; var xgen = x;
    correctSortIgnoreZero(xref); sortIgnoreZero(xgen);
    for i in 0..<n { if xref[i] != xgen[i] then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] int;
  var rs = new randomStream(int, seed=42);
  for i in x.domain { var v = rs.getNext() % 201 - 100; x[i] = if v == 0 then 1 else v; }
  for i in 0..<n/5 { x[i*5] = 0; }
  const orig = x;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { x = orig; sw.restart(); sortIgnoreZero(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { x = orig; sw.restart(); correctSortIgnoreZero(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

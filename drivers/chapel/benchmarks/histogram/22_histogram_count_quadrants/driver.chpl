use Time, Random;
config const problemSize: int = 1 << 24;
const NITER = 5;

record Point { var x, y: real; }

proc correctCountQuadrants(points: [] Point, ref bins: [] int) {
  for p in points {
    var q = (if p.x >= 0.0 then 1 else 0) + (if p.y >= 0.0 then 2 else 0);
    bins[q] += 1;
  }
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var pts: [0..<n] Point;
    var rs = new randomStream(real, seed=trial+1);
    for i in 0..<n { pts[i].x = rs.rand() * 2.0 - 1.0; pts[i].y = rs.rand() * 2.0 - 1.0; }
    var bref: [0..<4] int = 0; var bgen: [0..<4] int = 0;
    correctCountQuadrants(pts, bref); countQuadrants(pts, bgen);
    for i in 0..<4 { if bref[i] != bgen[i] then return false; }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var pts: [0..<n] Point; var bins: [0..<4] int = 0;
  var rs = new randomStream(real, seed=42);
  for i in 0..<n { pts[i].x = rs.rand() * 2.0 - 1.0; pts[i].y = rs.rand() * 2.0 - 1.0; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { bins = 0; sw.restart(); countQuadrants(pts, bins); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { bins = 0; sw.restart(); correctCountQuadrants(pts, bins); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

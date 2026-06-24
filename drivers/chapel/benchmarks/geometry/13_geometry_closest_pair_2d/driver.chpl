use Time, Random, Math;
config const problemSize: int = 1 << 12;
const NITER = 5;

record Point { var x, y: real; }

proc correctClosestPair(points: [] Point): real {
  const n = points.size;
  var minD = max(real);
  for i in 0..<n {
    for j in i+1..<n {
      var dx = points[i].x - points[j].x; var dy = points[i].y - points[j].y;
      var d = sqrt(dx*dx + dy*dy);
      if d < minD then minD = d;
    }
  }
  return minD;
}

proc doValidate(): bool {
  const testN = 256;
  for trial in 0..1 {
    var pts: [0..<testN] Point;
    var rs = new randomStream(real, seed=trial+1);
    for i in 0..<testN { pts[i].x = rs.getNext(); pts[i].y = rs.getNext(); }
    if abs(correctClosestPair(pts) - closestPair(pts)) > 1e-12 then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var pts: [0..<n] Point;
  var rs = new randomStream(real, seed=42);
  for i in 0..<n { pts[i].x = rs.getNext(); pts[i].y = rs.getNext(); }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = closestPair(pts); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctClosestPair(pts); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

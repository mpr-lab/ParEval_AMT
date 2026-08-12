use Time, Random, Math;
config const problemSize: int = 1 << 14;
const NITER = 5;

record Point { var x, y: real; }

proc correctConvexHullPerimeter(points: [] Point): real {
  const n = points.size;
  if n < 3 then return 0.0;
  var hull: [0..<n] Point;
  for i in hull.domain { hull[i].x = 0.0; hull[i].y = 0.0; }
  var l = 0;
  for i in 1..<n { if points[i].x < points[l].x then l = i; }
  var p = l; var hullSize = 0;
  do {
    hull[hullSize] = points[p]; hullSize += 1;
    var q = (p + 1) % n;
    for i in 0..<n {
      var cross = (points[i].x - points[p].x) * (points[q].y - points[p].y) -
                  (points[i].y - points[p].y) * (points[q].x - points[p].x);
      if cross < 0.0 then q = i;
    }
    p = q;
  } while p != l && hullSize < n;
  var perim = 0.0;
  for i in 0..<hullSize {
    var j = (i+1) % hullSize;
    var dx = hull[j].x - hull[i].x; var dy = hull[j].y - hull[i].y;
    perim += sqrt(dx*dx + dy*dy);
  }
  return perim;
}

proc doValidate(): bool {
  const testN = 128;
  for trial in 0..1 {
    var pts: [0..<testN] Point;
    var rs = new randomStream(real, seed=trial+1);
    for i in 0..<testN { pts[i].x = rs.next(); pts[i].y = rs.next(); }
    if abs(correctConvexHullPerimeter(pts) - convexHullPerimeter(pts)) > 1e-9 then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var pts: [0..<n] Point;
  var rs = new randomStream(real, seed=42);
  for i in 0..<n { pts[i].x = rs.next(); pts[i].y = rs.next(); }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = convexHullPerimeter(pts); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctConvexHullPerimeter(pts); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

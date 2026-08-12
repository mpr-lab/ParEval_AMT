use Time, Random, Math;
config const problemSize: int = 1 << 14;
const NITER = 5;

record Point { var x, y: real; }

proc jarvis(points: [] Point, ref hull: [] Point) {
  const n = points.size;
  for i in hull.domain { hull[i].x = 0.0; hull[i].y = 0.0; }
  if n < 3 then return;
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
}

proc hullPerim(hull: [] Point): real {
  var k = 0;
  while k < hull.size && (hull[k].x != 0.0 || hull[k].y != 0.0) { k += 1; }
  if k < 2 then return 0.0;
  var p = 0.0;
  for idx in 0..<k {
    var nx = (idx+1) % k;
    var dx = hull[nx].x - hull[idx].x; var dy = hull[nx].y - hull[idx].y;
    p += sqrt(dx*dx + dy*dy);
  }
  return p;
}

proc doValidate(): bool {
  const testN = 128;
  for trial in 0..1 {
    var pts: [0..<testN] Point;
    var rs = new randomStream(real, seed=trial+1);
    for i in 0..<testN { pts[i].x = rs.rand() + 0.1; pts[i].y = rs.rand() + 0.1; }
    var hullRef: [0..<testN] Point; var hullGen: [0..<testN] Point;
    jarvis(pts, hullRef); convexHull(pts, hullGen);
    if abs(hullPerim(hullRef) - hullPerim(hullGen)) > 1e-9 then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var pts: [0..<n] Point;
  var rs = new randomStream(real, seed=42);
  for i in 0..<n { pts[i].x = rs.rand(); pts[i].y = rs.rand(); }
  var hull: [0..<n] Point;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER {
    for i in hull.domain { hull[i].x = 0.0; hull[i].y = 0.0; }
    sw.restart(); convexHull(pts, hull); sw.stop(); computeTotal += sw.elapsed();
  }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER {
    for i in hull.domain { hull[i].x = 0.0; hull[i].y = 0.0; }
    sw.restart(); jarvis(pts, hull); sw.stop(); bestTotal += sw.elapsed();
  }
  writeln("BestSequential: ", bestTotal / NITER);
}

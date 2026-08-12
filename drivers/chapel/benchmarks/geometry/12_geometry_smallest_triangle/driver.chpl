use Time, Random, Math;
config const problemSize: int = 512;
const NITER = 5;

record Point { var x, y: real; }

proc correctSmallestArea(points: [] Point): real {
  const n = points.size;
  var minA = max(real);
  for i in 0..<n {
    for j in i+1..<n {
      for k in j+1..<n {
        var area = abs((points[j].x - points[i].x) * (points[k].y - points[i].y) -
                       (points[k].x - points[i].x) * (points[j].y - points[i].y)) / 2.0;
        if area > 0.0 && area < minA then minA = area;
      }
    }
  }
  return minA;
}

proc doValidate(): bool {
  const testN = 32;
  for trial in 0..1 {
    var pts: [0..<testN] Point;
    var rs = new randomStream(real, seed=trial+1);
    for i in 0..<testN { pts[i].x = rs.next(); pts[i].y = rs.next(); }
    if abs(correctSmallestArea(pts) - smallestArea(pts)) > 1e-9 then return false;
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
  for it in 0..<NITER { sw.restart(); var r = smallestArea(pts); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctSmallestArea(pts); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

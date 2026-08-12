use Time, Random, Math;
config const problemSize: int = 1 << 14;
const NITER = 5;

proc correctIfft(ref x: [] complex(128)) {
  const n = x.size;
  var out: [0..<n] complex(128);
  for k in 0..<n {
    var re_s = 0.0; var im_s = 0.0;
    for j in 0..<n {
      var angle = 2.0 * Math.PI * k * j / n:real;
      re_s += x[j].re * cos(angle) - x[j].im * sin(angle);
      im_s += x[j].re * sin(angle) + x[j].im * cos(angle);
    }
    out[k].re = re_s / n:real; out[k].im = im_s / n:real;
  }
  x = out;
}

proc doValidate(): bool {
  const testN = 64;
  for trial in 0..1 {
    var x: [0..<testN] complex(128);
    var rs = new randomStream(real, seed=trial+1);
    for i in 0..<testN { x[i].re = rs.rand(); x[i].im = rs.rand(); }
    var xref = x; var xgen = x;
    correctIfft(xref); ifft(xgen);
    for i in 0..<testN {
      if abs(xref[i].re - xgen[i].re) > 1e-9 then return false;
      if abs(xref[i].im - xgen[i].im) > 1e-9 then return false;
    }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] complex(128);
  var rs = new randomStream(real, seed=42);
  for i in 0..<n { x[i].re = rs.rand(); x[i].im = rs.rand(); }
  const xorig = x;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { x = xorig; sw.restart(); ifft(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { x = xorig; sw.restart(); correctIfft(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

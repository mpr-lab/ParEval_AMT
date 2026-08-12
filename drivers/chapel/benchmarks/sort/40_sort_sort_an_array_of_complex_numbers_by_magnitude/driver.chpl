use Time, Random, Math, Sort;
config const problemSize: int = 1 << 22;
const NITER = 5;

record MagnitudeComparator {
  proc key(z: complex(128)): real { return sqrt(z.re*z.re + z.im*z.im); }
}

proc correctSortComplexByMagnitude(ref x: [] complex(128)) {
  var cmp: MagnitudeComparator;
  sort(x, comparator=cmp);
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var x: [0..<n] complex(128);
    var rs = new randomStream(real, seed=trial+1);
    for i in 0..<n { x[i].re = rs.next(); x[i].im = rs.next(); }
    var xref = x; var xgen = x;
    correctSortComplexByMagnitude(xref); sortComplexByMagnitude(xgen);
    for i in 0..<n {
      if abs(xref[i].re - xgen[i].re) > 1e-12 then return false;
      if abs(xref[i].im - xgen[i].im) > 1e-12 then return false;
    }
  }
  return true;
}

proc main() {
  const n = problemSize;
  var x: [0..<n] complex(128);
  var rs = new randomStream(real, seed=42);
  for i in 0..<n { x[i].re = rs.next(); x[i].im = rs.next(); }
  const xorig = x;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { x = xorig; sw.restart(); sortComplexByMagnitude(x); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { x = xorig; sw.restart(); correctSortComplexByMagnitude(x); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

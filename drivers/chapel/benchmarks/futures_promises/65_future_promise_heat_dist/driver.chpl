use Time, Random;
config const problemSize: int = 1 << 10;
const NITER = 5;

proc correctParallelHeat(ref U: [] real, np: int, nx: int, nt: int, k: real, dt: real, dx: real) {
  const total = np * nx;
  var U0 = U; var U1: [0..<total] real;
  const coeff = k * dt / (dx * dx);
  for t in 0..<nt {
    ref cur = if t % 2 == 0 then U0 else U1;
    ref nxt = if t % 2 == 0 then U1 else U0;
    for i in 0..<total {
      const left  = if i == 0 then total-1 else i-1;
      const right = (i+1) % total;
      nxt[i] = cur[i] + coeff*(cur[left] - 2.0*cur[i] + cur[right]);
    }
  }
  U = if nt % 2 == 0 then U0 else U1;
}

proc doValidate(): bool {
  const np = 8; const nx = 16; const nt = 10;
  for trial in 0..1 {
    var U: [0..<np*nx] real; var rs = new randomStream(real, seed=trial+1); rs.fill(U);
    var Uc = U; var Ut = U;
    correctParallelHeat(Uc, np, nx, nt, 0.5, 0.1, 1.0);
    parallelHeat(Ut, np, nx, nt, 0.5, 0.1, 1.0);
    for i in Uc.domain do if abs(Uc[i]-Ut[i]) > 1e-8 then return false;
  }
  return true;
}

proc main() {
  const np = problemSize / 8; const nx = 8; const nt = 20;
  var U: [0..<np*nx] real; var rs = new randomStream(real, seed=42); rs.fill(U);
  const orig = U;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch; var computeTotal = 0.0;
  for i in 0..<NITER { U = orig; sw.restart(); parallelHeat(U, np, nx, nt, 0.5, 0.1, 1.0); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);
  var bestTotal = 0.0;
  for i in 0..<NITER { U = orig; sw.restart(); correctParallelHeat(U, np, nx, nt, 0.5, 0.1, 1.0); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

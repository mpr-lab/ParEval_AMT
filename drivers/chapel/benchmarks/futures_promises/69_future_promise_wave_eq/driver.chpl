use Time, Random, Math;
config const problemSize: int = 1 << 10;
const NITER = 5;

proc correctWaveEquation(ref U: [] real, N: int, nt: int, c: real, dt: real, dx: real) {
  const coeff = (c*dt/dx)**2;
  var Uprev = U; var Ucur = U; var Unext: [0..<N] real;
  for t in 0..<nt {
    for i in 1..<N-1 do Unext[i] = 2.0*Ucur[i] - Uprev[i] + coeff*(Ucur[i-1] - 2.0*Ucur[i] + Ucur[i+1]);
    Unext[0] = 0.0; Unext[N-1] = 0.0;
    Uprev = Ucur; Ucur = Unext;
  }
  U = Ucur;
}

proc doValidate(): bool {
  const n = 128;
  for trial in 0..1 {
    var U: [0..<n] real; var rs = new randomStream(real, seed=trial+1); rs.fill(U);
    U[0] = 0.0; U[n-1] = 0.0;
    var Uc = U; var Ut = U;
    correctWaveEquation(Uc, n, 10, 0.5, 0.1, 1.0);
    waveEquation(Ut, n, 10, 0.5, 0.1, 1.0);
    for i in Uc.domain do if abs(Uc[i]-Ut[i]) > 1e-8 then return false;
  }
  return true;
}

proc main() {
  const N = problemSize; var U: [0..<N] real; var rs = new randomStream(real, seed=42); rs.fill(U);
  U[0] = 0.0; U[N-1] = 0.0;
  const orig = U;

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch; var computeTotal = 0.0;
  for i in 0..<NITER { U = orig; sw.restart(); waveEquation(U, N, 20, 0.5, 0.1, 1.0); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);
  var bestTotal = 0.0;
  for i in 0..<NITER { U = orig; sw.restart(); correctWaveEquation(U, N, 20, 0.5, 0.1, 1.0); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

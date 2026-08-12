use Time, Random;
config const problemSize: int = 1 << 22;
const NITER = 5;

record Book { var title: string; var pages: int; }

proc correctFindLastShortBook(books: [] Book): int {
  var last = -1;
  for i in books.domain { if books[i].pages < 100 then last = i; }
  return last;
}

proc doValidate(): bool {
  const n = 1024;
  for trial in 0..1 {
    var books: [0..<n] Book;
    var rs = new randomStream(int, seed=trial+1);
    for i in 0..<n { books[i].title = "Book"; books[i].pages = ((rs.rand() % 200) + 200) % 200; }
    if correctFindLastShortBook(books) != findLastShortBook(books) then return false;
  }
  return true;
}

proc main() {
  const n = problemSize;
  var books: [0..<n] Book;
  var rs = new randomStream(int, seed=42);
  for i in 0..<n { books[i].title = "Book"; books[i].pages = ((rs.rand() % 200) + 200) % 200; }

  const isValid = doValidate();
  writeln("Validation: ", if isValid then "PASS" else "FAIL");
  if !isValid then return;

  var sw: stopwatch;
  var computeTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = findLastShortBook(books); sw.stop(); computeTotal += sw.elapsed(); }
  writeln("Time: ", computeTotal / NITER);

  var bestTotal = 0.0;
  for it in 0..<NITER { sw.restart(); var r = correctFindLastShortBook(books); sw.stop(); bestTotal += sw.elapsed(); }
  writeln("BestSequential: ", bestTotal / NITER);
}

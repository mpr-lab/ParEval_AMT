// Main driver for generated serial Chapel code. This relies on several externally available
// procedures:
//
//   - init() -- returns a context object
//   - compute(ctx) -- runs the benchmark
//   - best(ctx) -- runs the best sequential code
//   - validate(ctx) -- returns true if the benchmark is valid
//   - reset(ctx) -- resets the benchmark
//   - destroy(ctx) -- frees the context object
//
// These procedures are defined in the driver for the given benchmark and handle
// the data and calling the generated code.

use Time;

// Define the Context type (will be provided by benchmark driver)
record Context;

// External procedures that will be provided by the benchmark driver
extern proc init(): Context;
extern proc compute(ref ctx: Context);
extern proc best(ref ctx: Context);
extern proc validate(ref ctx: Context): bool;
extern proc reset(ref ctx: Context);
extern proc destroy(ref ctx: Context);

// Main procedure
proc main(args: [0..#] string) {
    // initialize settings from arguments
    var NITER: int = 5;
    if args.size > 1 {
        NITER = args[1].toInt();
    }

    // initialize
    var ctx = init();

    // validate
    var isValid = validate(ctx);
    writeln("Validation: " + (if isValid then "PASS" else "FAIL"));
    if !isValid {
        destroy(ctx);
        return;
    }

    // benchmark
    var totalTime: real = 0.0;
    for i in 1..NITER {
        var start = Time.now();
        compute(ctx);
        var end = Time.now();
        totalTime += (end - start).toSeconds();

        reset(ctx);
    }
    writeln("Time: " + totalTime / NITER:0.15f);

    // benchmark best
    totalTime = 0.0;
    for i in 1..NITER {
        var start = Time.now();
        best(ctx);
        var end = Time.now();
        totalTime += (end - start).toSeconds();

        reset(ctx);
    }
    writeln("BestSequential: " + totalTime / NITER:0.15f);

    // cleanup
    destroy(ctx);
}

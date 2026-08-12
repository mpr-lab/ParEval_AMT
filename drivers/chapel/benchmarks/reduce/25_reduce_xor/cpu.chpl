// Driver for 25_reduce_xor for Serial, OpenMP, MPI, and MPI+OpenMP
// This implements the interface expected by the model drivers:
//   - init() -- returns a context object
//   - compute(ctx) -- runs the benchmark
//   - best(ctx) -- runs the best sequential code
//   - validate(ctx) -- returns true if the benchmark is valid
//   - reset(ctx) -- resets the benchmark
//   - destroy(ctx) -- frees the context object

use Utilities;

// Include the generated code (will be provided during compilation)
include "generated-code.chpl";

// Include the baseline implementation
include "baseline.chpl";

// Context record
record Context {
    var x: [] bool;
    var result: bool;
}

// Initialize the context
proc init(): Context {
    var ctx = new Context();
    ctx.x = new [0..<DRIVER_PROBLEM_SIZE] bool;
    reset(ctx);
    return ctx;
}

// Reset the context with random data
proc reset(ref ctx: Context) {
    fillRand(ctx.x);
    #if defined(USE_MPI) || defined(USE_MPI_OMP)
    broadcastBools(ctx.x);
    #endif
}

// Compute the generated function
proc compute(ref ctx: Context) {
    ctx.result = reduceLogicalXOR(ctx.x);
}

// Compute the best (baseline) function
proc best(ref ctx: Context) {
    ctx.result = correctReduceLogicalXOR(ctx.x);
}

// Validate the implementation
proc validate(ref ctx: Context): bool {
    const TEST_SIZE: int = 1024;
    var x: [0..<TEST_SIZE] bool;
    var correct, test: bool;

    const numTries = MAX_VALIDATION_ATTEMPTS;
    for trialIter in 1..numTries {
        // set up input
        fillRand(x);
        #if defined(USE_MPI) || defined(USE_MPI_OMP)
        broadcastBools(x);
        #endif

        // compute correct result
        correct = correctReduceLogicalXOR(x);

        // compute test result
        test = reduceLogicalXOR(x);
        sync();

        var isCorrect: bool = true;
        if isRoot() && correct != test {
            isCorrect = false;
        }
        
        #if defined(USE_MPI) || defined(USE_MPI_OMP)
        broadcastBool(isCorrect);
        #endif
        
        if !isCorrect {
            return false;
        }
    }

    return true;
}

// Destroy the context
proc destroy(ref ctx: Context) {
    delete ctx.x;
    delete ctx;
}

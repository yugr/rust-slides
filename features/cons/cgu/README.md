Rust uses the concept of codegen units (CGUs) to parallelize compilation of crates and significantly reduce build times (16-32 cgus is the default value). However, splitting the program into several independent compilation units prevents some interprocedural optimizations:

 - Inlining requires explicit annotation and link-time optimization (but is still not perfect with these solutions) (https://github.com/wasmi-labs/wasmi/issues/339#issuecomment-1023034031)
 - Dead code elimination is unable to detect dead loops if they are split over multiple CGUs (https://github.com/rust-lang/rust/issues/57235#issuecomment-450673756)
 - CGUs cause vtable duplication (but vtables in different CGUs are not always equal) which causes some pointer comparisons to be unpredictable (https://github.com/rust-lang/rust/issues/46139)
 - Splitting code between CGUs can be (need to check current state) non-deterministic and thus result in performance hits from building on a different machine or adding an unrelated function (https://internals.rust-lang.org/t/lets-talk-about-parallel-codegen/2759/32).
 - Nethercote post (https://nnethercote.github.io/2023/07/11/back-end-parallelism-in-the-rust-compiler.html) states that CGUs are formed from rust modules and are then merged if needed.
This is a much more reproducible approach as opposed to function-based splitting in the previous point.

CGUs can be disabled (via `-C codegen-units=1`) but [recommended fix](https://llvm.org/devmtg/2021-02-28/slides/Patrick-rust-llvm.pdf) is to use ThinLTO.

# TODO

- Check slowdown (`O(N^2)` ?) and perf improvements when disabling CGUs (`-C codegen-units=1`) for large/performance-sensitive packages
- Is CGU number fixed or depends on build PC ? If latter, Rust builds are non-reproducible...

Rust uses the concept of codegen units (CGUs) to parallelize compilation of crates and significantly reduce build times (16 cgus is the default value, but not as strictly enforced when not specified by user). However, splitting the program into several independent compilation units prevents some interprocedural optimizations.

CGUs can be disabled (via `-C codegen-units=1`) e.g. Rustc itself is compiled with [single CGU](https://nnethercote.github.io/2024/03/06/how-to-speed-up-the-rust-compiler-in-march-2024.html). See `src/ci/docker/host-x86_64/dist-x86_64-linux/Dockerfile` for all Rust release build flags.
[Recommended fix](https://llvm.org/devmtg/2021-02-28/slides/Patrick-rust-llvm.pdf) is to use ThinLTO
but this [does not always](https://github.com/rust-lang/rust/issues/47745) restore performance:
> I think at this point the disparity between codegen-units + ThinLTO vs codegen-units=1 is,
> to some degree, something that we are accepting as a "fact of life"

This may not be a huge downside compared to C++ because Rust TU's are generally much larger (how much ?).
In a sense `codegen-units=N` is equivalent to C++ unity builds (with `N` batches).

Note that `--emit=asm` automatically enables `-C codegen-units=1` which may change generated code.

# Known performance hits

- Inlining requires explicit annotation (`#[inline]`) and LTO but is still not perfect with these solutions:
  * https://github.com/wasmi-labs/wasmi/issues/339#issuecomment-1023034031
  * https://github.com/rust-lang/rust/issues/47745
- Dead code elimination is unable to detect dead loops if they are split over multiple CGUs (https://github.com/rust-lang/rust/issues/57235#issuecomment-450673756). Could not reproduce, with current CGU partitioning algorithm a loop should never be split across multiple CGUs.
- CGUs cause vtable duplication (but vtables in different CGUs are not always equal) which causes some pointer comparisons to be unpredictable (https://github.com/rust-lang/rust/issues/46139)
  * This may be a problem for optimizer because different copies of vtables will block devirtualization; hopefully it'll be fixed in [#68262](https://github.com/rust-lang/rust/issues/68262)

# Determinism

Splitting code between CGUs can be (need to check current state) non-deterministic and thus result in performance hits from building on a different machine or adding an unrelated function (https://internals.rust-lang.org/t/lets-talk-about-parallel-codegen/2759/32).

Nethercote's post (https://nnethercote.github.io/2023/07/11/back-end-parallelism-in-the-rust-compiler.html) states that CGUs are formed from rust modules and are then merged if needed.
This is a much more reproducible approach as opposed to function-based splitting in the previous point.

# Links

Architecture and design choices are discussed by Nethercote [here](https://nnethercote.github.io/2023/07/11/back-end-parallelism-in-the-rust-compiler.html).

[Discussion](https://internals.rust-lang.org/t/lets-talk-about-parallel-codegen/2759/49) of pros and cons of CGUs.

# TODO

- [x] Check compile slowdown (`O(N^2)` ?) and perf improvements when disabling CGUs (`-C codegen-units=1`) for large/performance-sensitive packages
  * We can reuse data from [Let's talk about parallel codegen](https://internals.rust-lang.org/t/lets-talk-about-parallel-codegen/2759/1) but maybe it is too old ?
- [x] Is CGU number fixed or depends on build PC ? If latter, Rust builds are non-reproducible...
- [x] @zack suggests that crates are generally largers than C/C++ TUs (more like full programs i.e. unity builds)

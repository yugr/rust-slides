Good description of current state of CGU splitting, heuristics and trade-offs is presented in `compiler/rustc_monomorphize/src/partitioning.rs`.

# Background

Rust compiler automatically utilizes iterative comilation to speed up compilation process by splitting the compiled crate into codegen units (CGUs). Each codegen unit becomes a separate LLVM module and is compiled and optimized independently, without any possibility of cross-module optimizations (well, link-time has LTO). CGUs can be compiled in parallel, which significantly speeds up compilation (long compilation times are a known issue for Rust), but lack of inter-CGU optimization results in runtime performance impact. Having one CGU results in best optimizations, but worst compile time and vice versa. In C++ world you can think about it like separate compilation and unity builds. In a sense `codegen-units=N` is equivalent to C++ unity builds (with `N` batches).

Some missed optimizations due to CGU splitting can be mitigated by ThinLTO, however it generally does not achieve the same performance as CGU=1.

> I think at this point the disparity between codegen-units + ThinLTO vs codegen-units=1 is,
> to some degree, something that we are accepting as a "fact of life"

# CGU splitting behaviour

>  There are two codegen units for every source-level module:
>  - One for "stable", that is non-generic, code
>  - One for more "volatile" code, i.e., monomorphized instances of functions defined in that module

CGUs smaller than some heuristic threshold are always merged together, as for very small CGUs there is no/not enough benefit in compiling them separately.
When the requested number of CGUs is lower than generated with such heuristic, CGUs are merged based on their size (parallelization is best when all CGUs are approximately the same size) and on the number of overlapping copied for inlining functions.

Inlining is not possible across CGU boundary, so bodies of functions which are marked with `#[inline]` are copied into every CGU so that inlining can be performed.

# CGU number configuration

Number of CGUs to be used can be set by `-C codegen-units=<N>` flag provided to a compiler invocation or by `codegen-units` setting in crate's `Cargo.toml` (uses the same flag).

Note that `--emit=asm` automatically enables `-C codegen-units=1` which may change generated code (the motivation is that users expect to get a single asm artifact, and multiple CGUs would generate several).

# Known performance hits

- ThinLTO is not as good as `codegen-units=1`
  * https://github.com/rust-lang/rust/issues/47745
- Inlining requires explicit annotation `#[inline]` (otherwise function body will not be available in other CGUs).
- CGUs cause vtable duplication (but vtables in different CGUs are not always equal) which causes some pointer comparisons to be unpredictable (https://github.com/rust-lang/rust/issues/46139)
  * This may be a problem for optimizer because different copies of vtables will block devirtualization; hopefully it'll be fixed in [#68262](https://github.com/rust-lang/rust/issues/68262)

# Compile-time and performance with different numbers of CGUs

Baseline is built with 16 CGUs

## 1 CGU

### Build times

- `SpacetimeDB`: 278 sec
- `bevy`: 257 sec
- `meilisearch`: 462 sec
- `nalgebra`: 78 sec
- `oxipng`: 23 sec
- `rav1e`: 85 sec
- `regex`: 58 sec
- `ruff`: 148 sec
- `rust_serialization_benchmark`: 247 sec
- `tokio`: 49 sec
- `uv`: 311 sec
- `veloren`: 1045 sec
- `zed`: 333 sec

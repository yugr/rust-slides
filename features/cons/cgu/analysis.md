Good description of current state of CGU splitting, heuristics and trade-offs is presented in `compiler/rustc_monomorphize/src/partitioning.rs`.

# Background

Rust compiler automatically utilizes iterative compilation to speed up compilation process by splitting the compiled crate into codegen units (CGUs). Each codegen unit becomes a separate LLVM module and is compiled and optimized independently, without any possibility of cross-module optimizations (well, link-time has LTO). CGUs can be compiled in parallel, which significantly speeds up compilation (long compilation times are a known issue for Rust), but lack of inter-CGU optimization results in runtime performance impact. Having one CGU results in best optimizations, but worst compile time and vice versa. In C++ world you can think about it like separate compilation and unity builds. In a sense `codegen-units=N` is equivalent to C++ unity builds (with `N` batches).

Some missed optimizations due to CGU splitting can be mitigated by ThinLTO, however it generally does not achieve the same performance as CGU=1.

> I think at this point the disparity between codegen-units + ThinLTO vs codegen-units=1 is,
> to some degree, something that we are accepting as a "fact of life"
>
> -- https://github.com/rust-lang/rust/issues/47745#issuecomment-1139664706

# CGU splitting behaviour

>  There are two codegen units for every source-level module:
>  - One for "stable", that is non-generic, code
>  - One for more "volatile" code, i.e., monomorphized instances of functions defined in that module
>
> -- `compiler/rustc_monomorphize/src/partitioning.rs`

From this initial split in two CGU per source-level module based on whether or not function is generic or not, CGUs are only merged, so one source-level module will produce at most two CGUs.
CGUs smaller than some heuristic threshold are always merged together (can lead bring CGU count lower than default value, but strictly honours user-set value), as for very small CGUs there is no/not enough benefit in compiling them separately.
When the requested number of CGUs is lower than generated with such heuristic, CGUs are merged based on their size (parallelization is best when all CGUs are approximately the same size) and on the number of overlapping functions which were copied for inlining purposes.

Inlining is not possible across CGU boundary, so bodies of functions which are marked with `#[inline]` are copied into every CGU so that inlining can be performed.

# CGU number configuration

Number of CGUs to be used can be set by `-C codegen-units=<N>` flag provided to a compiler invocation or by `codegen-units` setting in crate's `Cargo.toml` (uses the same flag).

Note that `--emit=asm` automatically enables `-C codegen-units=1` which may change generated code (the motivation is that users expect to get a single assembly artifact, and multiple CGUs would generate several).

# Known performance hits

- ThinLTO is not as good as `codegen-units=1`
  * https://github.com/rust-lang/rust/issues/47745
- Inlining requires explicit annotation `#[inline]` (otherwise function body will not be available in other CGUs).
- CGUs cause vtable duplication (but vtables in different CGUs are not always equal) which causes some pointer comparisons to be unpredictable (https://github.com/rust-lang/rust/issues/46139)
  * This may be a problem for optimizer because different copies of vtables will block devirtualization; hopefully it'll be fixed in [#68262](https://github.com/rust-lang/rust/issues/68262)

# Compile-time and performance with different numbers of CGUs

Baseline is built with 16 CGUs

## x86_64

CPU:
```
$ lscpu
Architecture:                         x86_64
CPU op-mode(s):                       32-bit, 64-bit
Byte Order:                           Little Endian
Address sizes:                        46 bits physical, 48 bits virtual
CPU(s):                               24
On-line CPU(s) list:                  0-23
Thread(s) per core:                   2
Core(s) per socket:                   6
Socket(s):                            2
NUMA node(s):                         2
Vendor ID:                            GenuineIntel
CPU family:                           6
Model:                                63
Model name:                           Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz
Stepping:                             2
CPU MHz:                              2597.060
CPU max MHz:                          3200.0000
CPU min MHz:                          1200.0000
BogoMIPS:                             4794.66
Virtualization:                       VT-x
L1d cache:                            384 KiB
L1i cache:                            384 KiB
L2 cache:                             3 MiB
L3 cache:                             30 MiB
```

### 16 CGU

- `SpacetimeDB`:  223 sec
- `bevy`:  191 sec
- `meilisearch`:  352 sec
- `nalgebra`:  75 sec
- `oxipng`:  25 sec
- `rav1e`:  63 sec
- `regex`:  45 sec
- `ruff`:  110 sec
- `rust_serialization_benchmark`:  160 sec
- `tokio`:  40 sec
- `uv`:  375 sec
- `veloren`:  1167 sec
- `zed`:  283 sec

### 8 CGU

- `SpacetimeDB`: 222 sec, +25%
- `bevy`: 191 sec, +35%
- `meilisearch`: 456 sec, +1%
- `nalgebra`: 74 sec, +5%
- `oxipng`: 25 sec, -8%
- `rav1e`: 63 sec, +35%
- `regex`: 45 sec, +29%
- `ruff`: 109 sec, +36%
- `rust_serialization_benchmark`: 162 sec, +52%
- `tokio`: 40 sec, +22%
- `uv`: 349 sec, -11%
- `veloren`: 1107 sec, -6%
- `zed`: 284 sec, +17%

#### Performance gain

- `SpacetimeDB_0.json`: +0.7%
- `bevy_0.json`: +0.1%
- `meilisearch_0.json`: +1.2%
- `nalgebra_0.json`: +0.3%
- `oxipng_0.json`: -1.0%
- `rav1e_0.json`: -3.4%
- `regex_0.json`: +0.3%
- `ruff_0.json`: -0.9%
- `rust_serialization_benchmark_0.json`: +0.5%
- `tokio_0.json`: -0.1%
- `uv_0.json`: -1.7%
- `veloren_0.json`: -5.0%
- `zed_0.json`: +0.7%

### 1 CGU

#### Build times

- `SpacetimeDB`: 278 sec, +24%
- `bevy`: 257 sec, +34%
- `meilisearch`: 462 sec, +31%
- `nalgebra`: 78 sec, +4%
- `oxipng`: 23 sec, -8%
- `rav1e`: 85 sec, +34%
- `regex`: 58 sec, +28%
- `ruff`: 148 sec, +34%
- `rust_serialization_benchmark`: 247 sec, +54%
- `tokio`: 49 sec, +22%
- `uv`: 311 sec, -17%
- `veloren`: 1045 sec, -10%
- `zed`: 333 sec, +17%

#### Performance gain

- `SpacetimeDB_0.json`: +5.1%
- `bevy_0.json`: +4.2%
- `meilisearch_0.json`: +8.4%
- `nalgebra_0.json`: +2.7%
- `oxipng_0.json`: +1.8%
- `rav1e_0.json`: -1.4%
- `regex_0.json`: +0.1%
- `ruff_0.json`: +3.6%
- `rust_serialization_benchmark_0.json`: +4.2%
- `tokio_0.json`: +2.3%
- `uv_0.json`: +1.8%
- `veloren_0.json`: +1.4%
- `zed_0.json`: +10.2%

# TODO

- Collect compiler optimization counters:
  * licm, gvn, cse, loop-vectorize, inline
- Add info how to repro results (scripts ?)
- Add branch links

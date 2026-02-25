# Administrivia

Assignee: yugr

Parent task: gh-20

Effort: 96h

# Background

See [README](README.md), particularly [C++ status](README.md#c).

Note that feature consists from
  - compiler part (instrumentation of index accesses)
  - stdlib part (manual checks in stdlib containers)

2024 CVE stats: 3622 CVEs out of total 33k i.e. 11%
(but other CVEs are relatively higher-level e.g. input validation, etc.).

2024 KEV stats: 12 KEVs out of total 181 i.e. 6.5%
```
$ CVE/kev_scanner.py -y 2024 known_exploited_vulnerabilities.json
3 Integer Overflow
12 Memory Overflow
0 Stack overflow
0 Uninitialized
181 Total
```

[Mitre 2024 top-25 weaknesses rating](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html):
buffer overflows are still no. 2, 6 and 20.

For more information on security vulnerabilities caused by memory errors check
[Hardening: current status and trends](https://github.com/yugr/slides/blob/main/CppZeroCost/2025/EN.pdf).

TODO:
  - situation in other langs (Java, C#, Swift, Ada)

# Examples

URLO discussions of huge perf regressions caused by bounds checks (BCs)
that are before ~2022 are largely irrelevant
(also [matklad's examples](https://github.com/matklad/bounds-check-cost/blob/master/src/main.rs))
because LLVM optimizer has significantly improved since then.

LLVM can LICM bounds checks from loop very well now.
E.g. all loops that do simple `0..n`-like iterations (`f1`-`f4`, `f7`, `f10` (!), `f12`) over slices of Vecs optimize well
i.e. checks are removed from loops and loops are vectorized.

More complex examples that require non-trivial arithmetic still break optimizer
(e.g. `f5`, `f6`, `f8`, `f11`, `f13`).
Also unnecessary bounds checks are not always eliminated (`f10`).

# Optimizations

Unnecessary BCs are removed via value tracking in passes like InstCombine.

Optimization of BCs in loops may happen in several ways.
For example for
```
$ cat min.rs
pub fn f1(v: &[i32], n: usize) -> i32 {
    let mut ans = 0;
    for i in 0..n {
        ans += v[i];
    }
    ans
}
$ rustc --crate-type=rlib -O -C codegen-units=1 -C target-cpu=native -Cllvm-args=-print-after-all min.rs
```
it's done by two passes:
  - IndVarSimplifyPass - moves condition computation from loop
  - SimpleLoopUnswitchPass - removes condition from loop

On the other hand for
```
$ cat min.rs
pub fn f1(v: &mut [i32], n: usize) {
    for i in 0..n {
        v[i] = i as i32;
    }
}
```
all is done in LoopVectorize (probly on `createReplacement` in `LoopVectorize.cpp`).
If vectorizer is disabled (via `-Cllvm-args=-vectorize-loops=false`)
BCs will not be removed.

TODO:
  - list limitations ?

# Workarounds for bounds checks

See [README](README.md#solutions).

# Suggested reading

[How to avoid bounds checks in Rust without unsafe](https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e)
  * Bible of Rust bounds checks

[Story-time: C++, bounds checking, performance, and compilers](https://chandlerc.blog/posts/2024/11/story-time-bounds-checking/) (and links)
  * Bounds checking in C++

# Performance impact

## Prevalence

We should measure reduction of panics in our benchmarks:
  - overall count
  - loops with panics

Overall count may be detected by grepping disasm
but beware of stripping in project's `Cargo.toml`.

### Overall panics

I think we should not disable inlining because many BCs will not be removable after that.

Note that some project may strip panics or turn them to aborts so be sure to
```
$ sed -i -e 's/^\(strip\|panic\)/#\1/' Cargo.toml
```

#### Analysis for rustc

Here is the distribution of panics in rustc compiler (panics caused by bounds checks are marked with `!`):
```
$ ./x build -j12 --stage 2 compiler
$ objdump -rd build/x86_64-unknown-linux-gnu/stage2/lib/librustc_driver*.so | rustfilt > librustc_driver.d
$ grep 'call.*\(unwrap_failed\|expect_failed\|assert_failed\|slice_.*_fail\|core::panicking\|std::panicking\)' librustc_driver.d | sed -e 's/^[^<]*<//; s/@.*//' | sort | uniq -c | sort -nk1
...
    119 core::panicking::assert_failed::<u128, u128>
    128 core::panicking::assert_failed::<rustc_abi::Size, rustc_abi::Size>
    241 core::panicking::assert_failed::<bool, bool>
    310 std::panicking::try::cleanup
!    315 core::slice::index::slice_index_order_fail
    413 core::panicking::assert_failed::<hashbrown::control::tag::Tag, hashbrown::control::tag::Tag>
!    418 core::str::slice_error_fail
    434 core::panicking::assert_failed_inner
    # Emitted for explicit `panic!` or `assert!`
    559 std::panicking::begin_panic           # std::panicking is built on top of core::panicking, this is called in std context
    727 std::panicking::panic_count::is_zero_slow_path
!   1101 core::slice::index::slice_start_index_len_fail
   1498 core::panicking::panic_null_pointer_dereference
!   2193 core::slice::index::slice_end_index_len_fail
   3479 core::panicking::panic_misaligned_pointer_dereference
   3686 core::result::unwrap_failed
!   9516 core::panicking::panic_bounds_check
  10476 core::panicking::assert_failed        # Emitted for explicit assert_eq!/assert_ne! (in both std and no_std contexts)
  11880 core::option::expect_failed
  11927 core::option::unwrap_failed
  30663 core::panicking::panic_cannot_unwind  # Used for GCC unwinder to mark un-unwindable functions (e.g. `extern "C"`)
  30943 core::panicking::panic_fmt            # Emitted for explicit panic!/assert! with params in no_std context
  40774 core::panicking::panic                # Emitted for explicit panic!/assert! w/o params in no_std context
 124062 core::panicking::panic_in_cleanup     # Used for GCC unwinder to catch and abort on panics in landing pads
 143097 core::panicking::panic_nounwind       # Used by various fatal checks in stdlib which call e.g. assert_unsafe_precondition! from ub_checks.
                                              # This feature is off by default but can be enabled with -Zub-checks
                                              # (to become -Cub-checks, similar to -Coverflow-checks) or -Cdebug-assertions.
                                              # It's enabled in compiler because it's compiled with -Cdebug-assertions by default
                                              # (that's default from bootstrap.compiler.toml for "compiler" profile).
```

For rustc with `debug-assertions=false` I get more reasonable results:
```
    204 core::panicking::assert_failed_inner
    299 std::panicking::try::cleanup
!    320 core::slice::index::slice_index_order_fail
    344 core::panicking::panic_cannot_unwind
!    444 core::str::slice_error_fail
    550 core::panicking::assert_failed
    556 std::panicking::begin_panic
    568 std::panicking::panic_count::is_zero_slow_path
!   1134 core::slice::index::slice_start_index_len_fail
!   2300 core::slice::index::slice_end_index_len_fail
   3651 core::result::unwrap_failed
   7007 core::panicking::panic_fmt
!   9243 core::panicking::panic_bounds_check
  11409 core::option::expect_failed
  11632 core::option::unwrap_failed
  14865 core::panicking::panic
 117973 core::panicking::panic_in_cleanup
```

Note that `!`-marks above are approximate:
  - some `core::str::slice_error_fail` are due to char boundary checks
  - some other asserts mat be due to boundary checks in containers

To compare how big are the savings, build stage2 compiler with
```
[rust]
debug-assertions = false
...
```
and run
```
$ count-panics ./build/x86_64-unknown-linux-gnu/stage2/lib/librustc_driver*.so
```

Results are
  - baseline: 64410
  - bounds: 51122 (-21%)

### Panics in loops

Panics in loops may be found by analyzing LLVM via
```
export RUSTFLAGS='-Csave-temps'
```
which will store `.bc` files in target dir (we need `XXX.rcgu.bc`, without `no-opt`).
Beware that this [overloads settings in Cargo.toml](https://internals.rust-lang.org/t/we-need-configurably-additive-rustflags/19851)
and may break build.

#### Analysis for oxipng

```
# For ThinLTO builds need
#   find target-baseline -name *.thin-lto-after-pm.bc

$ RUSTFLAGS='-Csave-temps' cargo +baseline b --target-dir=target-baseline --release
$ find target-baseline -name '*.rcgu.bc' | xargs ~/tasks/rust/llvm-tool/CountLoops > results.txt
$ grep -c 'Loop may NOT panic' results.txt
3419
$ grep -c 'Loop may panic' results.txt
328

$ RUSTFLAGS='-Csave-temps' cargo +bounds b --target-dir=target-bounds --release
$ find target-bounds -name '*.rcgu.bc' | xargs ~/tasks/rust/llvm-tool/CountLoops > results.txt
$ grep -c 'Loop may NOT panic' results.txt
3826
$ grep -c 'Loop may panic' results.txt
73
```

So stats are
  - baseline: 8.8% loops panic
  - bounds: 1.9% loops panic (5x improvement)

#### Analysis for rustc

Add
```
[rust]
debug-assertions = false
```
to bootstrap.toml and run
```
$ RUSTFLAGS_NOT_BOOTSTRAP='-Csave-temps' ./x build --stage 2 compiler
$ find -name '*.rcgu.bc' | xargs ~/tasks/rust/llvm-tool/CountLoops > results.txt

# Baseline
$ grep -c 'Loop may NOT panic' results.txt
66946
$ grep -c 'Loop may panic' results.txt
3058

# Bounds
$ grep -c 'Loop may NOT panic' results.txt
68048
$ grep -c 'Loop may panic' results.txt
706
```

So stats are
  - baseline: 4.8% loops panic
  - bounds: 1% (5x improvement)

## Disabling the check

Compiler patch is in branch [yugr/disable-bounds-checks/1](https://github.com/yugr/rust-private/tree/yugr/disable-bounds-checks/1).
It
  - disables checks in compiler
  - removes relevant `panic!` / `assert!` / etc. in stdlib

Compiler part is based on https://blog.readyset.io/bounds-checks .

For stdlib I searched for
```
^\(.*\/\/\/\)\@!.*\(panic!\|\<assert!\|unreachable!\|_fail[a-z_]*(\|\.unwrap(\|\.expect(\)
```
in library/core and library/alloc for most important types:
  - arrays (core/src/array) :
    * updated `split_array_ref/mut` and `rsplit_array_ref/mut`
  - slices:
    * core/src/slice
      + removed all relevant asserts
    * alloc/src/slice.rs
      + high-level APIs without panics
  - strs:
    * core/src/str
      + updated `index` and `index_mut` in `str/traits.rs`
      + otherwise only char boundary checks
    * alloc/src/str.rs
      + high-level APIs without panics
  - Vec (alloc/src/vec and alloc/src/raw_vec)
    * `RawVec` has NULL-pointer checks for allocations but they are not relevant
    * updated methods in `vec/mod.rs`
  - String (alloc/src/string.rs)
    * only checks char boundaries
  - ptrs (core/src/ptr)
    * single check in `mut_ptr.rs`
  - ranges (core/src/range.rs and other range.rs files in core)
    * very few bounds checks
    * maybe need to replace `checked` ops with `unchecked` in `core/src/iter/range.rs` for iterators over `ops::Range/RangeInclusive`
      + but ranges may be used not only for indexes
  - VecDequeu (alloc/src/collections/vec_deque)
    * updated methods
  - HashMap/HashSet
    * can't update because it depends on hashbrown
  - BTreeXXX
    * not changed !

## Measurements

Note that according to [Hardening talk](https://github.com/yugr/slides/blob/main/CppZeroCost/2025/EN.pdf)
C++ hardening has comparable overhead:
  - `_FORTIFY_SOURCE`: 2-3%
  - STL hardening: 2-3% (0.3% w/ PGO+LTO)

### Static estimates

We can measure how bounds checking hurts most common optimizations.

Ideally we should be able to count optimization remarks but
they [do not work](https://github.com/rust-lang/rust/issues/142375)
and same goes for [compiler stats](https://github.com/rust-lang/rust/issues/142266).
So below we use `-Cllvm-args=-debug-only=...` instead.

_I think in general comparing compiler stats is useless - obviously default IR
(with checks) will have more opportunities for optimizations
(e.g. removal of duplicate checks) and its counts will be higher..._

#### Results for oxipng

Inliner:
```
$ export RUSTFLAGS='-Cllvm-args=-debug-only=inline -Ctarget-cpu=native'
$ cargo clean && cargo +baseline b -j1 --release |& grep -c 'Size after inlining:'
24320
$ cargo clean && cargo +bounds b -j1 --release |& grep -c 'Size after inlining:'
24208
```

Loop vectorizer:
```
$ export RUSTFLAGS='-Cllvm-args=-debug-only=loop-vectorize -Ctarget-cpu=native'
$ cargo clean && cargo +baseline b -j1 --release |& grep -c 'LV: Vectorizing'
102
$ cargo clean && cargo +bounds b -j1 --release |& grep -c 'LV: Vectorizing'
128
```

LICM:
```
$ export RUSTFLAGS='-Cllvm-args=-debug-only=licm'
$ cargo clean && cargo +baseline b -j1 --release |& grep -c 'LICM \(hoist\|sink\)ing'
42482
$ cargo clean && cargo +bounds b -j1 --release |& grep -c 'LICM \(hoist\|sink\)ing'
43094
```

GVN:
```
$ export RUSTFLAGS='-Cllvm-args=-debug-only=gvn'
$ cargo clean && cargo +baseline b -j1 --release |& grep -c 'GVN removed'
26458
$ cargo clean && cargo +bounds b -j1 --release |& grep -c 'GVN removed'
25302
```

CSE:
```
$ export RUSTFLAGS='-Cllvm-args=-debug-only=early-cse'
$ cargo clean && cargo +baseline b -j1 --release |& grep -c 'EarlyCSE CSE'
18603
$ cargo clean && cargo +bounds b -j1 --release |& grep -c 'EarlyCSE CSE'
18444
```

#### Results for rustc

Warning: ~10 hours to build and log file will take several GBs.

Do not forget to add to bootstrap.toml:
```
[llvm]
assertions = true
```

```
$ ./x build --stage 1 compiler
$ RUSTFLAGS_NOT_BOOTSTRAP='-Cllvm-args=-debug-only=inline,licm,early-cse,gvn,loop-vectorize,SLP' ./x build -j1 --stage 2 compiler &> build.log

# Baseline
$ grep -c 'Size after inlining:' build.log
2052611
$ grep -c 'LV: Vectorizing' build.log
2034
$ grep -c 'SLP: vectorized' build.log
23570
$ grep -c 'LICM \(hoist\|sink\)ing' build.log
2795747
$ grep -c 'GVN removed' build.log
757124
$ grep -c 'EarlyCSE CSE' build.log
2073875

# Bounds
$ grep -c 'Size after inlining:' build.log
2043429
$ grep -c 'LV: Vectorizing' build.log
2025
$ grep -c 'SLP: vectorized' build.log
23832
$ grep -c 'LICM \(hoist\|sink\)ing' build.log
2825349
$ grep -c 'GVN removed' build.log
704479
$ grep -c 'EarlyCSE CSE' build.log
2061444
```
(counters are slightly unstable because stdout of different CGU may intermix).

### Runtime improvements

#### x86_64

CPU: Intel(R) Core(TM) i7-9700K @ 3.60GHz

Results:
```
$ compare.py results/baseline results/bounds
SpacetimeDB_0.json: +0.8%
bevy: +0.6%
meilisearch_0.json: +3.0%
nalgebra: +0.4%
oxipng: +2.3%
rav1e: +3.8%
regex: +3.6%
ruff: +2.2%
rust_serialization_benchmark: +1%
tokio: -0.6%
uv: -0.6%
veloren: +5.7%
zed: -0.6%
```
(noise was <0.5%).

Performance of hardened C++ has been collected via `benchmarks/cpp/llvm-bench` and
`benchmarks/cpp/ffmpeg-bench` (for Clang 20):
  - Stack Protector
    * 2% Clang
    * 1% ffmpeg
    * no changes in PTS testsuite
  - `-D_FORTIFY_SOURCE=2/3`:
    * no changes in Clang, ffmpeg, PTS testsuite
  - STL indexing checks:
    * 0.5% Clang
    * ffmpeg N/A (no C++ code)
    * no changes in PTS testsuite
    * 2-3% [Google](https://bughunters.google.com/blog/6368559657254912/llvm-s-rfc-c-buffer-hardening-at-google)
  - `-fsanitize=object-size`:
    * no changes in Clang, ffmpeg
    * PTS testsuite: bullet 6.5%, coremark 1.2%, simdjson 25%
  - `-fsanitize=bounds`:
    * no changes Clang
    * 2.3% ffmpeg
    * PTS testsuite: povray 8.3%

(note: for PTS we ignored differences <= 1% due to high noise,
similar to [Exploiting Undefined Behavior in C/C++ Programs for
Optimization: A Study on the Performance Impact](https://web.ist.utl.pt/nuno.lopes/pubs/ub-pldi25.pdf)).

[Hardening: current status and trends](https://github.com/yugr/slides/blob/main/CppZeroCost/2025/EN.pdf)
reports worse numbers because it used old toolchains.

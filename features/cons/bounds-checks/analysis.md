# Administrivia

Parent task: gh-20

Effort: 50h

# Background

See [README](README.md).

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

TODO:
  - any other good posts ?

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
$ objdump -rd build/x86_64-unknown-linux-gnu/stage2/lib/librustc_driver*.so | c++filt | rustfilt > librustc_driver.d
$ grep 'call.*\(unwrap_failed\|expect_failed\|assert_failed\|slice_.*_fail\|core::panicking\)' librustc_driver.d | sed -e 's/.*<//; s/[+@].*//' | sort | uniq -c | sort -nk1
...
     52 core::panicking::assert_failed::hbeae657127ccdb04
     54 rustc_data_structures::fingerprint::Fingerprint, rustc_data_structures::fingerprint::Fingerprint>
     56 &[rustc_errors::SubstitutionPart; 2]>>
     56 &rustc_errors::SubstitutionPart>>
     56 (rustc_span::span_encoding::Span, alloc::string::String)>>
     72 T,A>::insert::assert_failed::hb73c9898ad762f24
     74 rustc_middle::ty::Ty, rustc_middle::ty::Ty>
     80 core::panicking::panic_const::panic_const_div_by_zero::hb3b56552275843e1
     81 rustc_type_ir::DebruijnIndex, rustc_type_ir::DebruijnIndex>
     87 core::panicking::panic_const::panic_const_rem_by_zero::hff9e8539b36b8d6d
    119 u128, u128>
    128 rustc_abi::Size, rustc_abi::Size>
    149 core::panicking::assert_failed::h85f033378b656379
    241 bool, bool>
!   315 core::slice::index::slice_index_order_fail::he688466d0d4f798a
!   418 core::str::slice_error_fail::hc91fd7c32234f2bf
    418 hashbrown::control::tag::Tag, hashbrown::control::tag::Tag>
    434 core::panicking::assert_failed_inner::hb42cf086ef3fa5ea
!  1101 core::slice::index::slice_start_index_len_fail::h2b0bd6f1ea36895a
   1483 core::panicking::panic_null_pointer_dereference::h455305b503f39847
!  2193 core::slice::index::slice_end_index_len_fail::h082810a57bbce7a7
   3479 core::panicking::panic_misaligned_pointer_dereference::h639314a5907ff82f
   3686 core::result::unwrap_failed::h1d408d629b4c41f6
!  9516 core::panicking::panic_bounds_check::he67b256737aac4b7
  10191 core::panicking::assert_failed::h7dbe1cbed9b3aef1
  11895 core::option::expect_failed::h35ab5df33563192c
  11923 core::option::unwrap_failed::h540db45763f4b740
  30678 core::panicking::panic_cannot_unwind::h03c30cf82c32c9e1
  30932 core::panicking::panic_fmt::h86f596f4590a5a7b
  40774 core::panicking::panic::h542f6569b46282bf
 124049 core::panicking::panic_in_cleanup::h6976e89252f67f6a
 143106 core::panicking::panic_nounwind::h4f41ec38a26ac6dc
```

To compare how big are the savings, build compiler as usual
```
$ ./x build -j12 --stage 2 compiler
```
and run
```
$ count-panics ./build/x86_64-unknown-linux-gnu/stage2/lib/librustc_driver*.so
```

Results are
  - baseline: 440483
  - bounds: 427842

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
$ for f in `find target-baseline -name *.rcgu.bc`; do ~/src/rust/llvm-tool/CountLoops $f; done > results.txt
$ grep -c 'Loop may NOT panic' results.txt
1446
$ grep -c 'Loop may panic' results.txt
132

$ RUSTFLAGS='-Csave-temps' cargo +bounds b --target-dir=target-bounds --release
$ for f in `find target-bounds -name *.rcgu.bc`; do ~/src/rust/llvm-tool/CountLoops $f; done > results.txt
$ grep -c 'Loop may NOT panic' results.txt
1501
$ grep -c 'Loop may panic' results.txt
66
```

#### Analysis for rustc

```
$ export RUSTFLAGS_NOT_BOOTSTRAP='-Csave-temps'
$ ./x build --stage 2 compiler
$ find -name '*.rcgu.bc' | xargs ~/tasks/rust/llvm-tool/CountLoops > results.txt

# Baseline
$ grep -c 'Loop may NOT panic' results.txt
35532
$ grep -c 'Loop may panic' results.txt
25915

# Bounds
$ grep -c 'Loop may NOT panic' results.txt
35773
$ grep -c 'Loop may panic' results.txt
25377
```

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

### Static estimates

We can measure how bounds checking hurts most common optimizations.

Ideally we should be able to count optimization remarks but they [do not work](https://github.com/rust-lang/rust/issues/142375)
and same goes for [compiler stats](https://github.com/rust-lang/rust/issues/142266).
So below we use `-Cllvm-args=-debug-only=...` instead.

#### Results for oxipng

Loop vectorizer:
```
$ export RUSTFLAGS='-Cllvm-args=-debug-only=loop-vectorize -Ctarget-cpu=native'
$ cargo clean
$ cargo +baseline b -j1 --release |& grep -c 'LV: Vectorizing'
85
$ cargo clean
$ cargo +bounds b -j1 --release |& grep -c 'LV: Vectorizing'
87
```

LICM:
```
$ export RUSTFLAGS='-Cllvm-args=-debug-only=licm'
$ cargo clean
$ cargo +baseline b -j1 --release |& grep -c 'LICM \(hoist\|sink\)ing'
27714
$ cargo clean
$ cargo +bounds b -j1 --release |& grep -c 'LICM \(hoist\|sink\)ing'
27957
```

GVN:
```
$ export RUSTFLAGS='-Cllvm-args=-debug-only=gvn'
$ cargo clean
$ cargo +baseline b -j1 --release |& grep -c 'GVN removed'
8508
$ cargo clean
$ cargo +bounds b -j1 --release |& grep -c 'GVN removed'
7688
```

CSE:
```
$ export RUSTFLAGS='-Cllvm-args=-debug-only=early-cse'
$ cargo clean
$ cargo +baseline b -j1 --release |& grep -c 'EarlyCSE CSE'
20820
$ cargo clean
$ cargo +bounds b -j1 --release |& grep -c 'EarlyCSE CSE'
20724
```

TODO:
  - why GVN/CSE degrade? perhaps some preceeding opts should be checked

#### Results for rustc

Warning: ~9 hours to build and log file will take several GBs

Do not forget to add to bootstrap.toml:
```
[llvm]
assertions = true
```

```
$ export RUSTFLAGS_NOT_BOOTSTRAP='-Cllvm-args=-debug-only=licm,early-cse,gvn,loop-vectorize'
$ ./x setup
$ ./x build -j1 --stage 2 compiler &> tee build.log

# Baseline
$ grep -c 'LV: Vectorizing' build.log
549
$ grep -c 'LICM \(hoist\|sink\)ing' build.log
2248327
$ grep -c 'GVN removed' build.log
798577
$ grep -c 'EarlyCSE CSE' build.log
2379907

# Bounds
$ grep -c 'LV: Vectorizing' build.log
537
$ grep -c 'LICM \(hoist\|sink\)ing' build.log
2289792
$ grep -c 'GVN removed' build.log
772504
$ grep -c 'EarlyCSE CSE' build.log
2374779
```

### Runtime improvements

#### x86_64

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

Results:
```
$ compare.py results/baseline results/bounds
oxipng_0.json: +3.9%
meilisearch_0.json: +1.6%
ruff_0.json: +1.3%
tokio_0.json: +2.5%
regex_0.json: +1.2%
bevy_0.json: +0.9%
rust_serialization_benchmark_0.json: +1.2%
nalgebra_0.json: -1.1%
rav1e_0.json: +1.8%
SpacetimeDB_0.json: +2.2%
```

TODO:
  - perf measurements for AArch64
  - PMU counters (inst count, I$/D$/branch misses) ?

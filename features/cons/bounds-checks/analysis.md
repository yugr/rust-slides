# Administrivia

Parent task: gh-20

Effort: 15h

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

TODO:
  - add info about (size) overheads in more complex examples (convolution, fibonacci)

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

TODO:
  - identify functions which contain calls to `core::panicking::panic_bounds_check` (or `core::slice::index::slice_index_order_fail`)
    * should we disable inlining ? Probably not because many BCs will not be removable after that.
  - identify loops which have branch to block with panics

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

TODO:
  - analyze optional asserts in library/core/src/ub_checks.rs
    (assert_unsafe_precondition and friends)

## Measurements

TODO:
  - collect perf measurements for benchmarks:
   * runtime
   * PMU counters (inst count, I$/D$/branch misses)
   * compiler stats
     + SLP/loop autovec for bounds checking feature
     + CSE/GVN/LICM for alias feature

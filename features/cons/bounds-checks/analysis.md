# Motivating example

URLO discussions of huge perf regressions caused by bounds checks
(also [matklad's examples](https://github.com/matklad/bounds-check-cost/blob/master/src/main.rs))
date back for pre 2020-s times.

LLVM optimizer has significantly improved since then.
All loops that do simple `0..n`-like iterations (`f1`-`f4`, `f7`) optimize well
i.e. checks are removed from loops and loops are vectorized.

More complex examples that require non-trivial arithmetic still break optimizer
(e.g. `f5` or `f6`).

TODO:
  - more examples where checks are not removed
  - also check `Vec`

# Optimizations

TODO:
  - info whether LLVM can potentially optimize it (and with what limitations)

# Workarounds for bounds checks

TODO:
  - info on how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all

# Analysis of real code

TODO:
  - info on whether this error is a common case in practice
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences

# Suggested reading

TODO:
  - links to important articles

# Performance impact

## Disabling the check

Compiler patch is in branch yugr/disable-bounds-checks/1 .
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
  - analyze optional asserts in library/core/src/ub_checks.rs (assert_unsafe_precondition and friends)
  - verify no bounds checks for `a[i]`, `a[i..j]`, `a[i..=j]` for arrays, slices, string slices, Vecs, Strings

## Analyzing projects

TODO:
  - collect perf measurements for benchmarks:
   * runtime
   * PMU counters (inst count, I$/D$/branch misses)
   * compiler stats
     + SLP/loop autovec for bounds checking feature
     + CSE/GVN/LICM for alias feature

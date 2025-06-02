Need to
  - disable checks in compiler
  - remove relevant `panic!` / `assert!` / etc. in stdlib

For compiler patch from https://blog.readyset.io/bounds-checks seems to be enough.
There is also some code in compiler/rustc_index (vec.rs, slice.rs, etc.)
but these seem to be custom containers/wrappers (no additional checks).

Two relevant parts of stdlib are library/alloc and library/core.
In particular need to scan
  - arrays (library/core/src/array) :
    * what to do about `split_array_ref/mut` and `rsplit_array_ref/mut` (add `Option::unsafe_unwrap` ?)
  - slices:
    * library/core/src/slice
      + removed all relevant asserts
    * library/alloc/src/slice.rs
      + high-level APIs without panics
  - strs:
    * library/core/src/str
      + updated `index` and `index_mut` in `str/traits.rs`
      + otherwise only char boundary checks
    * library/alloc/src/str.rs
      + high-level APIs without panics
  - Vec (library/alloc/src/vec)
  - String (library/alloc/src/string.rs)
  - ptrs (library/core/src/ptr)
  - ranges (library/core/src/range.rs and other range.rs files in core)
for `panic!\|\<assert!\|unreachable!\|_fail[a-z_]*(\|\.unwrap(\|\.expect(` and patch if needed.

TODO:
  - analyze optional asserts in library/core/src/ub_checks.rs (assert_unsafe_precondition and friends)
  - verify no bounds checks for `a[i]`, `a[i..j]`, `a[i..=j]` for arrays, slices, string slices, Vecs, Strings

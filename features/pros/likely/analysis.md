# Administrivia

Assignee: yugr

Parent task: gh-48

Effort: 2h

TODO:
  - fix all TODOs that are mentioned in feature's README

# Background

Rust provides several means for assigning frequencies.
The basic one is function attribute:
```
#[cold]
pub const fn foo() {}
```
It's used in many places in stdlib:
  - mark allocating or panicking code in `Vec`, slice, `String`, `&str`
  - incorrect borrows in `RefCell`
  - panics routines
  - expect/unwrap fails in `Option` and `Result`
  - `strict_XXX` APIs

Unstable intrinsics `std::intrinsics::{likely, unlikely, cold_path}`
are built on top of `#[cold]` (also reexported as `std::hint::{likely, unlikely, cold_path}`).
They are used in some places in stdlib:
  - mark fails (`Rc`)
  - mark overflows (`checked_XXX`, `StepBy` and `Slip` iterators`)

`cold_path` is useful for match statements.
Most likely intrinsics will be stabilized ([#136873](https://github.com/rust-lang/rust/issues/136873)).

Codegen additionally marks blocks as cold if all their succs are cold.

GCC/Clang have `__builtin_expect` intrinsic to mark likely branch
and recent C++ has `[[likely]]` annotations.
GCC uses them for `std::expected`:
```
constexpr _Tp&
value() &
{
  if (_M_has_value) [[likely]]
    return _M_val;
  _GLIBCXX_THROW_OR_ABORT(bad_expected_access<_Er>(_M_unex));
}
```
`std::optional` and `std::vector::at` do not have this
but the failing part of method ends with call to `abort`
(or another `noreturn` function) or `throw` and
LLVM is clever enough to infer low probability for it.

TODO:
  - apply_attrs_to_cleanup_callsite ?
  - why is this feature needed ?
    * enabled by default and why
    * situation in other langs:
      + [Java](https://docs.oracle.com/javase/specs/jls/se24/html/),
      + [C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/introduction)
      + [Go](https://go.dev/ref/spec)
      + [Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/aboutthelanguagereference/)
      + [Fortran](https://j3-fortran.org/doc/year/24/24-007.pdf)
      + Ada ([RM](http://www.ada-auth.org/standards/22rm/html/RM-TOC.html) and [ARM](http://www.ada-auth.org/standards/22aarm/html/AA-TOC.html))
      + [Julia](https://docs.julialang.org)
  - (need to collect prooflinks with timecodes, reprocases for everything)

# Example

TODO:
  - example errors/opt which are caught by this check
  - clear example (Rust microbenchmark, asm code)

# Optimizations

TODO:
  - types of check (e.g. compiler/stdlib parts)
  - info whether LLVM can potentially optimize it (and with what limitations)

# Workarounds

TODO:
  - info on how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all

# Suggested readings

TODO:
  - links to important articles (design, etc.)

# Performance impact

## Prevalence

TODO:
  - is this check is a common case in practice ?
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences

## Disabling the check

TODO:
  - determine how to enable/disable feature in compiler/stdlib
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      + patch for each feature needs to be implemented in separate branch (in private compiler repo)
      + compiler modifications need to be kept in private compiler repo `yugr/rust-private`
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`

## Measurements

TODO:
  * collect perf measurements for benchmarks:
    + runtime
    + code size (if applicable)
    + compiler stats
      - depend on feature
      - e.g. SLP/loop autovec for bounds checking feature
      - e.g. NoAlias returns from AA manager for alias feature
      - e.g. CSE/GVN/LICM for alias feature


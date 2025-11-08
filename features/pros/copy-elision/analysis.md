# Administrivia

Assignee: yugr

Parent task: gh-32

Effort: 0h

TODO: fix all TODOs that are mentioned in feature's README

# Background

TODO:
  - why is this feature needed ?
    * example errors which are caught by this check
    * enabled by default and why
    * situation in C/C++
      + e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
      + e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
    * situation in other langs:
      + [Java](https://docs.oracle.com/javase/specs/jls/se24/html/),
      + [C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/introduction)
      + [Go](https://go.dev/ref/spec)
      + [Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/aboutthelanguagereference/)
      + [Fortran](https://j3-fortran.org/doc/year/24/24-007.pdf)
      + Ada ([RM](http://www.ada-auth.org/standards/22rm/html/RM-TOC.html) and [ARM](http://www.ada-auth.org/standards/22aarm/html/AA-TOC.html))
      + [Julia](https://docs.julialang.org)
  - types of check (e.g. compiler/stdlib parts)

# Examples

TODO:
  - clear example (Rust microbenchmark, asm code)

# Optimizations

TODO:
  - info whether LLVM can potentially optimize it (and with what limitations)

# Workarounds

TODO:
  - info on how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all

# Suggested reading

TODO:
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)

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
  - collect perf measurements for benchmarks:
    * runtime
    * code size
    * standard compiler stats (inline, CSE/GVN/LICM, SLP/loop autovec)

# Administrivia

Assignee: zak

Parent task: gh-57

Effort: 0h

TODO:
  - fix all TODOs that are mentioned in feature's README

# Background

TODO:
  - why is this feature needed ?
    * example cases which are optimized by niche and struct reorg
    * benefits (better D$ utilization)
    * situation in C/C++
      + struct reorg opt in GCC and Clang (by Golovanevsky Olga)
      + e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
      + e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
    * situation in other langs:
      + [Java](https://docs.oracle.com/javase/specs/jls/se24/html/),
      + [C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/introduction)
      + [Go](https://go.dev/ref/spec)
      + [Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/aboutthelanguagereference/)
      + [Fortran](https://j3-fortran.org/doc/year/24/24-007.pdf)
      + Ada ([RM](http://www.ada-auth.org/standards/22rm/html/RM-TOC.html) and [ARM](http://www.ada-auth.org/standards/22aarm/html/AA-TOC.html))
  - types of optimizations (niche via fields, niche via ranges, struct reorg)
  - consequences (lack of stable ABI)

# Examples

TODO:
  - clear example (Rust microbenchmark, asm code)

# Optimizations

# Workarounds

TODO:
  - info on how developer can disable this optimization

# Suggested reading

TODO:
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)

# Performance impact

## Prevalence

TODO:
  - is this check is a common case in practice ?
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences

## Disabling the opt

TODO:
  - determine how to disable opts in compiler
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      + patch for each feature needs to be implemented in separate branch (in private compiler repo)
      + compiler modifications need to be kept in private compiler repo `yugr/rust-private`
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`

## Measurements

TODO:
  - collect perf measurements for benchmarks:
    * runtime
      + large unexpected changes need to be investigated
    * code size (if applicable)
    * compiler stats (if applicable)
      + depend on feature
      + LLVM stats may be misleading because some opts (e.g. inline) are done in frontend
        (at MIR level). But recollecting with `-Zmir-opt-level=0`
        e.g. in panic feature didn't improve anything.
      + e.g. SLP/loop autovec for bounds checking feature
      + e.g. NoAlias returns from AA manager for alias feature
      + e.g. CSE/GVN/LICM for alias feature

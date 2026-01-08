# Administrivia

Assignee: yugr

Parent task: gh-38

Effort: 2h

# Background

Rust stdlib tends to be more safe i.e. performs more checks (`assert!`, etc.)
than that of C/C++.  For example Rust default PRNG is of higher quality but slower.
Also Rust IO is unbuffered (and thus much slower) by default.

There are also many complaints on Rust iterators
as compiler (often ?) fails to optimize complex adapter combinations
(e.g. [#80416](https://github.com/rust-lang/rust/issues/80416)).

In general stdlib safety checks can be identified via
```
$ grep 'panic!\|\<assert!\|unreachable!' core alloc \
  | grep '\.rs' \
  | grep -v '\/\/\/\|test\|static_assert\|#\['
```
(this is oversimplification because some checks are hidden in
`checked_XXX` and `unwrap` APIs).

A lot of APIs in stdlib check that indexes are within bounds and do not overflow.
E.g. see asm generated for `Vec`
[here](https://github.com/Shnatsel/bounds-check-cookbook/blob/main/src/bin/fibvec_clever_indexing.rs):
there are _two_ overflow checks (that `size` does not exceed `isize::MAX` and
`size * elem_size` does not overflow). Also `capacity_overflow` in `raw_vec/mod.rs`.
Index checks are handled in [dedicated feature](../bounds-checks).

Also counter and capacity overflows panic
  - alloc/src/collections/vec_deque/{mod.rs,spec_extend}.rs
  - alloc/src/slice.rs
  - alloc/src/rc.rs
  - alloc/src/sync.rs
  - alloc/src/raw_vec/mod.rs
  - alloc/src/vec/{mod,spec_from_iter_nested}.rs
  - core/src/cell.rs
  - core/src/slice/index.rs
  - core/src/str/traits.rs

(counter checks are handled in [dedicated feature](../arithmentic-checks)).

There are also checks for much rarer errors e.g.
  - memory allocation errors panic
    * CWE-770 and children (no KEV and 17 CVEs out of 33K total, out of 4.5K memory errors in 2024):
    * relevant files: alloc/src/alloc.rs
  - UTF-8 invariant checks for `String`s
    * CWE-173 and CWE-838 (no KEVs and just 3 CVEs out of 33K total in 2024).
    * relevant files: `alloc/src/string.rs` and `core/src/str/mod.rs`
    * makes code slower compared to C strings and C++ `std::string`

Finally there are some API-specific misuse checks (e.g. for `Cell` or
iterator adapters or alignment checks in core/src/ptr or
comparator checks in `core/src/slice/sort`).

TODO:
  - situation in C/C++
    * e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
    * e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
  - situation in other langs:
    * [Java](https://docs.oracle.com/javase/specs/jls/se24/html/),
    * [C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/introduction)
    * [Go](https://go.dev/ref/spec)
    * [Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/aboutthelanguagereference/)
    * [Fortran](https://j3-fortran.org/doc/year/24/24-007.pdf)
    * Ada ([RM](http://www.ada-auth.org/standards/22rm/html/RM-TOC.html) and [ARM](http://www.ada-auth.org/standards/22aarm/html/AA-TOC.html))

# Examples

Example of invalid Unicode detection:
```
$ cat tmp36.rs
use std::io;

fn main() {
    let mut input = String::new();
    io::stdin().read_line(&mut input).unwrap();
    println!("{}", input);
}

$ echo Привет | ./tmp36
Привет

$ echo Привет | iconv -f UTF-8 -t KOI8-RU | ./tmp36
thread 'main' panicked at tmp36.rs:5:39:
called `Result::unwrap()` on an `Err` value: Error { kind: InvalidData, message: "stream did not contain valid UTF-8" }
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

# Optimizations

TODO:
  - info whether LLVM and MIR opts can potentially optimize it (and with what limitations)

# Workarounds

There is no way to avoid these checks.

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

## Measurements

TODO:
  - determine how to enable/disable feature in compiler/stdlib
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      + patch for each feature needs to be implemented in separate branch (in private compiler repo)
      + compiler modifications need to be kept in private compiler repo `yugr/rust-private`
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`

### Static estimates

TODO:
  - compiler stats
    * depend on feature
    * LLVM stats may be misleading because some opts (e.g. inline) are done in frontend
      (at MIR level). But recollecting with `-Zmir-opt-level=0`
      e.g. in panic feature didn't improve anything.
    * e.g. SLP/loop autovec for bounds checking feature
    * e.g. NoAlias returns from AA manager for alias feature
    * e.g. CSE/GVN/LICM for alias feature

### Runtime improvements

TODO:
  - benchmark disabling of invariant checks in `String`
  - benchmark disable of checks in `Option::unwrap` and `Option::expect` (?)
  - compare against similar features in hardened C++
  - collect perf measurements for benchmarks:
    * runtime
      + large unexpected changes need to be investigated
    * code size (if applicable)

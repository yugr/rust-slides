# Administrivia

Assignee: yugr

Parent task: gh-38

Effort: 4.5h

# Background

Rust stdlib tends to be more safe i.e. performs more checks (`assert!`, etc.)
than that of C/C++.  For example Rust default PRNG is of higher quality but slower.
Also Rust IO is unbuffered (and thus much slower) by default
and `io::stdout()` is line-buffered even for non-TTY outputs
(details in [README](README.md)).

There are also many complaints on Rust iterators
as compiler (often ?) fails to optimize complex adapter combinations
(e.g. [#80416](https://github.com/rust-lang/rust/issues/80416)).

In general stdlib safety checks can be identified via
```
$ grep 'panic!\|\<assert!\|unreachable!\|\<checked_\(add\|sub\|mul\).*\(expect\|unwrap\)\|strict_\(add\|sub\|mul\)' core alloc \
  | grep '\.rs' \
  | grep -v '\/\/\/\|test\|#\['
```
(this is oversimplification because some checks are hidden in
`unwrap`/`expect` APIs, explicit checks against `usize::MAX`, etc.).

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
  - core/src/slice/{index,mod}.rs
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

C/C++ stdlibs also have some optional debug checks
but each distro decides whether to enable them
(via controlling macros like `-D_GLIBCXX_ASSERTIONS` or `-DNDEBUG`,
there is also `-D_GLIBCXX_DEBUG` but it's considered too heavy for production).
C is less safe than C++ e.g. `malloc` will return `NULL` on OOM
rather than crash (like `operator new` or failed container allocations in C++).
Recent trend in C++ is enabling more sanity checks in STL
(so called "security hardening").
C provides some indexing checks under `-D_FORTIFY_SOURCE=2`
and C++ with `-D_GLIBCXX_ASSERTIONS`.
C++ does not provide as rich support for Unicode as Rust
in its `std::u8string` and thus does perform similar UTF-8 boundary checks.

TODO:
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
$ cat test.rs
use std::io;

fn main() {
    let mut input = String::new();
    io::stdin().read_line(&mut input).unwrap();
    println!("{}", input);
}

$ echo Привет | ./test
Привет

$ echo Привет | iconv -f UTF-8 -t KOI8-RU | ./test
thread 'main' panicked at test.rs:5:39:
called `Result::unwrap()` on an `Err` value: Error { kind: InvalidData, message: "stream did not contain valid UTF-8" }
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

# Optimizations

There are too many opts to give definite answer but
it's unlikely that compiler can optimize OOMs or (non-constant) String checks.

# Workarounds

There is no way to avoid these checks (without changing stdlib code).

# Suggested reading

N/A

# Performance impact

I added branches which disable checks which are
supposedly high overhead but rare in practice:
  - size/counter overflows: [yugr/stdlib/no-overflow-checks/2](https://github.com/yugr/rust-private/tree/yugr/stdlib/no-overflow-checks/2)
  - char boundary checks: [yugr/stdlib/no-char-checks/2](https://github.com/yugr/rust-private/tree/yugr/stdlib/no-char-checks/2)

TODO:
  - ensure that `ub_checks::assert_unsafe_precondition!` are disabled
    (should be no check before call to `fmt` in
    `<alloc::string::String as core::fmt::Display>::fmt`)

## Prevalence

We use the same apporoach as in [bound checks](../bounds-checks/analysis.md#prevalence):
build compiler as usual
```
$ ./x build -j12 --stage 2 compiler
```
and run
```
$ count-panics ./build/x86_64-unknown-linux-gnu/stage2/lib/librustc_driver*.so
```

Results are
  - baseline: 440495
  - no-char-checks: 440144 (0.1%)
  - no-overflow-checks: 436329 (1%)

TODO:
  - rebuild rustc w/ `debug-assertions=false` and recollect data

## Measurements

### Static estimates

```
$ ./x build --stage 1 compiler
$ RUSTFLAGS_NOT_BOOTSTRAP='-Cllvm-args=-debug-only=inline,licm,early-cse,gvn,loop-vectorize,SLP' ./x build -j1 --stage 2 compiler &> build.log

# Baseline
$ grep -c 'Size after inlining' build.log
2533754
$ grep -c 'LV: Vectorizing' build.log
549
$ grep -c 'LICM \(hoist\|sink\)ing' build.log
2248947
$ grep -c 'GVN removed' build.log
798566
$ grep -c 'EarlyCSE CSE' build.log
2380605
$ grep -c 'SLP: vectorized' build.log
25065

# No char checks
$ grep -c 'Size after inlining' build.log
2532992
$ grep -c 'LV: Vectorizing' build.log
545
$ grep -c 'LICM \(hoist\|sink\)ing' build.log
2241138
$ grep -c 'GVN removed' build.log
795817
$ grep -c 'EarlyCSE CSE' build.log
2380456
$ grep -c 'SLP: vectorized' build.log
25038

# No overflow checks
$ grep -c 'Size after inlining' build.log
2498914
$ grep -c 'LV: Vectorizing' build.log
602
$ grep -c 'LICM \(hoist\|sink\)ing' build.log
2233869
$ grep -c 'GVN removed' build.log
780245
$ grep -c 'EarlyCSE CSE' build.log
2328470
$ grep -c 'SLP: vectorized' build.log
25113
```

So 10% more loops vectorized without overflow checks
otherwise small and meaningless diffs.

TODO: recollect with `debug-assertions = false`

### Runtime improvements

TODO:
  - collect perf measurements for benchmarks:
    * runtime
      + large unexpected changes need to be investigated
    * code size (if applicable)

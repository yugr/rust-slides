# Administrivia

Assignee: yugr

Parent task: gh-36

Effort: 4h

TODO:
  - fix all TODOs that are mentioned in feature's README

# Background

Any error in program, either detected by compiler or forced by programmer via
`panic!`, `unreachable!`, `assert!`, `unimplemented!` or `Option::unwrap`,
by default is handled by unwindint the stack, calling destructors (drops) in each frame,
until either `catch_unwind` is found or we reach ToS. In the latter case
detailed error message (and, with `RUST_BACKTRACE` set, backtrace)
is printed and program is aborted.

Unwinding is a very slow process as it involves parsing the unwind tables
which is effectively bytecode interpretation
(many people argue that it could be done faster)
so _usually_ shouldn't be relied on in normal code.
Normal Rust error handling should use error codes (`Option` and `Result`,
C++ P0709 zero-overhead exceptions are like this).

TODO:
  - exceptions may [reduce code size](https://www.youtube.com/watch?v=LorcxyJ9zr4)
    (because error checking is no longer needed)
  - citations about faster unwinding
  - using exceptions to replace _very rare_ error codes
    to improve performance by avoiding checks

Panics are very similar to C++ exceptions, both logically and internally
(Rust panics use same mechanisms in LLVM e.g. `invoke` and landing pads).
Rust is actually more aggressive than C++ because panics in destructors are
allowed (controlled via `-Z panic-in-drop=abort` option).

Rust needs to insert landing pads for all function calls
that may unwind:
  - Rust functions with panics or which call functions that may panic
    * TODO: does Rust know unwind status for functions from other crates ?
  - `extern "C++"` (but not `extern "C"`)

Panic handling have certain costs:
  - binary size for unwind tables (`.eh_frame`), landing pads,
    panic messages
    * landing pads are needed only for functions with destructors
      + TODO: how many functions are such ?
    * panic messages are needed only for functions with checks
      (but those are majority)
  - wasted I$ and RAM
  - disabled optimizations
    (based on [Roman's talk](https://www.youtube.com/watch?v=ItemByR4PRg)):
    * mainly hurts inlining
    * a lot of cut-offs in other passes (e.g. ADCE)

What's worse, these costs are enabled even if panics never fire in program
so they are NOT zero-cost abstractions.

TODO: 
  - code bloat in [here](https://www.rottedfrog.co.uk/?p=24)
  - strong arguments for exceptions resulting in smaller code size:
    https://www.youtube.com/watch?v=BGmzMuSDt-Y

To work around them we have `-C panic=abort` which is similar to `-fno-exceptions`
(`-fno-exceptions` is enabled in many high-performance codebases e.g. LLVM,
[50% codebases disable it](https://accu.org/conf-docs/PDFs_2019/herb_sutter_-_de-fragmenting_cpp__making_exceptions_more_affordable_and_usable.pdf)
(also [CppCon talk](https://www.youtube.com/watch?v=ARYP83yNAWk))
and e.g. Google C++ Code Style [prohibits it](https://google.github.io/styleguide/cppguide.html#Exceptions)).
It allows the following codegen optimizations:
```
/// * Calling a function which can't unwind means codegen simply ignores any
///   associated unwinding cleanup.
/// * Calling a function which can unwind from a function which can't unwind
///   causes the `abort_unwinding_calls` MIR pass to insert a landing pad that
///   aborts the process.
/// * This affects whether functions have the LLVM `nounwind` attribute, which
///   affects various optimizations and codegen.
```
(from `fn_can_unwind`) and also completely removes unwind tables.

There is one thing this flag does not disable:
program still will contains significant amount of code to emit
a user-friendly error message for panic.

TODO:
  - can we force a simple single `ud2` for the whole program,
    both for compiler-generated and user panics ?
  - will hot-cold splitting help and how to enable ?
  - error handling in other languages:
    * C/C++
      + e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
      + e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
    * [Java](https://docs.oracle.com/javase/specs/jls/se24/html/),
    * [C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/introduction)
    * [Go](https://go.dev/ref/spec)
    * [Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/aboutthelanguagereference/)
    * [Fortran](https://j3-fortran.org/doc/year/24/24-007.pdf)
    * Ada ([RM](http://www.ada-auth.org/standards/22rm/html/RM-TOC.html) and [ARM](http://www.ada-auth.org/standards/22aarm/html/AA-TOC.html))
    * [Julia](https://docs.julialang.org)

# Example

Optimized asm for this simple code
```
#[inline(never)]
pub fn bar(x: &mut Vec<i32>) {
    std::hint::black_box(x);
}

#[no_mangle]
pub fn foo(mut x: Vec<i32>) {
    bar(&mut x);
}
```
takes 93 bytes and 38 of them are due to exceptions.
Compiling without panics (`-Cpanic=abort`) gives just 40 bytes.

# Optimizations

Landing pads from nested blocks reuse landing pads for outer blocks
(so there is no `O(N^2)` code size). E.g. this
```
#[inline(never)]
pub fn bar1(x1: &mut Vec<i32>) {
    std::hint::black_box(x1);
}

#[inline(never)]
pub fn bar2(x1: &mut Vec<i32>, x2: &mut Vec<i32>) {
    std::hint::black_box(x1);
    std::hint::black_box(x2);
}

#[inline(never)]
pub fn bar3(x1: &mut Vec<i32>, x2: &mut Vec<i32>, x3: &mut Vec<i32>) {
    std::hint::black_box(x1);
    std::hint::black_box(x2);
    std::hint::black_box(x3);
}

#[no_mangle]
pub fn foo1() {
    let mut x1 = vec![1, 2, 3];
    bar1(&mut x1);
}

#[no_mangle]
pub fn foo2() {
    let mut x1 = vec![1, 2, 3];
    bar1(&mut x1);
    let mut x2 = vec![1, 2, 3];
    bar2(&mut x1, &mut x2);
}

#[no_mangle]
pub fn foo3() {
    let mut x1 = vec![1, 2, 3];
    bar1(&mut x1);
    let mut x2 = vec![1, 2, 3];
    bar2(&mut x1, &mut x2);
    let mut x3 = vec![1, 2, 3];
    bar3(&mut x1, &mut x2, &mut x3);
}
```
has the following combined landing pad for `foo3`:
```
  movq  %rax, %rbx
  movq  48(%rsp), %rsi
  testq %rsi, %rsi
  je  .LBB5_9
  movq  56(%rsp), %rdi
  shlq  $2, %rsi
  movl  $4, %edx
  callq *_RNvCs1EfgSJrSbwZ_7___rustc14___rust_dealloc@GOTPCREL(%rip)
  jmp .LBB5_9
.LBB5_8:
.Ltmp20:
  movq  %rax, %rbx
.LBB5_9:
  movq  24(%rsp), %rsi
  testq %rsi, %rsi
  je  .LBB5_5
  movq  32(%rsp), %rdi
  shlq  $2, %rsi
  movl  $4, %edx
  callq *_RNvCs1EfgSJrSbwZ_7___rustc14___rust_dealloc@GOTPCREL(%rip)
  jmp .LBB5_5
.LBB5_4:
.Ltmp23:
  movq  %rax, %rbx
.LBB5_5:
  movq  (%rsp), %rsi
  testq %rsi, %rsi
  je  .LBB5_7
  movq  8(%rsp), %rdi
  shlq  $2, %rsi
  movl  $4, %edx
  callq *_RNvCs1EfgSJrSbwZ_7___rustc14___rust_dealloc@GOTPCREL(%rip)
.LBB5_7:
  movq  %rbx, %rdi
  callq _Unwind_Resume@PLT
```
(landing pads of inner blocks jump to outer landing pads).

TODO:
  - info whether LLVM can potentially optimize it (and with what limitations)

# Workarounds

TODO:
  - info on how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all

# Suggested readings

TODO:
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)

# Performance

TODO:
  - performance impact:
    * is this check is a common case in practice ?
      + may need to write analysis passes to scan real Rust code (libs, big projects) for occurences
    * determine how to enable/disable feature in compiler/stdlib
      + there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
        - patch for each feature needs to be implemented in separate branch (in private compiler repo)
        - compiler modifications need to be kept in private compiler repo `yugr/rust-private`
      + make sure that found solution works on real examples
      + note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`
    * collect perf measurements for benchmarks:
      + runtime
      + PMU counters (inst count, I$/D$/branch misses)
        - actually we failed to understand how to collect PMUs in benchmarks (gh-25)...
      + compiler stats
        - depend on feature
        - inliner improvements
        - e.g. SLP/loop autovec for bounds checking feature
        - e.g. NoAlias returns from AA manager for alias feature
        - e.g. CSE/GVN/LICM for alias feature
    * at least x86/AArch64
      + maybe also normal/ThinLTO/FatLTO, cgu=default/1 in future if we have time

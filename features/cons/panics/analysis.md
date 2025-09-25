# Administrivia

Assignee: yugr

Parent task: gh-36

Effort: 27h

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

Panics are very similar to C++ exceptions, both logically and internally
(Rust panics use same mechanisms in LLVM e.g. `invoke` and landing pads).
Rust is actually more aggressive than C++ because panics in destructors are
allowed (controlled via `-Z panic-in-drop=abort` option).

Rust needs to insert landing pads for all function calls
that may unwind:
  - Rust functions with panics or which call functions that may panic
    (note that Rust knows unwind status for functions from other crates,
    see `codegen_fn_attrs` in `compiler/rustc_metadata`;
    this is a notable improvement compared to C++ which can NOT know
    this at compile time if `noexcept`'s are missing)
  - `extern "C-unwind"` but not `extern "C"`
    (e.g. see [this](https://www.rottedfrog.co.uk/?p=24))

Panic handling have certain costs,
similar to C++ exceptions (on which machinery Rust panics are built upon):
  - binary size for unwind tables (`.eh_frame`), landing pads,
    panic messages
    * landing pads are needed only for functions with destructors
      or nounwind functions with potentially panicking callees
    * panic messages are needed only for functions with checks
      (but those are majority)
    * panic messages can be made cheaper by using `-Z location-detail=none`
      (which will remove filename strings from binary)
    * [here](https://www.youtube.com/watch?v=BGmzMuSDt-Y) Khalil Estell (@kammce)
      argues that exceptions can actually save code space by avoiding code for
      error handling (but measurements only for microbenchmarks)
  - wasted I$ and RAM
  - disabled optimizations
    (based on [Roman's talk](https://www.youtube.com/watch?v=ItemByR4PRg)
    which is LLVM-based so also applicable):
    * mainly hurts inlining
    * a lot of cut-offs in other passes (e.g. ADCE)

What's worse, these costs are enabled even if panics never fire in program
so they are NOT zero-cost abstractions.

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
To achieve that we can recompile stdlib with
`-Zbuild-std-features=panic_immediate_abort`
(see example [here](https://github.com/microsoft/edit/blob/7338c3cbbc99c1366d556d631402cdd853d989bd/Cargo.toml),
maybe `-Zbuild-std` is needed too).

In some rare cases exceptions my make code faster by removing error handling code
(see [README](README.md#advantages-of-panics) for details).

Error handling approaches in other languages are different.
Go is similar to Rust: exceptions exist (`panic` + `recover`) but
not used for "normal" error handling.
In Java and C# exceptions are the idiomatic way of error handling
(they are also handled more efficiently there due to lack of dtors,
often begin a single jump within inlined method).
Swift does not have any exception-like unwinding,
just syntax sugared return codes.

TODO:
  - (LOW) check if C++ also has same overhead due to exceptions: https://www.rottedfrog.co.uk/?p=24
    * if not, we need a slide on this...

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

There is not much LLVM or MIR can do about landing pads
(except simplifying trivial and merging in SimplifyCFG)
and they can hurt efficiency of various passes as shown in
[Roman's talk](https://www.youtube.com/watch?v=ItemByR4PRg).

TODO:
  - (LOW) does MachineBlockPlacement always place code at the end of function ?
    this would help I$ as well

# Workarounds

Info available in [README](README.md#solutions).

# Suggested readings

[No-panic Rust](https://blog.reverberate.org/2025/02/03/no-panic-rust.html)

[You might want to use panics for error handling](https://purplesyringa.moe/blog/you-might-want-to-use-panics-for-error-handling/)

[Error codes are far slower than exceptions](https://web.archive.org/web/20230605115838/https://lordsoftech.com/programming/error-codes-are-far-slower-than-exceptions/)

# Performance impact

## Prevalence

Here is LLVM IR panics statistics in Rust compiler:
```
$ RUSTFLAGS_NOT_BOOTSTRAP=-Csave-temps ./x build -j12 --stage 2 compiler
$ find -name '*.rcgu.bc' | xargs ~/tasks/rust/count-panic-stats/Count > results.txt

# Insn stats
$ cat results.txt | awk '/all insns/{s += $NF} END{print s}'
14852456
$ cat results.txt | awk '/calls/{s += $NF} END{print s}'
1870448
$ cat results.txt | awk '/invokes/{s += $NF} END{print s}'
1850321
$ cat results.txt | awk '/panics/{s += $NF} END{print s}'
546167
$ cat results.txt | awk '/panic handling insns/{s += $NF} END{print s}'
1481282
$ cat results.txt | awk '/unwind insns/{s += $NF} END{print s}'
963937
$ cat results.txt | awk '/PANIC.UNWIND insns/{s += $NF} END{print s}'
1979710

# BB stats
$ cat results.txt | awk '/all blocks/{s += $NF} END{print s}'
3277100
$ cat results.txt | awk '/panic handling blocks/{s += $NF} END{print s}'
526448
$ cat results.txt | awk '/unwind blocks/{s += $NF} END{print s}'
371158
$ cat results.txt | awk '/PANIC.UNWIND blocks/{s += $NF} END{print s}'
742214
```

Some conclusions:
  - practically 50% of calls are invokes (for rest compiler is
    _probly_ able to infer that they don't panic)
  - 10% (1481282 / 14852456) of ALL insns and 16% (526448 / 3277100) of ALL blocks are handling panics
  - 6.5% (963937 / 14852456) of ALL insns and 11% (371158 / 3277100) of ALL blocks are landing pads
  - 13% (1979710 / 14852456) of ALL insns and 23% (742214 / 3277100) of ALL blocks are handling panics OR landing pads

## Disabling the check

To compare overhead of exceptions we measure several variants:
  - (A) forced `-Cpanic=abort` ([yugr/force-panic-abort/1](https://github.com/yugr/rust-private/tree/yugr/force-panic-abort/1) branch)
  - (B) = (A) + build stdlib with `panic_immediate_abort` ([yugr/force-panic-immediate-abort/1](https://github.com/yugr/rust-private/tree/yugr/force-panic-immediate-abort/1) branch)
  - (C1) and (C2): A + outlining landing pads (to improve I$ locality) ([yugr/enable-hot-cold-splitting/1](https://github.com/yugr/rust-private/tree/yugr/enable-hot-cold-splitting/1) and [yugr/enable-machine-splitter/1](https://github.com/yugr/rust-private/tree/yugr/enable-machine-splitter/1) branches)

(A) removes landing pads for non-FFI (Rust) functions.

(B) removes most panics: panic calls in librustc_driver.so
reduce _roughly_ by 98%:
```
# This may be a bit cynical...
$ objdump -d build/x86_64-unknown-linux-gnu/stage1/lib/librustc_driver-033b48a87851ef3e.so > librustc.d
$ grep -c 'call.*panic' librustc.d

# baseline
352905

# force-panic-immediate-abort
7828
```

The reason for remaining panics is that some standard APIs,
most notably slices and cells, do not respect `panic_immediate_abort`:
```
$ cat librustc.d | sed -ne '/call.*panic/{s/^[^<]*<\(.*\)@@.*/\1/; p}' | sort | uniq -c | sort -rnk1 | head
   2416 core::slice::index::slice_end_index_len_fail::do_panic::runtime
   1282 core::cell::panic_already_borrowed
   1022 core::slice::index::slice_start_index_len_fail::do_panic::runtime
    929 std::thread::local::panic_access_error
    532 core::cell::panic_already_mutably_borrowed
    405 core::slice::index::slice_index_order_fail::do_panic::runtime
    209 <rustc_serialize::opaque::FileEncoder>::panic_invalid_write::<10>
     87 std::panic::resume_unwind
     47 core::slice::<impl [T]>::copy_from_slice::len_mismatch_fail::do_panic::runtime
     45 <rustc_serialize::opaque::FileEncoder>::panic_invalid_write::<8>
```
So even with (B) not all panics are removed. Shame on stdlib !

I also checked that (B) actually removes panic/unwind code
in the following most common cases:
  - `unreachable!`, `unimplemented!`, `todo!`, `panic!` (works)
  - `Option::unwrap`, `Option::expect`, `Result` (works)
  - Vec allocation e.g. `__rust_alloc` (works)
  - call FFI functions with C ABI
    * note that C-unwind ABI still needs a landing pad
  - https://news.ycombinator.com/item?id=30867188 (works)

For (C) there 2 options:
  - HotColdSplitting:
    * middle-end pass that outlines to separate functions
      + increases code size and [not necessarily a win](https://llvm.org/devmtg/2019-10/slides/Kumar-HotColdSplitting.pdf)
    * similar to Rust's manual approach to separate cold code to funcs
    * off by default, enabled via `-Cllvm-args="-hot-cold-split -enable-cold-section"`
    * outlines both landing pads and explicit panics
  - MachineFunctionSplitter:
    * back-end pass that outlines individual blocks
    * based on basic block sections feature
    * off by default, enabled via `-enable-split-machine-functions -mfs-split-ehcode`
    * outlines only landing pads (not explicit panics, needs PGO for them)
  - (there is also MachineOutliner but it outlines repeated, not cold, code)

## Measurements

TODO:
  - runtime
    * can only be done in benches w/o `catch_unwind` (in bench itself and deps)
  - code+rodata size
  - compiler stats
    * depend on feature
    * inliner improvements
    * stack usage
    * e.g. SLP/loop autovec for bounds checking feature
    * e.g. NoAlias returns from AA manager for alias feature
    * e.g. CSE/GVN/LICM for alias feature

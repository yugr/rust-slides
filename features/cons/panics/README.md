All info about performance overhead of panics.

Note that `unreachable!`, `assert!` and `unimplemented!`
all panic internally.

Panics involve stack unwinding and destructors so are definitely not free.
E.g. they complicate compiler analyses due to presence of landing pads.

Panicking causes significant code bloat in small functions (e.g. [here](https://www.rottedfrog.co.uk/?p=24)).

It's not clear how they influence performance (or whether they do at all).
Note that exceptions may actually be _beneficial_ for performance
because no BTB is wasted on error handling code (see below).

Panics make leaf functions no longer leaf (see [this](https://www.reddit.com/r/programming/comments/2po703/comment/cmym6jk/))
which may harm optimizations (e.g. inlining) and introduce unnecessary reg spills.

# Prevalence

Based on stage 2 Rust compiler:
```
$ objdump -rd build/x86_64-unknown-linux-gnu/stage2/lib/librustc_driver*.so | c++filt | rustfilt > librustc_driver.d
$ grep 'call.*\(unwrap_failed\|expect_failed\|assert_failed\|slice_.*_fail\|core::panicking\)' librustc_driver.d | sed -e 's/.*<//; s/[+@].*//' | sort | uniq -c | sort -nk1
...
     52 core::panicking::assert_failed::hbeae657127ccdb04
     54 rustc_data_structures::fingerprint::Fingerprint, rustc_data_structures::fingerprint::Fingerprint>
     56 &[rustc_errors::SubstitutionPart; 2]>>
     56 &rustc_errors::SubstitutionPart>>
     56 (rustc_span::span_encoding::Span, alloc::string::String)>>
     72 T,A>::insert::assert_failed::hb73c9898ad762f24
     74 rustc_middle::ty::Ty, rustc_middle::ty::Ty>
     80 core::panicking::panic_const::panic_const_div_by_zero::hb3b56552275843e1
     81 rustc_type_ir::DebruijnIndex, rustc_type_ir::DebruijnIndex>
     87 core::panicking::panic_const::panic_const_rem_by_zero::hff9e8539b36b8d6d
    119 u128, u128>
    128 rustc_abi::Size, rustc_abi::Size>
    149 core::panicking::assert_failed::h85f033378b656379
    241 bool, bool>
    315 core::slice::index::slice_index_order_fail::he688466d0d4f798a
    418 core::str::slice_error_fail::hc91fd7c32234f2bf
    418 hashbrown::control::tag::Tag, hashbrown::control::tag::Tag>
    434 core::panicking::assert_failed_inner::hb42cf086ef3fa5ea
   1101 core::slice::index::slice_start_index_len_fail::h2b0bd6f1ea36895a
   1483 core::panicking::panic_null_pointer_dereference::h455305b503f39847
   2193 core::slice::index::slice_end_index_len_fail::h082810a57bbce7a7
   3479 core::panicking::panic_misaligned_pointer_dereference::h639314a5907ff82f
   3686 core::result::unwrap_failed::h1d408d629b4c41f6
   9516 core::panicking::panic_bounds_check::he67b256737aac4b7
  10191 core::panicking::assert_failed::h7dbe1cbed9b3aef1
  11895 core::option::expect_failed::h35ab5df33563192c
  11923 core::option::unwrap_failed::h540db45763f4b740
  30678 core::panicking::panic_cannot_unwind::h03c30cf82c32c9e1
  30932 core::panicking::panic_fmt::h86f596f4590a5a7b
  40774 core::panicking::panic::h542f6569b46282bf
 124049 core::panicking::panic_in_cleanup::h6976e89252f67f6a
 143106 core::panicking::panic_nounwind::h4f41ec38a26ac6dc
```

# Advantages of panics

If error case is _very_ rare panics can give better performance than
Rust's preferred error handling (`Result`, `Option`) as
demononstrated by Alisa Sireneva with [iex](https://purplesyringa.moe/blog/you-might-want-to-use-panics-for-error-handling/)
crate (5-20% improvement on real projects).
[Here](https://web.archive.org/web/20230605115838/https://lordsoftech.com/programming/error-codes-are-far-slower-than-exceptions/)
and [here](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1886r0.html)
5-10% improvement is obtained for C++.
This could be improved by 4x with [different implementation](https://purplesyringa.moe/blog/bringing-faster-exceptions-to-rust/)
of panics (author [claims](https://www.reddit.com/r/rust/comments/1gl050z/comment/lvrowre/)
that 100x savings are possible).
In [this post](https://web.archive.org/web/20230605115838/https://lordsoftech.com/programming/error-codes-are-far-slower-than-exceptions/)
author suggests that exceptions are beneficial if error frequency is < 0.01%.

This generally goes against [popular guidelines](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html).

# Solutions

Rust has `panic=abort` (similar to C++ `-fno-exceptions`, ex. `-Z no-landing-pads`)

[No-panic Rust](https://blog.reverberate.org/2025/02/03/no-panic-rust.html)
approach is about rigorously removing _all_ panic calls from your program.

Ideally panics should be moved to cold functions to reduce overhead
but this is [not done](https://github.com/rust-lang/rust/issues/111866) now.

Outline panics via techniques like [this](https://www.reddit.com/r/rust/comments/1fdzu7z/comment/lmqfb49/):
```
#[inline(always)]
pub fn cheap_index<T>(slice: &[T], idx: usize) -> &T {
    match slice.get(idx) {
        Some(val) => val,
        None => outlined_panic(),
    }
}

#[cold]
#[inline(never)]
fn outlined_panic() -> ! {
    panic!("Index out of bounds")
}
```
Unfortunately many language constructs (e.g. `assert!` but see [issue #111866](https://github.com/rust-lang/rust/issues/111866))
do not outline.

# Combining panics

In some cases Rust needs to perform several checks at once
(see example in [bounds-checks](../bounds-checks/README.md)).

RFC 560 explicitly allows [delayed panics](https://github.com/rust-lang/rfcs/blob/master/text/0560-integer-overflow.md#delayed-panics)
i.e. combining these checks and emitting one final panic if any of them failed.
Also [this comment](https://github.com/rust-lang/rfcs/pull/560#issuecomment-69382228):
> it should be permitted but not required to abort the process when a overflowed value would have been observed

Unfortunately for LLVM each panic is an unknown function call with distinct parameters
so this can not be done at LLVM level and there is not dedicated MIR pass for this.

As a workaround, developers need to use manual `assert!`'s (or `core::hint::unreachable_unchecked`).

# TODO

Check overhead on panics in benches
  - can only be done in benches w/o `catch_unwind` (in bench itself and deps)
  - don't forget to disable panicking in stdlib:
    * update `[rust] std-features' in bootstrap.toml
    * or use `-Z build-std -Z build-std-features` in cargo

What is `panic_immediate_abort` ?

Does `panic=abort` remove landing pads and libunwind ?
  - `-Z no-landing-pads`, `-Zbuild-std-features=panic_immediate_abort` and `-Zlocation-detail=none` may be needed as well
  - it seems that `panic=abort` still calls the (blackbox) panic hooks (handlers)
  - try replacing `panic` with `core::panicking::panic_nounwind`

Does `panic=abort` avoid all overheads ? I couldn't get it to do anything in [this](https://news.ycombinator.com/item?id=30867188) example.
  - we need to find way to reduce it to `ud2`
  - compare to `-fno-exceptions`

Check if optimizations from https://www.youtube.com/watch?v=ItemByR4PRg (LICM, ADCE, etc.) are also disabled for Rust ?

Check if C++ also has same overhead due to exceptions: https://www.rottedfrog.co.uk/?p=24
  - If not, we need a slide on this

Measure increase of BTB/I$ misses PMUs and [stack usage](https://www.memorysafety.org/blog/rav1d-performance-optimization)
when panics are disabled

Check if hot-cold splitting works (i.e. panic handlers moved out of normal function code)
and speeds up

All info about performance overhead of panics.

Note that `unreachable!`, `assert!` and `unimplemented!`
all panic internally.

Panics involve stack unwinding and destructors so are definitely not free.
E.g. they complicate compiler analyses due to presence of landing pads.

Panicking causes significant code bloat in small functions (e.g. [here](https://www.rottedfrog.co.uk/?p=24)).

It's not clear how they influence performance (or whether they do at all).
Note that exceptions may actually be _beneficial_ for performance
because no BTB is wasted on error handling code.

Panics make leaf functions no longer leaf (see [this](https://www.reddit.com/r/programming/comments/2po703/comment/cmym6jk/))
which may harm optimizations (e.g. inlining) and introduce unnecessary reg spills.

# Advantages of panics

If error case is _very_ rare panics can give better performance than
Rust's preferred error handling (`Result`, `Option`) as
demononstrated by [iex](https://purplesyringa.moe/blog/you-might-want-to-use-panics-for-error-handling/)
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

What is `panic_immediate_abort` ?

Does `panic=abort` remove landing pads and libunwind ?
  - `-Z no-landing-pads`, `-Zbuild-std-features=panic_immediate_abort` and `-Zlocation-detail=none` may be needed as well
  - It seems that `panic=abort` still calls the (blackbox) panic hooks (handlers)

Does `panic=abort` avoid all overheads ? I couldn't get it to do anything in [this](https://news.ycombinator.com/item?id=30867188) example.
  - we need to find way to reduce it to `ud2`

Check if optimizations from https://www.youtube.com/watch?v=ItemByR4PRg (LICM, ADCE, etc.) are also disabled for Rust ?

Check if C++ also has same overhead due to exceptions: https://www.rottedfrog.co.uk/?p=24
  - If not, we need a slide on this

Measure increase of BTB/I$ misses PMUs and [stack usage](https://www.memorysafety.org/blog/rav1d-performance-optimization)
when panics are disabled

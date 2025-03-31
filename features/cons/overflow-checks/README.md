Rust does not check overflows in release (so I'm not sure we need this directory).

Rust does not check for signed integer overflow in release because it is fully specified as 2's complement wrapping (https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow).
Rust suggests using `wrapping_*` methods to explicitly use this.

On the other hand it does not assign `nsw`s to signed integer computations like C/C++.
See https://kristerw.blogspot.com/2016/02/how-undefined-signed-overflow-enables.html for example optimizations based on `nsw`.

Android seems to enable overflow checks (UBsan, Isan) for critical components (written in C):
  - https://android-developers.googleblog.com/2016/05/hardening-media-stack.html
  - https://android-developers.googleblog.com/2018/06/compiler-based-security-mitigations-in.html

# Problems caused by defined overflow

Note that overhead here is not the checks themselves but disabling of optimizations (e.g. vectorization).

# Solutions

- `unchecked_add` and friends
- `unchecked_math` pragma
- asserts or compiler hints:
```
pub unsafe fn nop(x: i32) -> i32 {
    if x <= i32::MIN >> 1 || x >= i32::MAX >> 1 {
        unsafe { std::hint::unreachable_unchecked() }
    }
    x * 2 / 2
}
```
(from [here](https://www.reddit.com/r/rust/comments/181av9f/comment/kae7079/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)).

# TODO

- Add `nsw` to signed integers and compare perf of large and/or performance sensitive projects
- Measure overhead via `-Z force-overflow-checks`
  * Does it add `nsw`/`nuw` and enable loop optimizations ?

# Inclusive ranges are slower than exclusive ones

Loop like
```
for i in 0 ..= max {
```
is much slower than
```
for i in 0 .. (max + 1) {
```

This happens because `..=` is a `RangeInclusive` object whose implementation of `Iterator`
contains a check for last element. This check introduces overhead on every iteration.

`RangeInclusive` can't be replaced with exclusive Range (with `n+1` upper bound)
due to potential overflow and panic. Programmer can do this manually though.

TODO: check if LLVM could move the check outside of loop

Good explanation of this is given in https://www.reddit.com/r/rust/comments/15tvuio/why_isnt_the_for_loop_optimized_better_in_this/

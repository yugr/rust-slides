Rust does not check overflows in release (so I'm not sure we need this directory).

Overflows are evaluated via 2's complement wrapping (https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow)
in release but panic in debug
This is allowed by [RFC 560](https://github.com/rust-lang/rfcs/blob/master/text/0560-integer-overflow.md)
(panicking is also permitted in release so its suggested to NOT rely on wrapping semantics
in release and use explicit `wrapping_*` methods / `Wrapping` types if needed).

This decision is a compromise between safety and security.
Rust developers clearly [state](https://github.com/rust-lang/rfcs/pull/560#issuecomment-69403142) that
> Plan is to turn on checking by default if we can get the performance hit low enough
and also that it should
> leave room in the future to move towards universal overflow checking if it becomes feasible
and also [here](https://www.reddit.com/r/rust/comments/4gz93u/comment/d2mcoje/)
> It is hoped that as the performance of checks improves (notably with delayed checks, better value propagation, etc...),
> at some point in the future they could be switched on by default.

John Regehr's well known study [estimates](https://users.cs.utah.edu/~regehr/papers/overflow12.pdf)
integer checks to have 30-50% overhead on average (with up to 3x worst case).

Main sources of overhead from checked arithmetic are
  - checks themselves (comparison + optional jump => wasted decode + increased I$ and BTB pressure)
  - inhibiting other opts due to serialization (so disables vectorization, loop opts)
(from [Myths and Legends](https://huonw.github.io/blog/2016/04/myths-and-legends-about-integer-overflow-in-rust/)).
The second one is much more problemantic in terms of perf.
[This discussion](https://www.reddit.com/r/rust/comments/ab7hsi/comment/ed0u11h/)
suggests that this could be fixed if overflow checking were combined
into arithmetic instruction in IR (to avoid introducing control flow and splitting BBs).

Interestingly enough Rust makes a less secure choice than Swift
which aborts on integer overflow even in release builds.

On the other hand it does not assign `nsw`s to signed integer computations like C/C++.
See https://kristerw.blogspot.com/2016/02/how-undefined-signed-overflow-enables.html for example optimizations based on `nsw`.
This may not be a big problem: `0..n` in
```
for i in 0..n
```
is guaranteed to execute `n` times.

Android seems to enable overflow checks (UBsan, Isan) for critical components (written in C):
  - https://android-developers.googleblog.com/2016/05/hardening-media-stack.html
  - https://android-developers.googleblog.com/2018/06/compiler-based-security-mitigations-in.html

Also Swift language has overflow checks on by default even in optimized builds.

# Problems caused by defined overflow

Note that overhead here is not the checks themselves but disabling of optimizations
(e.g. vectorization due to potential wrapping).

# Solutions

- `unchecked_add` and friends
- `Wrapping<T>` types in stdlib
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

# Links

* [RFC 560](https://github.com/rust-lang/rfcs/blob/master/text/0560-integer-overflow.md)
* [Myths and Legends about Integer Overflow](https://huonw.github.io/blog/2016/04/myths-and-legends-about-integer-overflow-in-rust/)

# TODO

- Add `nsw` to signed integers and compare perf of large and/or performance sensitive projects
- Measure overhead via `-Z force-overflow-checks` (or `-C overflow-checks=on`)
  * See [RFC 1535](https://github.com/rust-lang/rfcs/blob/master/text/1535-stable-overflow-checks.md) for some details
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

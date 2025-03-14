Rust does not check overflows in release (so I'm not sure we need this directory).
On the other hand it does not assign `nsw`s to signed integer computations like C/C++.

# TODO

- Add `nsw` to signed integers and compare perf of large and/or performance sensitive projects

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

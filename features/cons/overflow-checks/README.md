All info about problems with overflow checks at runtime.

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

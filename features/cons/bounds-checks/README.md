All info about problems with bounds checks at runtime.

# Problems caused by bounds checks

matklad [claims](https://github.com/matklad/bounds-check-cost) that main problem with bounds checks
is blockage of autovec (and maybe other optimizations) and check themselves are cheap.
Another example of blocked autovec: https://rust.godbolt.org/z/hccWGv889

burntsushi [claims](https://news.ycombinator.com/item?id=14903258) that bounds checking is not the only problem with autovectorization

Feedback from Servo devs on bounds checks overhead: https://news.ycombinator.com/item?id=10268151

Note that bounds checks also take some I$ and branch predictor slots.

# Solutions

Often compiler may remove bounds checks itself
but this is not always the case even in [simple](https://users.rust-lang.org/t/performance-of-array-access-vs-c/43522)
examples.

Bounds checks can be removed via
  - using iterators instead of indexes (this is not always possible)
    * [example](https://www.reddit.com/r/rust/comments/154vowr/comment/jsr0b51/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
  - using asserts (https://rust.godbolt.org/z/GPMcYd371) or `core::hint::unreachable_unchecked`
    * [example](https://github.com/rust-random/rand/pull/960)
  - constructing pre-checked slices:
```
let len = vec.len();
let slice = &vec[0..len];
for i in 0..len {
    slice[i] // no bounds check
}
```
  (also [here](https://users.rust-lang.org/t/possible-rust-specific-optimizations/79895/5)).

# TODO

- Disable index checks in compiler and compare perf of large and/or performance sensitive projects
  * patch to disable checks: https://blog.readyset.io/bounds-checks
  * also some info [here](https://users.rust-lang.org/t/a-way-to-turn-off-all-bounds-checks-for-exploring-optimisation-potential/117528/4)
  * disables [in stdlib](https://github.com/rust-lang/rust/pull/119440)
  * [unchecked_math](https://github.com/rust-lang/rfcs/issues/2508) feature may be relevant
- Can we somehow measure how often compiler is able to remove index checks from loops ?

# Combining multiple checks not optimized

Compiler does not combine multiple related index checks to same slice within same scope into one.
See [upstream #50759](https://github.com/rust-lang/rust/issues/50759) for good example of this.

Basically when accessing `h[0]` and then `h[1]` it has to first check `0` and then `1`
because it tries to report exact error location (or at least LLVM optimizer believes so).

This may be an overkill - RFC 560 explicitly [allows](https://github.com/rust-lang/rfcs/blob/master/text/0560-integer-overflow.md#delayed-panics)
delayed panics. Also [here](https://github.com/rust-lang/rfcs/pull/560#issuecomment-69382228):
> it should be permitted but not required to abort the process when a overflowed value would have been observed

Programmers can use explicit `assert!` macro to allow compiler to optimize checks.
Or just optimizer hint:
```
pub unsafe fn nop(x: i32) -> i32 {
    if x <= i32::MIN >> 1 || x >= i32::MAX >> 1 {
        unsafe { std::hint::unreachable_unchecked() }
    }
    x * 2 / 2
}
```
(from [here](https://www.reddit.com/r/rust/comments/181av9f/comment/kae7079/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)).

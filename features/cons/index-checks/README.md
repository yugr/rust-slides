All info about problems with bounds checks at runtime.

# Problems caused by bounds checks

matklad [claims](https://github.com/matklad/bounds-check-cost) that main problem with index checks
is blockage of autovec (and maybe other optimizations) and check themselves are cheap.
Another example of blocked autovec: https://rust.godbolt.org/z/hccWGv889

burntsushi [claims](https://news.ycombinator.com/item?id=14903258) that bounds checking is not the only problem with autovectorization

Feedback from Servo devs on bounds checks overhead: https://news.ycombinator.com/item?id=10268151

Note that bounds checks also take some I$ and branch predictor slots.

# Solutions

Bounds checks can be removed via
  - using iterators instead of indexes (this is not always possible)
  - using asserts (https://rust.godbolt.org/z/GPMcYd371)
  - constructing pre-checked slices:
```
let len = vec.len();
let slice = &vec[0..len];
for i in 0..len {
    slice[i] // no bounds check
}
```

# TODO

- Disable index checks in compiler and compare perf of large and/or performance sensitive projects
  * patch to disable checks: https://blog.readyset.io/bounds-checks
- Can we somehow measure how often compiler is able to remove index checks from loops ?

# Combining multiple checks not optimized

Compiler does not combine multiple related index checks to same slice within same scope into one.
See [upstream #50759](https://github.com/rust-lang/rust/issues/50759) for good example of this.

Basically when accessing `h[0]` and then `h[1]` it has to first check `0` and then `1`
because it tries to report exact error location (or at least LLVM optimizer believes so).

Programmers can use explicit `assert!` macro to allow compiler to optimize checks.

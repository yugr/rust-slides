Rust does not check overflows in release (so I'm not sure we need this directory).

Overflows are evaluated via 2's complement wrapping (https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow)
in release but panic in debug.
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

# Explicit overflow checks in stdlib

Even when overflow checks are disabled, stdlib performs them in some APIs.

String slices also check that upper limit is not `usize::MAX`
(see e.g. `SliceIndex<str>::index` in `core/src/str/traits.rs`).

Also in `library/alloc/src/slice.rs`:
```
let capacity = self.len().checked_mul(n).expect("capacity overflow");
```
or `alloc/src/str.rs`:
```
    let reserved_len = sep_len
        .checked_mul(iter.len())
        .and_then(|n| {
            slice.iter().map(|s| s.borrow().as_ref().len()).try_fold(n, usize::checked_add)
        })
        .expect("attempt to join into collection with len > usize::MAX");
```

# Solutions

- `unchecked_add` or `wrapping_XXX` intrinsics
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
(from [here](https://www.reddit.com/r/rust/comments/181av9f/comment/kae7079/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button))

Some people (e.g. John Regehr) argue that HW support for overflow checking would significantly reduce costs.
But arhictects [claim](https://news.ycombinator.com/item?id=8766264) that
this will cause a big (~5%) increase of clock cycle.

# Other languages

C++ has UBsan/Isan and Pascal has long had `$Q+` (e.g. [here](https://www.freepascal.org/docs-html/prog/progsu64.html)).

# Overflow UB in C++

Undefining signed integer overflow is relevant for some important usecases in C/C++.

Consider a loop like
```
for (T i = 0; i <= n; ++i) {  // Also 'i != n'
  p[i] = 1.0;
}
```
([Godbolt link](https://godbolt.org/z/MEhfEdb9z)).

On 64-bit platforms pointers are 64-bit but indices are often 32-bit.

For `T == int` this loop will execute forever for `n == INT_MAX`
(considering wrapping arithmetic).
Also due to wrap-around it's not possible to promote `i` to 64-bit -
we have to sign-extend it in loop to preserve the wrap-around semantics.

Same problem occurs for unsigned indices (and signed under `-fwrapv`)
but unfortunately overflow is defined for them
(so above loop is significantly slower for `T == unsigned`).

Another example: without UB it would be impossible to replace
other induction variables:
```
for (i = lo; i <= hi; i++)
  sum ^= i * 53;
```
with
```
for (ic = lo * 53; ic <= hic; ic += 53)
  sum ^= ic;
```

In [this case](https://nullprogram.com/blog/2018/07/20/)
using unsigned's also does not allow compiler
to fuse index variables to pointers (due to potential overflow):
```
    for (;;) {
        int c1 = buf[i1];
        int c2 = buf[i2];
        if (c1 != c2)
            return c1 - c2;
        i1++;
        i2++;
    }
```
This is similar to infamous Carruth's example in
[Garbage In, Garbage Out](https://youtu.be/yG1OZ69H_-o?t=2358) talk.
Basically any program where indices do not have a fixed upper bound
has this issue.

Finally signed overflow UB also allows for better
[range tracking](https://kristerw.blogspot.com/2016/02/how-undefined-signed-overflow-enables.html).

# Links

* [RFC 560](https://github.com/rust-lang/rfcs/blob/master/text/0560-integer-overflow.md)
* [Myths and Legends about Integer Overflow](https://huonw.github.io/blog/2016/04/myths-and-legends-about-integer-overflow-in-rust/)

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

Take for example these two codes in Rust
```
#[no_mangle]
pub fn sum_of_n_unsigned(n: usize) -> usize {
    let mut total = 0;
    for i in 1..=n {
        total += i;
    }
    total
}
```
and C
```
unsigned long sum_of_n_unsigned(unsigned long n) {
  unsigned long total = 0;
  for (unsigned long i = 0; i <= n; ++i)
    total += i;
  return total;
}
```

They produce very different asms:
```
.LBB0_3:
        movq    %rcx, %rdx
        cmpq    %rdi, %rcx
        adcq    $0, %rcx
        addq    %rdx, %rax
        cmpq    %rdi, %rdx
        jae     .LBB0_5
        cmpq    %rdi, %rcx
        jbe     .LBB0_3
```
and
```
.LBB0_1:                                # =>This Inner Loop Header: Depth=1
        addq    %rcx, %rax
        addq    $1, %rcx
        cmpq    %rdi, %rcx
        jbe     .LBB0_1
```
(respectively). C asm is better for a reason: it allows for endless loop
(for `n == USIZE_MAX`) whereas Rust code is finite.

In theory this could be optimized by LLVM by making two copies of loop
(for normal and `USIZE_MAX` cases) but this would significantly increase code size ?

Good explanation of this is given in https://www.reddit.com/r/rust/comments/15tvuio/why_isnt_the_for_loop_optimized_better_in_this/

Another [good citation](https://www.reddit.com/r/rust/comments/eiwhkn/comment/fcu4y8y/):
> This is a general problem for all state-machine iterators,
> that is iterators where the implementation of next
> involves switching on a "state" variable, and thus applies to chain as well. 

All info about problems with bounds checks at runtime.

Memory safety issues account for [76%](https://security.googleblog.com/2024/09/eliminating-memory-safety-vulnerabilities-Android.html)
of vulnerabilities in Android.

Important note is that most problems reported by users are
in perf-critical code (codecs, math, autovec, etc.)
Real-world codebases have much smaller average overhead
E.g. Google reports [report](https://security.googleblog.com/2024/11/retrofitting-spatial-safety-to-hundreds.html)
just 0.3% performance overhead for services and ~0.5% size increase of Chrome binary:
  - caveat - the numbers were measured with FDO enabled
    (w/o FDO penalty is [4x larger](https://bughunters.google.com/blog/6368559657254912/llvm-s-rfc-c-buffer-hardening-at-google))

It's important to keep an eye on compiler as some bounds check optimizations
may regress across versions.

# Problems caused by bounds checks

matklad [claims](https://github.com/matklad/bounds-check-cost) that main problem with bounds checks
is blockage of autovec (and maybe other optimizations) and check themselves are cheap.
Another example of blocked autovec: https://rust.godbolt.org/z/hccWGv889

burntsushi [claims](https://news.ycombinator.com/item?id=14903258) that bounds checking is not the only problem with autovectorization.

Feedback from Servo devs on bounds checks overhead: https://news.ycombinator.com/item?id=10268151

Note that even though bounds checks are predictable
they also take some I$ and branch predictor slots.
E.g. Daniel Lemire [shows](https://lemire.me/blog/2019/11/06/adding-a-predictable-branch-to-existing-code-can-increase-branch-mispredictions/)
that addition of predictable branch in hot loop increases branch mispredicts 2x-4x.

# Solutions

Often compiler may remove bounds checks itself
but this is not always the case even in [simple](https://users.rust-lang.org/t/performance-of-array-access-vs-c/43522)
examples.

Bounds checks can be removed via
  - using iterators instead of indexes (this is not always possible)
    * [example](https://www.reddit.com/r/rust/comments/154vowr/comment/jsr0b51/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
  - using asserts (https://rust.godbolt.org/z/GPMcYd371) or `core::hint::unreachable_unchecked`
    * [example](https://github.com/rust-random/rand/pull/960)
    * [examples in Nethercote's book](https://nnethercote.github.io/perf-book/bounds-checks.html)
    * note that plain `assert!` should be used (e.g. `assert_eq!` may cause [slowdown](https://coaxion.net/blog/2018/01/speeding-up-rgb-to-grayscale-conversion-in-rust-by-a-factor-of-2-2-and-various-other-multimedia-related-processing-loops/) !)
  - constructing pre-checked slices (reslicing, subslicing):
```
let len = vec.len();
let slice = &vec[0..len];
for i in 0..len {
    slice[i] // no bounds check
}
```
  (also [here](https://users.rust-lang.org/t/possible-rust-specific-optimizations/79895/5)).
    * a handy variant of this when performing multiple accesses at once (from [here](https://www.reddit.com/r/rust/comments/10edmjf/comment/j4ufzxk/)):
```
let [a, b, c, d] = data[..4] else { panic!() }
```
  - slicing i.e. using slices instead of e.g. `Vec`'s or `String`'s; particularly good for `&mut [T]` vs `&mut Vec<T>`
    * see [issue](https://github.com/nnethercote/perf-book/issues/50) and [clippy check](https://github.com/rust-lang/rust-clippy/issues/10269)
  - using `cmp::min` to force index into safe range:
```
let bounded_i = cmp::min(i, sums.len());
sums[bounded_i] = ...
```
    * this approach may be unstable in removing the checks, see [this](https://users.rust-lang.org/t/rust-vs-c-vs-go-runtime-speed-comparison/104107/15) and [this](https://users.rust-lang.org/t/rust-vs-c-vs-go-runtime-speed-comparison/104107/20) for details
    * this is useful to tell compiler that two slices have the same range (by subslicing them to `min` of lengths, e.g. [here](https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e)) although [using zip](https://www.reddit.com/r/rust/comments/154vowr/comment/jsr0b51/) also works
  - forcing index into bounds via `& (len - 1)` (`len` must be power-of-2)
  - avoid complex (actually [any nontrivial](https://www.nickwilcox.com/blog/autovec/)) arithmetic on indexes

For workarounds like this keep in mind that
> The thing is that using unsafe not bound checking access
> you are 100% sure code will do what you want,
> otherwise you will have to chase the rabbit into the rabbithole with every version of Rust
> since it changes how compiles the stuff,
> sometimes it gains performance while others take a hit 
(from [here](https://www.reddit.com/r/rust/comments/10edmjf/comment/j4qhgeo/)).

# C++

C++ also has checking methods e.g. `std::vector::at` but more importantly
it supports hardening mode (both Libstdc++ and Libc++,
`-fhardened` (aka `_GLIBCXX_ASSERTIONS`) and `-fhardened-libc++` (`_LIBCPP_HARDENING_MODE`) resp.,
also MSVC with `_ITERATOR_DEBUG_LEVEL` and EASTL with its own checks)
which implements checks like bounds, strict weak ordering, etc.
Moreover STL hardening [has been accepted](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2025/p3471r4.html)
for Standard.

Bounds checking overhead can be equated to replacing
`reserve` + `push_back` with `resize`
([here](https://source.chromium.org/chromium/chromium/src/+/63dbcdf2bfd553bc91524ec0a77dfd32a4d4a427)
it brought up to 50% performance)
or `operator[]` with `at` ([20%](https://quick-bench.com/q/o9du22dYmO0BCs5YqJ9gEKPyQ10) perf loss).
This should not be a surprise - people who practice LeetCode know that
`std::vector::resize` with direct indexing is _faster_ than
`std::vector::reserve` with `push_back`'s.

All Linux distros use `_FORTIFY_SOURCE` and some (Fedora, RHEL) also `_GLIBCXX_ASSERTIONS`.

There is also proposal for language dialect eo prevent raw pointer arithmetic
and provide fixits for easier migration
([-Wunsafe-buffer-usage](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734))

Pascal/Delphi also had [range checking](http://www.pascal.helpov.net/index/pascal_$R)
long ago.

# Links

- [How to avoid bounds checks in Rust without unsafe](https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e)

# TODO

- Disable index checks in compiler and compare perf of large and/or performance sensitive projects
  * patch to disable checks: https://blog.readyset.io/bounds-checks
  * also some info [here](https://users.rust-lang.org/t/a-way-to-turn-off-all-bounds-checks-for-exploring-optimisation-potential/117528/4)
  * disables [in stdlib](https://github.com/rust-lang/rust/pull/119440)
  * [unchecked_math](https://github.com/rust-lang/rfcs/issues/2508) feature may be relevant
- Can we somehow measure how often compiler is able to remove index checks from loops ?
- Verify strange off-by-one behaviour of bounds checks (maybe a bug?) (https://users.rust-lang.org/t/rust-vs-c-vs-go-runtime-speed-comparison/104107/20)

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

One more workaround suggested [here](https://users.rust-lang.org/t/is-bound-checking-the-only-runtime-cost-of-rust/66661/22)
and [here](https://www.reddit.com/r/rust/comments/10edmjf/comment/j4sfxyl/)
is to rearrange access to perform the farthest one first.

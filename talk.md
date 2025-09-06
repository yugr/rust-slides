This is the plan of the talk.

# What this talk is NOT about

- Non-idiomatic code (SIMD, intrinsics, inline asm, `wrapping_add`, too many `unsafe`s, `restrict` in C++, `__builtin_expect`'s, etc.)
  * would like to compare "standard" (default) Rust and C++
  * Benchmarks Game uses wildly non-canonical code, to everyone's dismay
  * "It makes little sense to compare Rust vs C with respect to performance, because you can write the exact equivalent of C code in Rust and get the same performance"
    (from [here](https://users.rust-lang.org/t/a-good-performance-comparision-c-and-rust/5901/4))
  * "When you compare languages like C, C++ and Rust, which are by-design on equal footing, you can essentially only compare how easy it is to write performant code or how performant idiomatic code is. Modulo optimizer deficiencies, if you implement the exact same datastructures and same algorithms in these languages, they will perform the same." (from [here](https://www.reddit.com/r/rust/comments/9jsqyg/comment/e6ufwcm/))
  * "If C can be faster than C I don't see why Rust can't be faster than C"
    (from [here](https://www.reddit.com/r/rust/comments/1ixt1ei/comment/meow7rc/))
  * [Good example](https://steveklabnik.com/writing/is-rust-faster-than-c) of why non-idiomatic code is less relevant
- Just comparing few random programs
  * not enough to draw conclusions
- Just looking at asm code
  * inefficiencies may be due to bug / NYI feature in LLVM ("Sufficiently Smart Compiler")
  * should check what is NYI and can never be implemented in LLVM optimizer
  * do not expect "heroic compiler"
- Performance of parallel code (["fearless concurrency"](https://blog.rust-lang.org/2015/04/10/Fearless-Concurrency.html))
  * claimed to be underlying reason of `ripgrep` success by its author
  * well known and discussed in many posts and presentations
  * maybe next time
- Container performance
  * e.g. `HashMap` is known to be much better than `std::unordered_map` (and `BTreeMap` than `std::map`) but in practice everyone just uses Abseil or Boost maps
- Language features which are not directly performance-related:
  * custom allocators and placement-new
  * ABI
- (Slow) compile times
  * A lot of work done by Nethercote
- Analysis of benchmarks regressions/improvements
  * Maybe next time...

# Is it fair to compare with C++ ?

Rust targets same problem area:
  - [system programming language](https://willcrichton.net/notes/systems-programming/)
    * "Generaly, it's 'the same order of magnitude as C'. Sometimes faster, sometimes slower" ([Steven Klabnik](https://users.rust-lang.org/t/what-kind-of-performance-rust-is-trying-to-achieve/1674/2))
  - zero-cost abstractions (should better be called "zero (unavoidable) overhead", this is also used by Stroustroup)
    * no (or minimal) runtime overhead
    * don't pay for what you don't use
    * no GC
    * "What you don’t use, you don’t pay for. And further: What you do use, you couldn’t hand code any better" (Stroustrup "Abstraction and the C++ machine model")
  - supports low-level tuning
    * SIMD (core::arch, core::simd), inline asm, intrinsics (e.g. `__builtin_assume` vs `core::hint::assume`, `__builtin_expect` vs `#[likely]`, PGO)
  - same optimizer (LLVM)

As [put by scottmcmrust](https://www.reddit.com/r/rust/comments/kpqmrh/comment/gi3u2ki/):
```
Because there's no way that the code you're writing needs to be as optimized as possible while discounting all other factors. Everything has diminishing returns, but that's ignored for benchmarks.

And then for AoT-compiled languages in particular, clang and rustc are both producing LLVM IR and running mostly the same LLVM optimization passes. So given enough work they can always produce essentially the same thing, making the comparisons pointless.

It's even worse for things like the TechEmpower web ones -- there's no requirement that they error properly or are secure against attacks. At least for offline batch things like in benchmarks game you could use the implementations, but it would be negligent to use the top-performing ones in the TechEmpower benchmarks.
```

Important caveats:
  - make sure to build with `--release` :)
  - make sure that (default) target CPU is the same (especially JIT languages like Java are equivalent to `-C target-cpu=native`)
  - `--emit=asm` may change codegen due to implied [-C codegen-units=1](https://github.com/rust-lang/rust/issues/57235)
    * so it's more reliable to compile to .rlib and use `objdump -d`
  - note about benchmarks:
    * numbers are averaged over many scenarios in each bench
    * even a 1% regression means there's some scenario with 10-20% degradation

# Rust performance issues

Rust seems to put safety ahead of performance:
  - "Rust is a modern systems programming language focusing on safety, speed, and concurrency" ([Rust by Example](https://doc.rust-lang.org/rust-by-example/))
  - "Rust prioritizes memory safety above all else. But speed is a close second" ([Steven Klabnik](https://users.rust-lang.org/t/what-kind-of-performance-rust-is-trying-to-achieve/1674/2))
  - more on tradeoffs [here](https://www.infoq.com/presentations/rust-tradeoffs/) and [here](https://www.youtube.com/watch?v=2wZ1pCpJUIM)
  - manifests e.g. in inability to enable fast math or turn off bounds checking
  - but at the same time things which would have incurred too much overhead are disabled e.g.
    * integer overflows not checked in release (because overhead is unacceptable)
    * result of sort is not checked (may cause unpredictable results for bad comparators)
    * some checks are hidden under `-Z ub-checks` (alignment and NULL)

Some Rust's abstractions are NOT zero-cost (or at least less zero-cost than in C++) :
  - are by design more expensive than C++ equivalents
  - can not be fixed by more sophisticated optimizations
  - see examples below

Main source of performance overhead: UB avoidance

Note that some overheads are basic (e.g. bounds checking)
and some are consequences (e.g. disabled autovec).

Even fast checks introduce several problems:
  - pressure on caches (I$, BTB)
  - more complex control flow so other opts break

- Runtime checks (see `AssertKind` enum in `compiler/rustc_middle/src/mir/syntax.rs`):
  * index accesses:
    + LLVM may not always remove them which will break autovec
      - TODO: we need to collect statistics on autovec improvements if checking is disabled
    + prefer iterators to indexing
    + need to investigate several common cases: LICM for index checks in loops, support for [inclusive](https://github.com/rust-lang/rust/issues/45222)/exclusive ranges, const/non-const bounds
    + slices have to be fat (so take up two registers in function call)
    + explicit reslicing needed (see https://users.rust-lang.org/t/understanding-rusts-auto-vectorization-and-methods-for-speed-increase/84891/5)
  * strings
    + UTF-8 invariants checked during operations (see e.g. https://users.rust-lang.org/t/performance-comparison/56041/5)
- Inefficient data structures due to borrow checker limitations:
  * self-referential structs require refcounting
    + `Rc<RefCell<T>>`
    + `borrow_mut` checks may not be reliably LICM-ed from loops
    + graphs, what other important data structues ?
    + "self-ref structs are not 0-cost" (https://www.youtube.com/watch?v=UrDhMWISR3w)
  * unable to take two mutable refs to different elements of std collections / slices
  * have to use indices (with runtime index checks penalty) instead of iterators
  * as a result, ALL high-performance data structures use unsafe code to skip borrow checker (see [this](https://internals.rust-lang.org/t/goals-and-priorities-for-c/12031/52))
- Integer overflows are defined (wrapping) in release
  * so no loop optimizations based on signed overflow
- slower (safer?) library defaults:
  * [PRNG](https://users.rust-lang.org/t/julia-outperforms-rust-in-generating-a-vector-of-random-numbers/101624)
  * [unbuffered IO](https://users.rust-lang.org/t/in-my-benchmark-i-found-rust-slower-than-c/71944/6) (need to use BufWriter, also read [this](https://nnethercote.github.io/perf-book/io.html))
  * safer but slower sort algorithm
    + https://github.com/Voultapher/sort-research-rs/blob/main/writeup/sort_safety/text.md
    + https://www.youtube.com/watch?v=rZ7QQWKP8Rk
- No dynamic stack allocation (`alloca`, VLAs)
  * Some work done in [RFC 1909](https://github.com/rust-lang/rfcs/blob/master/text/1909-unsized-rvalues.md)
    but not much work since 2018
- Panic unwinding overhead
- Lack of type-based aliasing like in C (`-fstrict-aliasing`)
  * not considered important due to reference aliasing rules
  * but may be important for pointer operations in unsafe blocks
- Lack of `-ffast-math`
  * https://www.reddit.com/r/rust/comments/e5ge5k/rust_and_ffastmath
- Error codes vs. exceptions
  * how much we pay in terms of binary size (and I$ utilization) ?
- No `nullptr`
  * is discriminator in `Option<T&>` (`Result<T&, E>`) always optimized out ?
- No per-class/container allocators
  * https://github.com/rust-lang/rust/issues/32838
  * Why “bring your own allocator” APIs are not more popular in Rust? https://internals.rust-lang.org/t/why-bring-your-own-allocator-apis-are-not-more-popular-in-rust/14494
- Forced variable initializations (especially large arrays)
  * https://blog.logrocket.com/understanding-inheritance-other-limitations-rust/
- Code size
- No gotos, computed or otherwise
  * This is a real problem for writing efficient state machines
    (see [this](https://github.com/rust-lang/rfcs/pull/3720) RFC proposal)
- Mandatory initialization of all variables

# Rust-specific optimization opportunities

Rust language also enables new, more aggressive optimizations.
Rust _can_ be faster than C !

Rust makes some default choices more performant:
  * move by default
  * functions are static by default
  * struct members can be reordered by default
  * references are restrict by default
  * `-fno-plt` and `-ffunction-sections` by default

Arguably similar defaults are recommended for C++
but often (usually ?) not present in average production codebase.

- Move by default (https://www.thecodedmessage.com/posts/cpp-move/ and https://mcyoung.xyz/2021/04/26/move-ctors/)
  * also `Vec` is moved on `resize` at once, rather than by element as in STL
    + is this correct ? `std::vector` should be optimized for trivial types !
  * are issues from https://www.youtube.com/watch?v=rHIkrotSwcc fixed in Rust ?
- All references are `restrict` by default
  * currently only applied at func boundaries
- Discriminator (enum tag) embegging
    * analog of LLVM's `PointerIntPair`, `PointerSumType`, `PointerUnion`
    * https://users.rust-lang.org/t/documentation-of-null-pointer-optimization/58038
    * https://github.com/rust-lang/rfcs/issues/1230
- Struct size optimizations
- Support for ZSTs
  * do not need EBO like C++
- Fearless concurrency
- Copy/move elision (?)
- `Box` is more performant than `unique_ptr` (https://www.youtube.com/watch?v=rHIkrotSwcc&t=1261s)
- local function visibility by default

# Comparing against C++

We can't fairly compare Rust to C++ because there are very few equivalent programs
written in both Rust and C++.

Instead we make an assumption that Rust with disabled checks is very close to C++
(similar abstraction like functions, stack, heap, etc. and same LLVM backend).
So we expect that comparing performance of stock Rust vs. Rust without checks
should be close to comparing Rust to C/C++.

TODO:
  - compare performance of rav1d/rav1e without checks to C code (hopefully should be close)

# Conclusions

- Ideally need some ballpark numbers here for different classes of programs
- Also split problems to ones that
  * may eventually be fixed by compiler, at least in theory
    + short-term (e.g. loop unswitching in iterators or redundant `memcpy`)
    + long-term (e.g. de-templatizing)
  * should be worked around by developers (e.g. bounds checks)
  * can not be efficiently fixed (e.g. fast math)
- It's possible to write 100% equivalent Rust/C++ code;
  but Rust generally makes saner defaults in idiomatic code

Caveat for whoever watches this in future: contents may easily get outdated

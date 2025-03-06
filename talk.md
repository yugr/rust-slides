This is the plan of the talk.

# What this talk is NOT about

- Non-idiomatic code (SIMD, intrinsics, inline asm, `wrapping_add`, too many `unsafe`s, etc.)
  * would like to compare "standard" Rust and C++
- Just comparing few random programs
  * not enough to draw conclusions
- Just looking at asm code
  * inefficiencies may be due to bug / NYI feature in LLVM
  * should check what is NYI and can never be implemented in LLVM optimizer
- Performance of parallel code
  * maybe next time
- Container performance
  * e.g. `HashMap` is known to be much better than `std::unordered_map` (and `BTreeMap` than `std::map`) but in practice everyone just uses Abseil or Boost maps
- Language features which are not directly performance-related:
  * custom allocators and placement-new
  * ABI

# Is it fair to compare with C++ ?

Rust targets same problem area:
  - system programming language
  - zero-cost abstractions
    * no (or minimal) runtime overhead
    * don't pay for what you don't use
    * no GC
  - supports low-level tuning
    * SIMD, inline asm, intrinsics (e.g. `__builtin_assume`, `__builtin_expect`)
  - same optimizer (LLVM)

# Rust performance issues

Some Rust's abstractions are NOT zero-cost (or at least less zero-cost than in C++) :
  - are by design more expensive than C++ equivalents
  - can not be fixed by more sophisticated optimizations
  - see examples below

Main source of performance overhead: UB avoidance

- Runtime checks:
  * index accesses:
    + LLVM may not always remove them which will break autovec
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
  * as a result, ALL high-performance data structures use unsafe code to skip borrow checker
- Integer overflows are defined (wrapping) in release
  * so no loop optimizations based on signed overflow
- slower (safer?) library defaults:
  * [PRNG](https://users.rust-lang.org/t/julia-outperforms-rust-in-generating-a-vector-of-random-numbers/101624)
  * [unbuffered IO](https://users.rust-lang.org/t/in-my-benchmark-i-found-rust-slower-than-c/71944/6) (need to use BufWriter)
  * safer but slower sort algorithm
    + https://github.com/Voultapher/sort-research-rs/blob/main/writeup/sort_safety/text.md
    + https://www.youtube.com/watch?v=rZ7QQWKP8Rk
- No dynamic stack allocation (`alloca`, VLAs)
- Panic unwinding overhead
  * panics involve stack unwinding and destructors so are definitely not free
  * need to check if items from Roman's talk apply: "Исключения C++ через призму компиляторных оптимизаций" (https://www.youtube.com/watch?v=ItemByR4PRg)
  * C++ has `-fno-exceptions`, is `panic=abort` same ?
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
- Forced variable initializations (especially large arrays)
  * https://blog.logrocket.com/understanding-inheritance-other-limitations-rust/

# Rust-specific optimization opportunities

Rust language also enables new, more aggressive optimizations.

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

# Conclusions

Ideally need some ballpark numbers here for different classes of programs

# Goal of the talk

Rust is defined as a safe, low-level, system programming language
directly competing with C++.

How much does it pay for safety in terms of performance ?

In this talk we
  - identify performance weak spots of Rust
  - propose countermeasures / performance best practices (?)

# Target conference

C++Russia 2026

# High-level plan

This talk is NOT about:
  - non-idiomatic code (SIMD, intrinsics, inline asm, `wrapping_add`, too many `unsafe`s, etc.)
    * need to compare "standard" Rust against C++
  - just comparing few random programs
    * not enough to draw conclusions
  - just looking at asm code
    * inefficiencies may be due to bug / NYI feature in LLVM
    * should check what is NYI and can never be implemented in LLVM optimizer
  - important missing features which are not directly perf-related:
    * custom allocators and placement new
    * ABI

Rust is similar to C++ :
  - system programming language
  - zero-cost abstractions
  - don't pay for what you don't use
  - supports low-level tuning
    * SIMD, inline asm, intrinsics (e.g. `__builtin_assume`, `__builtin_expect`)
  - same optimizer (LLVM)

Can we expect similar performance on idiomatic code ?
  - caveat: not comparing `HashMap` with `unordered_map` (C++ `unordered_map` is just too bad)

Some Rust's abstractions are NOT zero-cost (or at least less zero-cost than in C++) :
  - are by design more expensive than C++ equivalents
  - can not be fixed by more sophisticated optimizations

Rust performance overheads:
  - overflow is not UB in release => no signed overflow loop optimizations
  - all index accesses are checked
    * LLVM may not always remove them which will break autovec
    * need to investigate several common cases: LICM for index checks in loops, support for [inclusive](https://github.com/rust-lang/rust/issues/45222)/exclusive ranges, const/non-const bounds
    * fat slices
    * reslicing needed (see https://users.rust-lang.org/t/understanding-rusts-auto-vectorization-and-methods-for-speed-increase/84891/5)
  - UTF-8 strings
  - slower library defaults: [PRNG](https://users.rust-lang.org/t/julia-outperforms-rust-in-generating-a-vector-of-random-numbers/101624), [unbuffered IO](https://users.rust-lang.org/t/in-my-benchmark-i-found-rust-slower-than-c/71944/6) (need to use BufWriter)
  - no `alloca`
  - panic unwinding is costly
    * need to check if items from Roman's talk apply: "Исключения C++ через призму компиляторных оптимизаций" https://www.youtube.com/watch?v=ItemByR4PRg
    * C++ has `-fno-exceptions`, is panic=abort same ?
  - no type-based aliasing (`-fno-strict-aliasing`)
    * important for pointer operations in unsafe blocks
  - borrow checker limitations:
    * self-referential structs require refcounting
      + `Rc<RefCell<T>>`
      + `borrow_mut` checks may not be reliably LICM-ed from loops
      + graphs, what other important data structues ?
    * unable to take two mutable refs to different elements of std collections / slices
    * have to use indices (with runtime index checks penalty) instead of iterators
    * as a result, ALL high-performance data structures use unsafe code to skip borrow checker
  - `Option`/`Result` may be more expensive than `nullptr`
  - no `-ffast-math` (https://www.reddit.com/r/rust/comments/e5ge5k/rust_and_ffastmath/)
  - error codes vs. exceptions

How much performance can be regained using unsafe code ?
  - check what optimizations we can't express even with unsafe blocks

Rust performance improvements:
  - in some cases Rust allows more aggressive optimizations
  - move by default
    * also `Vec` is moved on `resize` at once, rather than by element
  - `restrict` by default
    * currently only applied at func boundaries
  - enum tag embegging and struct optimizations
    * analog of LLVM's `PointerIntPair`, `PointerSumType`, `PointerUnion`
    * https://users.rust-lang.org/t/documentation-of-null-pointer-optimization/58038
    * https://github.com/rust-lang/rfcs/issues/1230
  - zero-sized types
    * do not need EBO like C++
  - fearless concurrency
  - copy/move elision (?)
  - `Box` is more performant than `unique_ptr` (https://www.youtube.com/watch?v=rHIkrotSwcc&t=1261s)

How to deal with unsafe ?
  - idiomatic (safe) should still be main topic
  - need to mention cases where unsafe may help

# Materials

For each link need to
  * read/watch
  * categorize each reported problem / optimization suggestion and update our lists
  * extract useful examples
  * for blogposts also be sure to check comments, links and other Rust-performance-relevant posts on blog

Blog posts:
  - C++ comparisons:
    * C++ faster and safer by Rust: benchmarked by Yandex: https://habr.com/ru/articles/492410/
    * The relative performance of C and Rust: https://bcantrill.dtrace.org/2018/09/28/the-relative-performance-of-c-and-rust/
    * Speed of Rust vs C: https://kornel.ski/rust-c-speed
    * An Optimization That’s Impossible in Rust! https://tunglevo.com/note/an-optimization-thats-impossible-in-rust/
    * Rust превосходит по производительности C++ согласно результатам Benchmarks Game: https://habr.com/ru/articles/480608/
    * Rust vs. C++ на алгоритмических задачах: https://habr.com/ru/articles/344282/
    * Небезопасный Rust сложнее C: https://habr.com/ru/companies/ruvds/articles/858246/
  - Compiler:
    * Rust loves LLVM: https://www.youtube.com/watch?v=Kqz-umsAnk8 (https://llvm.org/devmtg/2024-10/slides/keynote/Popov-Rust_Heart_LLVM.pdf)
    * Rust and LLVM in 2021: https://llvm.org/devmtg/2021-02-28/slides/Patrick-rust-llvm.pdf
    * Unleash the Power of Auto-Vectorization in Rust with LLVM: https://www.luiscardoso.dev/blog/auto-vectorization/
    * Taking Advantage of Auto-Vectorization in Rust: https://www.nickwilcox.com/blog/autovec/ (also comments in https://www.reddit.com/r/rust/comments/gkq0op/taking_advantage_of_autovectorization_in_rust/)
    * Inspecting rustc LLVM optimization remarks using cargo-remark: https://kobzol.github.io/rust/cargo/2023/08/12/rust-llvm-optimization-remarks.html
      + need to run `cargo remark` on real projects
    * Improving crypto code in Rust using LLVM’s optnone: https://blog.trailofbits.com/2022/02/01/part-2-rusty-crypto/
    * Why Rust doesn't need a standard div_rem: An LLVM tale: https://codspeed.io/blog/why-rust-doesnt-need-a-standard-divrem (also comments in https://www.reddit.com/r/rust/comments/173wr86/why_rust_doesnt_need_a_standard_div_rem_an_llvm)
  - data structures:
    * Learn Rust With Entirely Too Many Linked Lists: https://rust-unofficial.github.io/too-many-lists/
  - Optimizations:
    * Aliasing in Rust: https://www.reddit.com/r/rust/comments/1ery9dy/aliasing_in_rust/
    * Unwind considered harmful? https://smallcultfollowing.com/babysteps/blog/2024/05/02/unwind-considered-harmful/
    * Rust’s iterators are inefficient, and here’s what we can do about it: https://medium.com/@veedrac/rust-is-slow-and-i-am-the-cure-32facc0fdcb
    * Nethercote's posts (!!!): https://blog.mozilla.org/nnethercote/category/rust/
    * http://troubles.md/abusing-rustc/
    * Можно ли доверить компилятору оптимизацию вашего кода? https://habr.com/ru/companies/timeweb/articles/759326/
    * Как избавиться от проверок выхода за границы: https://habr.com/ru/companies/otus/articles/718012/
    * Портируем декодер AV1 с С на Rust: https://habr.com/ru/companies/ruvds/articles/842970
    * Как я ускорила парсинг строк в serde_json на 20%: https://habr.com/ru/articles/838404/
    * Пошаговое повышение производительности алгоритма: https://habr.com/ru/articles/852974/
  - Field reports:
    * Leaving Rust gamedev after 3 years: https://loglog.games/blog/leaving-rust-gamedev/ (also comments in https://news.ycombinator.com/item?id=40172033 and https://habr.com/ru/articles/813597/)

User forum:
  * Rust vs C++ Theoretical Performance: https://users.rust-lang.org/t/rust-vs-c-theoretical-performance/4069/8
  * Rust-specific code optimisations vs other languages: https://users.rust-lang.org/t/rust-specific-code-optimisations-vs-other-languages/49663
  * Looking for help understanding Rust’s performance vs C++: https://users.rust-lang.org/t/looking-for-help-understanding-rusts-performance-vs-c/30469/27
  * Performance of array access vs C: https://users.rust-lang.org/t/performance-of-array-access-vs-c/43522/13
  * Looking for help understanding Rust’s performance vs C++: https://users.rust-lang.org/t/looking-for-help-understanding-rusts-performance-vs-c/30469/22
  * Rust newbie: Algorithm performance question: https://users.rust-lang.org/t/rust-newbie-algorithm-performance-question/47413/11
  * Why my Rust multithreaded solution is slow as compared: https://users.rust-lang.org/t/why-my-rust-multithreaded-solution-is-slow-as-compared-to-the-same-c-solution/95581
  * A performance problem compared with Julia: https://users.rust-lang.org/t/a-performance-problem-compared-with-julia/51871/18
  * Help comparing Rust vs Julia speed: https://users.rust-lang.org/t/help-comparing-rust-vs-julia-speed/54514/11
  * Optimizing linear algebra code: https://users.rust-lang.org/t/optimizing-linear-algebra-code/39433/14
  * Executable size and performance vs. C? https://users.rust-lang.org/t/executable-size-and-performance-vs-c/4496/30
  * Rust vs. C vs. Go runtime speed comparison: https://users.rust-lang.org/t/rust-vs-c-vs-go-runtime-speed-comparison/104107/13
  * Rust program has only 42% the speed of similar c++ program: https://users.rust-lang.org/t/rust-program-has-only-42-the-speed-of-similar-c-program/73738
  * We need to do better in the benchmarks game: https://users.rust-lang.org/t/we-need-to-do-better-in-the-benchmarks-game/7317/5
  * Performance issue with C-array like computation: https://users.rust-lang.org/t/performance-issue-with-c-array-like-computation-2-times-worst-than-naive-java/9807/49
  * Performance issue - High complexity code: https://users.rust-lang.org/t/performance-issue-high-complexity-code/40241/17
  * Performance question: https://users.rust-lang.org/t/performance-question/54977/8
  * Performance questions: https://users.rust-lang.org/t/performance-questions/45265
  * Simple Rust and C# performance comparison: https://users.rust-lang.org/t/simple-rust-and-c-performance-comparison/42970/3
  * Why is C++ still beating Rust at performance in some places? https://users.rust-lang.org/t/why-is-c-still-beating-rust-at-performance-in-some-places/95877/4
  * Rust-specific code optimisations vs other languages: https://users.rust-lang.org/t/rust-specific-code-optimisations-vs-other-languages/49663/9
  * Rust vs. C++: Fine-grained Performance: https://users.rust-lang.org/t/rust-vs-c-fine-grained-performance/4407
  * A good performance comparision C and Rust: https://users.rust-lang.org/t/a-good-performance-comparision-c-and-rust/5901/7
  * What kind of performance rust is trying to achieve? https://users.rust-lang.org/t/what-kind-of-performance-rust-is-trying-to-achieve/1674/4
  * Non-aliasing guarantees of &mut T and rustc optimization: https://users.rust-lang.org/t/non-aliasing-guarantees-of-mut-t-and-rustc-optimization/34386
  * Possible Rust-specific optimizations: https://users.rust-lang.org/t/possible-rust-specific-optimizations/79895/2 (also https://habr.com/ru/companies/beget/articles/842868/)
  * Auto-vectorization in Rust: https://users.rust-lang.org/t/auto-vectorization-in-rust/24379/14
  * Understanding Rusts Auto-Vectorization and Methods for speed: https://users.rust-lang.org/t/understanding-rusts-auto-vectorization-and-methods-for-speed-increase/84891/5 (reslicing technique)

Developer forum:
  * TODO: https://internals.rust-lang.org/c/compiler

This week in Rust:
  * TODO: https://this-week-in-rust.org/

Relevant Github issues:
  - Inefficient codegen when accessing a vector with literal indices: https://github.com/rust-lang/rust/issues/50759

# Where to find more materials

Google for
  - Rust gamedev problems
  - Rust inefficient data structures
  - Rust performance issues

Coding guidelines for big Rust projects
  - e.g. rustc dev guide
  - https://softwarepatternslexicon.com/patterns-rust/
  - The Rust Performance Book: https://nnethercote.github.io/perf-book/

Survey Github for innate (unfixable, by design) performance issues:
  - rejected opts: https://github.com/rust-lang/rust/issues?q=is%3Aissue%20state%3Aclosed%20reason%3Anot-planned%20label%3AI-slow
  - compiler RFCs: https://github.com/rust-lang/rust/issues?q=is%3Aissue%20label%3AT-compiler%20rfc
  - what else ?

Look at real code:
  - microbenchmarks
    * easy to analyze and demonstrate issues
    * do not show how common issue is in real code
  - algorithms
    * CS 101 e.g. sorts/trees
    * math e.g. matmul/FFT
    * relatively easy to collect ([benchmarks game](https://benchmarksgame-team.pages.debian.net/benchmarksgame/measurements/rust.html))
  - real production code
    * very hard to analyze
      + need methodology (e.g. first profile and study only hotspots)
    * concrete examples:
      * Eigen vs nalgebra
      * rustc
        + https://habr.com/ru/articles/539796/
      * regex
      * Servo (https://habr.com/ru/articles/274815/), Parity, Redox, Rusoto, Firefox
      * what else ?

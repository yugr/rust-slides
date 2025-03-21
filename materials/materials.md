Materials have been collected according to [collection methodology](materials/method.md).

Note that section split below is rather crude and may do more harm than good.
Refactor structure if you think it makes sense.
On the other hand, once all materials are analyzed we won't care about this file.

- TODO(gh-1) scan https://internals.rust-lang.org/c/compiler for relevant posts and add them to above sections
- TODO(gh-2) add more interesting issues from
  * rejected opts: https://github.com/rust-lang/rust/issues?q=is%3Aissue%20state%3Aclosed%20reason%3Anot-planned%20label%3AI-slow
  * compiler RFCs: https://github.com/rust-lang/rust/issues?q=is%3Aissue%20label%3AT-compiler%20rfc

# Coding guidelines

- Rustc development guide: https://rustc-dev-guide.rust-lang.org/
- Rust design patterns: https://softwarepatternslexicon.com/patterns-rust/
- Rust Performance Book (by Nethercote): https://nnethercote.github.io/perf-book/
  * pay attention to links at https://nnethercote.github.io/perf-book/bounds-checks.html
  * comments: https://www.reddit.com/r/rust/comments/jvmb8u/the_rust_performance_book/
  * additions: https://github.com/nnethercote/perf-book/issues
- Some general guidelines from Redox OS https://doc.redox-os.org/book/rusting-properly.html
- TODO(gh-3) survey [other projects](real-projects.md)

# C++ comparison

- C++ faster and safer by Rust: benchmarked by Yandex: https://habr.com/ru/articles/492410/
  * Assignee: yugr
  * Status: DONE (15m)
  * Problem: response to critique of Rust by Polukhin; they confirm that comparison of asm of microbenchmarks is pointless
  * More materials: no interesting mats in suggestions
- The relative performance of C and Rust: https://bcantrill.dtrace.org/2018/09/28/the-relative-performance-of-c-and-rust/
  * Assignee: yugr
  * Status: DONE (15m)
  * Problem: studies performance of Rust data structures vs. some custom C equivalents (irrelevant)
  * More materials: no performance-related materials found in blog
- Speed of Rust vs C: https://kornel.ski/rust-c-speed
  * Assignee: yugr
  * Status: DONE (50m)
  * Problem: basic comparison of Rust/C (not C++!) performance features; in particular
    + LLVM optimizer is the same
    + Rust misses `alloca`/`computed goto`
    + 64-bit offsets in Rust (so what ?)
    + Rust iterators allow more efficient codegen
    + UTF-8 strings are slower
    + no IO buffering by default
    + due to privacy control in Rust, libs may return their types by value (so that users can store them on stack) without disclosing library details
      - stack-allocated structs can be better optimized
      - this breaks ABI though
    + Rust can inline functions from stdlib (C++ can too)
    + Struct optimizations
    + Fearless concurrency
  * More materials: nothing on blog but some vibrant discussions in aggregators :
    + [Reddit](https://www.reddit.com/r/rust/comments/m427lj/speed_of_rust_vs_c/)
    + [HN](https://news.ycombinator.com/item?id=26443768)
    + [Another HN](https://news.ycombinator.com/item?id=39476941)
    + no new links found (hoorah !)
- An Optimization That’s Impossible in Rust! https://tunglevo.com/note/an-optimization-thats-impossible-in-rust/
  * Comments: https://www.reddit.com/r/rust/comments/1f87siw/an_optimization_thats_impossible_in_rust/
- Rust превосходит по производительности C++ согласно результатам Benchmarks Game: https://habr.com/ru/articles/480608/
  * Assignee: yugr
  * Status: DONE (15m)
  * Article itself just confirms Benchmarks Game results; an interesting discussion in comments about `unique_ptr`
  * More materials: added info about `unique_ptr` vs `Box` to features
- Rust vs. C++ на алгоритмических задачах: https://habr.com/ru/articles/344282/
  * Assignee: yugr
  * Status: DONE (10m)
  * Article compares C++ vs Rust on simple programs
  * More materials: nothing interesting in comments
- Safety vs Performance. A case study of C, C++ and Rust sort implementations: https://github.com/Voultapher/sort-research-rs/blob/main/writeup/sort_safety/text.md
  * Assignee: yugr
  * Status: DONE (10m)
  * Article benchmarks various sort implementations in Rust/C++ and their safety guarantees
  * Rust implementations also have to be memory-safe
  * Only relevant part is perf comparison (Rust wins by Nx)
  * More materials: NA
- Loop Performance in Rust: https://www.youtube.com/watch?v=E37rSIhWjso
  * Assignee: yugr
  * Status: DONE (50m)
  * Video discusses loop codegen :
    + autovec
    + lack of fast math
    + LLVM misopts
    + explicit SIMD
  * More materials: N/A
- Rust vs C++ Theoretical Performance: https://users.rust-lang.org/t/rust-vs-c-theoretical-performance/4069
  * Assignee: yugr
  * Status: DONE (30m)
  * Discussion about Rust potential improvements over C++:
    + niche optimization
    + shared refs guarantee immutability
    + aliasing
    + non-nullability of references
  * More materials: added some more linked mats and started looking at Shnatsel's posts
- Looking for help understanding Rust’s performance vs C++: https://users.rust-lang.org/t/looking-for-help-understanding-rusts-performance-vs-c/30469
  * Assignee: yugr
  * Status: DONE (15m)
  * Problem: matrix multiply code is slower than C++
  * Root cause: bounds checks can not be eliminated
  * Solution: suggested to construct custom slice or use `get_unchecked`
  * LLVM: can not be optimized (data struct is too complex: `Vec<Vec<f64>>`)
  * More materials: 
- Performance of array access vs C: https://users.rust-lang.org/t/performance-of-array-access-vs-c/43522
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: code slower than C++ equivalent
  * Root cause: bounds checks in simple pattern
  * Solution: rewrite to allow LLVM to better optimize it
  * LLVM: most likely could be fixed
  * More materials: N/A
- Executable size and performance vs. C? https://users.rust-lang.org/t/executable-size-and-performance-vs-c/4496
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: code slower than C++ equivalent
  * Root cause: most likely bounds checks
  * Solution: rewrite to use iterators
  * LLVM: most likely have been fixed (the post is very old)
  * More materials: N/A
- Rust vs. C vs. Go runtime speed comparison: https://users.rust-lang.org/t/rust-vs-c-vs-go-runtime-speed-comparison/104107
- Performance issue with C-array like computation: https://users.rust-lang.org/t/performance-issue-with-c-array-like-computation-2-times-worst-than-naive-java/9807
- Simple Rust and C# performance comparison: https://users.rust-lang.org/t/simple-rust-and-c-performance-comparison/42970
- Why is C++ still beating Rust at performance in some places? https://users.rust-lang.org/t/why-is-c-still-beating-rust-at-performance-in-some-places/95877
- Rust vs. C++: Fine-grained Performance: https://users.rust-lang.org/t/rust-vs-c-fine-grained-performance/4407
- A good performance comparision C and Rust: https://users.rust-lang.org/t/a-good-performance-comparision-c-and-rust/5901/7
- Rust-specific code optimisations vs other languages: https://users.rust-lang.org/t/rust-specific-code-optimisations-vs-other-languages/49663
- How to speed up this rust code? I’m measuring a 30% slowdown versus the C++ version: https://users.rust-lang.org/t/how-to-speed-up-this-rust-code-im-measuring-a-30-slowdown-versus-the-c-version/1488
- Goals and priorities for C++: https://internals.rust-lang.org/t/goals-and-priorities-for-c/12031/32 (some points on Rust perf features like lack of fast-math or move semantics)
- Zero cost abstractions: Rust vs C++: https://www.rottedfrog.co.uk/?p=24
  * Assignee: yugr
  * Status: DONE (20m)
  * Article compares performance of `unique_ptr` vs `Box`
    + code is larger to support panic unwinding
    + LLVM does not optimize dead code after tail call
    + significantly more code to support panicking (but it can be removed with `-C panic=abort`)
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/gqw2gj/zero_cost_abstractions_rust_vs_c/)
    + no more interesting posts in "performance site:https://www.rottedfrog.co.uk"
- Evaluating Languages for Bioinformatics: https://github.com/rjray/mscs-thesis-project
  * Assignee: yugr
  * Status: DONE (5m)
  * Thesis investigates applicability of diff. languages to bioinformatics
  * He runs several domain-relevant benchmarks and compares results, without any analysis
  * Conclusion: not relevant
  * More materials: none
- Rust is now overall faster than C in benchmarks: https://www.reddit.com/r/rust/comments/kpqmrh/rust_is_now_overall_faster_than_c_in_benchmarks/
  * Assignee: yugr
  * Status: DONE (5m)
  * Just general rant about Benchmarks Game irrelevance
  * More materials: none
- Rust Optimizations That C++ Can't Do: https://robert.ocallahan.org/2017/04/rust-optimizations-that-c-cant-do_5.html
  * Assignee: yugr
  * Status: in progress
- What makes Rust faster than C/C++? https://www.reddit.com/r/rust/comments/px72r1/what_makes_rust_faster_than_cc/
- Why ISN'T Rust faster than C? https://www.reddit.com/r/rust/comments/1at3r6d/why_isnt_rust_faster_than_c_given_it_can_leverage/
- Why is Rust not able to optimize this? https://www.reddit.com/r/rust/comments/181tp1a/why_is_rust_not_able_to_optimize_this/ (signed overflow)
- Is bound checking the only runtime cost of Rust? https://users.rust-lang.org/t/is-bound-checking-the-only-runtime-cost-of-rust/66661
- Why is Rust slightly slower than C? https://news.ycombinator.com/item?id=20944403
- Rewrite the VP9 codec library in Rust: https://news.ycombinator.com/item?id=39537735
- Is C++ more performant than Rust? https://www.reddit.com/r/cpp/comments/17zaiu6/is_c_more_performant_than_rust/
- Why Not Rust ? https://github.com/guevara/read-it-later/issues/8279

# Rust-specific opts

- Non-aliasing guarantees of &mut T and rustc optimization: https://users.rust-lang.org/t/non-aliasing-guarantees-of-mut-t-and-rustc-optimization/34386
- Possible Rust-specific optimizations: https://users.rust-lang.org/t/possible-rust-specific-optimizations/79895/2 (also https://habr.com/ru/companies/beget/articles/842868/)
- What kind of performance rust is trying to achieve? https://users.rust-lang.org/t/what-kind-of-performance-rust-is-trying-to-achieve/1674

# Compiler codegen

- Rust under the hood: https://www.youtube.com/watch?v=L8caNpK3Shs
- Rust loves LLVM: https://www.youtube.com/watch?v=Kqz-umsAnk8 (https://llvm.org/devmtg/2024-10/slides/keynote/Popov-Rust_Heart_LLVM.pdf)
- Rust and LLVM in 2021: https://llvm.org/devmtg/2021-02-28/slides/Patrick-rust-llvm.pdf
- Inspecting rustc LLVM optimization remarks using cargo-remark: https://kobzol.github.io/rust/cargo/2023/08/12/rust-llvm-optimization-remarks.html
  * need to run `cargo remark` on real projects
- Improving crypto code in Rust using LLVM’s optnone: https://blog.trailofbits.com/2022/02/01/part-2-rusty-crypto/
- Why Rust doesn't need a standard div_rem: An LLVM tale: https://codspeed.io/blog/why-rust-doesnt-need-a-standard-divrem (also comments in https://www.reddit.com/r/rust/comments/173wr86/why_rust_doesnt_need_a_standard_div_rem_an_llvm)
- Asm snippets: https://www.eventhelix.com/rust/
- Battle Of The Backends: Rust vs. Go vs. C# vs. Kotlin - inovex GmbH: https://www.inovex.de/de/blog/rust-vs-go-vs-c-vs-kotlin
  * Assignee: yugr
  * Status: DONE (0m)
  * Problem: just comparing performance of some network app (no analysis)
- How much does Rust's bounds checking actually cost? https://blog.readyset.io/bounds-checks/
  * Assignee: yugr
  * Status: DONE (75m)
  * Problem: investigates overhead of bounds checking operations
  * Solution:
    + experiments with replacing accesses with `get_unchecked` and modifying compiler (!)
    + does not provide any analysis of results, asm, etc.
    + no noticeable changes on her machine but up to 4x according to comments on Reddit
  * More materials:
    + a lot of comments on [Reddit](https://www.reddit.com/r/rust/comments/z92vid/measuring_how_much_rusts_bounds_checking_actually/), [Reddit](https://www.reddit.com/r/programming/comments/z9hjpk/how_much_does_rusts_bounds_checking_actually_cost/) and [HackerNews](https://news.ycombinator.com/item?id=33805419)
    + added new materials
- A cool Rust optimization story: https://quickwit.io/blog/search-a-sorted-block
- Inefficient codegen when accessing a vector with literal indices: https://github.com/rust-lang/rust/issues/50759
  * Assignee: yugr
  * Status: DONE (20-30m)
  * Problem: repetative indexing checks when Vec/slice is accessed multiple times
  * Root cause: Rust has to preserve order of checks (for not so clear reason)
  * Solution: can be worked around via `assert!` hint (looks like generic solution for such situations)
  * LLVM: no good/generic way to solve this in LLVM
  * More materials: NA
- Costs of iterators and Zero Cost Abstractions in Rust: https://github.com/mike-barber/rust-zero-cost-abstractions
  * pay attention to this post, it directly intersects with our topic
- Addressing Rust optimization failures in LLVM: http://www.khei4.com/gsoc2023/
  * Assignee: yugr
  * Status: DONE (5m)
  * Just solved some LLVM bugs, no generalizations
  * More materials: N/A
- Why does the Rust compiler not optimize code assuming that two mutable references cannot alias? https://stackoverflow.com/questions/57259126/why-does-the-rust-compiler-not-optimize-code-assuming-that-two-mutable-reference
- Square powers not being fully optimized? https://www.reddit.com/r/rust/comments/exojhk/square_powers_not_being_fully_optimized/
  * Assignee: yugr
  * Status: postponed (awaiting response, 20m)
  * Problem: `2.pow(n)` not optimized to `1 << n`
  * Root cause: missing optimization in LLVM
  * Solution: was fixed in LLVM in [upstream #47234](https://github.com/rust-lang/rust/issues/47234) but the reverted due to [upstream #120537](https://github.com/rust-lang/rust/issues/120537); current status unclear so I asked in first issue
  * More materials: no interesting mats in suggestions
- Why isn't the for loop optimized better (in this one example)? https://www.reddit.com/r/rust/comments/15tvuio/why_isnt_the_for_loop_optimized_better_in_this/
  * Assignee: yugr
  * Status: DONE (30m)
  * Problem: loop slowdown when using inclusive ranges
  * Root cause: inclusive ranges are slower by design (explained in comments)
  * Solution: replace with exclusive range with explicit addition
  * LLVM: one of commenters suggest how it can be fixed in LLVM (via loop splitting)
  * More materials: no new mats in suggestions
- Assembly examples of missed Rust compiler optimizations: https://www.reddit.com/r/rust/comments/14zhb0s/assembly_examples_of_missed_rust_compiler/
- Does the compiler optimize moves? https://www.reddit.com/r/rust/comments/ykku69/does_the_compiler_optimize_moves/
  * this should be a dedicated perf issue
- Rust `[#inline]` annotations discussion https://github.com/rust-lang/hashbrown/pull/119
  * Assignee: zakhar
  * Status: DONE (15m)
  * Discussion mostly about `[#inline]` effect on compile time
  * Not our topic
  * More materials: N/A
- Check for Integer Overflow by Default: https://github.com/rust-lang/rust/issues/47739
- Myths and Legends about Integer Overflow in Rust: https://huonw.github.io/blog/2016/04/myths-and-legends-about-integer-overflow-in-rust/
- How are bounds checks optimized away? https://users.rust-lang.org/t/how-are-bounds-checks-optimized-away/91737
- Rust's Vec indexing is bound-checked by default: https://news.ycombinator.com/item?id=30867188
- Iterators and eliminating all runtime bounds checks: https://users.rust-lang.org/t/iterators-and-eliminating-all-runtime-bounds-checks/13935
- How to zip two slices efficiently: https://users.rust-lang.org/t/how-to-zip-two-slices-efficiently/2048
- How to avoid bounds checks in Rust without unsafe: https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e
- Inline In Rust: Inline In Rust: https://matklad.github.io/2021/07/09/inline-in-rust.html

# Data structures performance

- Learn Rust With Entirely Too Many Linked Lists: https://rust-unofficial.github.io/too-many-lists/
- Nine Rules for Creating Fast, Safe, and Compatible Data Structures in Rust:
  * https://towardsdatascience.com/nine-rules-for-creating-fast-safe-and-compatible-data-structures-in-rust-part-1-c0973092e0a3
  * https://towardsdatascience.com/nine-rules-for-creating-fast-safe-and-compatible-data-structures-in-rust-part-2-da5e6961a0b7
- https://dev.to/arunanshub/self-referential-structs-in-rust-33cm

# Vectorization

- Unleash the Power of Auto-Vectorization in Rust with LLVM: https://www.luiscardoso.dev/blog/auto-vectorization/
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: there is not problem actually, the article just illustrates how autovec works, etc.
  * More materials: no more interesting mats on this blog
- Taking Advantage of Auto-Vectorization in Rust: https://www.nickwilcox.com/blog/autovec/ (also comments in https://www.reddit.com/r/rust/comments/gkq0op/taking_advantage_of_autovectorization_in_rust/)
- Nine Rules for SIMD Acceleration of Your Rust Code:
  * https://towardsdatascience.com/nine-rules-for-simd-acceleration-of-your-rust-code-part-1-c16fe639ce21
  * https://medium.com/towards-data-science/nine-rules-for-simd-acceleration-of-your-rust-code-part-2-6a104b3be6f3
- Taming Floating-Point Sums: https://orlp.net/blog/taming-float-sums/
- Auto-vectorization in Rust: https://users.rust-lang.org/t/auto-vectorization-in-rust/24379
- Understanding Rusts Auto-Vectorization and Methods for speed: https://users.rust-lang.org/t/understanding-rusts-auto-vectorization-and-methods-for-speed-increase/84891 (reslicing technique)
- We need to do better in the benchmarks game: https://users.rust-lang.org/t/we-need-to-do-better-in-the-benchmarks-game/7317
- Performance questions: https://users.rust-lang.org/t/performance-questions/45265
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: C++ version was significantly faster
  * Root cause: not determined (OP didn't continue on thread)
  * More materials: nothing generic enough in suggested articles
- bounds-check-cost: https://github.com/matklad/bounds-check-cost
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: studies influence of bounds checks on performance
  * Root cause: matklad concludes that main cost is due to blocked autovec and checks themselves are cheap
  * Solution: N/A (pure analysis)
  * LLVM: N/A (pure analysis)
  * More materials: not checked (~100 non-fork Rust repos)
- Nine Rules for SIMD Acceleration of Your Rust Code (Part 1): https://www.reddit.com/r/rust/comments/18hj1m6/nine_rules_for_simd_acceleration_of_your_rust/
- Taking Advantage of Auto-Vectorization in Rust: https://www.nickwilcox.com/blog/autovec/
- Auto-Vectorization for Newer Instruction Sets in Rust: https://www.nickwilcox.com/blog/autovec2/
- Can You Trust a Compiler to Optimize Your Code? https://matklad.github.io/2023/04/09/can-you-trust-a-compiler-to-optimize-your-code.html
  * Comments in https://www.reddit.com/r/rust/comments/15f5p94/can_you_trust_a_compiler_to_optimize_your_code/
- Iterator::max with reference-type items cannot leverage SIMD instructions: https://github.com/rust-lang/rust/issues/106539
- SIMD Vector/Slice/Chunk Addition: https://www.reddit.com/r/rust/comments/154vowr/simd_vectorslicechunk_addition/
- simd-itertools: simd-accelerated iterators for "find", "filter", "contains" and many more: https://www.reddit.com/r/rust/comments/1e3ps2a/simditertools_simdaccelerated_iterators_for_find/
- Memory-safe PNG decoders now vastly outperform C PNG libraries: https://www.reddit.com/r/rust/comments/1ha7uyi/memorysafe_png_decoders_now_vastly_outperform_c/

# Manual optimizations

- Aliasing in Rust: https://www.reddit.com/r/rust/comments/1ery9dy/aliasing_in_rust/
- Rust’s iterators are inefficient, and here’s what we can do about it: https://medium.com/@veedrac/rust-is-slow-and-i-am-the-cure-32facc0fdcb
- (!) Nethercote's posts: https://blog.mozilla.org/nnethercote/category/rust/
  * Nethercote is top industry expert, need to pay close attention to his posts
- (!) Moar Nethercote's posts: https://nnethercote.github.io/
- http://troubles.md/abusing-rustc/
- Можно ли доверить компилятору оптимизацию вашего кода? https://habr.com/ru/companies/timeweb/articles/759326/
- Как избавиться от проверок выхода за границы: https://habr.com/ru/companies/otus/articles/718012/
- Портируем декодер AV1 с С на Rust: https://habr.com/ru/companies/ruvds/articles/842970
- Как я ускорила парсинг строк в serde_json на 20%: https://habr.com/ru/articles/838404/
- Пошаговое повышение производительности алгоритма: https://habr.com/ru/articles/852974/
- Unnecessary Optimization in Rust: https://emschwartz.me/unnecessary-optimization-in-rust-hamming-distances-simd-and-auto-vectorization/
- Improve an algorithm performance step by step: https://blog.mapotofu.org/blogs/rabitq-bench/
- Bringing runtime checks to compile time in Rust: https://ktkaufman03.github.io/blog/2023/04/20/rust-compile-time-checks
- Optimization story - quantum mechanics simulation speedup: https://tinkering.xyz/fmo-optimization-story
- Benchmarking and Optimization of Rust Libraries by Paul Mason: https://www.youtube.com/watch?v=d2ZQ9-4ZJmQ&t=749s
- Rust newbie: Algorithm performance question: https://users.rust-lang.org/t/rust-newbie-algorithm-performance-question/47413
- Why my Rust multithreaded solution is slow as compared: https://users.rust-lang.org/t/why-my-rust-multithreaded-solution-is-slow-as-compared-to-the-same-c-solution/95581
- A performance problem compared with Julia: https://users.rust-lang.org/t/a-performance-problem-compared-with-julia/51871
- Help comparing Rust vs Julia speed: https://users.rust-lang.org/t/help-comparing-rust-vs-julia-speed/54514
- Optimizing linear algebra code: https://users.rust-lang.org/t/optimizing-linear-algebra-code/39433
- Rust program has only 42% the speed of similar c++ program: https://users.rust-lang.org/t/rust-program-has-only-42-the-speed-of-similar-c-program/73738
- Performance issue - High complexity code: https://users.rust-lang.org/t/performance-issue-high-complexity-code/40241
- Performance question: https://users.rust-lang.org/t/performance-question/54977
- Rust performance help (convolution): https://users.rust-lang.org/t/rust-performance-help-convolution/44075
- Optimization comparison: Vec vs array and for vs while: https://internals.rust-lang.org/t/optimization-comparison-vec-vs-array-and-for-vs-while/16410
- Performance optimization, and how to do it wrong: https://genna.win/blog/convolution-simd/
  * comments: https://www.reddit.com/r/rust/comments/1j2iqhq/performance_optimization_and_how_to_do_it_wrong/
- Code critique/review request: https://www.reddit.com/r/learnrust/comments/xllzqm/code_critiquereview_request/ (comments)
- When Zero Cost Abstractions Aren’t Zero Cost: https://www.reddit.com/r/rust/comments/p0ul6b/when_zero_cost_abstractions_arent_zero_cost/
- Achieving warp speed with Rust: https://gist.github.com/jFransham/369a86eff00e5f280ed25121454acec1
  * pay attention to `assert` hint
- From 48s to 5s - optimizing a 350 line raytracer in Rust: https://medium.com/@cfsamson/from-48s-to-5s-optimizing-a-350-line-pathtracer-in-rust-191ab4a1a412
- Using break in for loop takes even 100ms in release mode: https://www.reddit.com/r/rust/comments/1738kd7/using_break_in_for_loop_takes_even_100ms_in/
  * overhead of consuming iterators
- 5x Slower than Go? Optimizing Rust Protobuf Decoding Performance: https://www.greptime.com/blogs/2024-04-09-rust-protobuf-performance
- Rust Performance Pitfalls: https://llogiq.github.io/2017/06/01/perf-pitfalls.html
- Where should I start if I want to squeeze out as much performance as I can from my rust code? https://www.reddit.com/r/rust/comments/bb5lnj/where_should_i_start_if_i_want_to_squeeze_out_as/
- How to avoid bounds checks in Rust: https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e
  * this article is very important for bounds checking part
  * comments: https://www.reddit.com/r/rust/comments/10edmjf/how_to_avoid_bounds_checks_in_rust_without_unsafe/
- Unnecessary Optimization in Rust: https://www.reddit.com/r/rust/comments/1hk0bry/unnecessary_optimization_in_rust_hamming/
  * check comments
- From 'Very Fast' to '~Fastest': Helping rust unleash compiler optimizations: https://blog.anubhab.me/tech/optimizing-diff-match-patch/
  * comments in https://www.reddit.com/r/rust/comments/1hsnnat/40_boost_in_text_diff_flow_just_by_facilitating/
- Example of loop rewrite for vectorization https://github.com/dropbox/rust-brotli/blob/238c9c539b446d7d980e0a50795752c45dd3359e/src/enc/static_dict.rs lines 122 and 131
- Discussion about explicit SIMD in Rust https://internals.rust-lang.org/t/getting-explicit-simd-on-stable-rust/4380/133
- Optimizing rav1d, an AV1 Decoder in Rust: https://www.memorysafety.org/blog/rav1d-performance-optimization/
  * comments in https://www.reddit.com/r/rust/comments/1fdzu7z/optimizing_rav1d_an_av1_decoder_in_rust/
- Porting C to Rust for a Fast and Safe AV1 Media Decoder: https://www.memorysafety.org/blog/porting-c-to-rust-for-av1/
  * this contains example of efficient implementation of self-referential struct
- Safe elimination of unnecessary bound checks: https://www.reddit.com/r/rust/comments/1iqev5s/safe_elimination_of_unnecessary_bound_checks/
- Rust loop speed: https://www.reddit.com/r/rust/comments/1aumq2h/rust_loop_speed/
- Why is this functional version faster than my for loop? https://www.reddit.com/r/rust/comments/xtiqj8/why_is_this_functional_version_faster_than_my_for/
- Iterators vs index loops performance: https://users.rust-lang.org/t/iterators-vs-index-loops-performance/52131
- Performance difference between iterator and for loop: https://users.rust-lang.org/t/performance-difference-between-iterator-and-for-loop/50254
- Performance of iterator over for-loops without boundry check: https://users.rust-lang.org/t/performance-of-iterator-over-for-loops-without-boundry-checks/96162
- Are iterators even efficient? https://users.rust-lang.org/t/are-iterators-even-efficient/36050
- Iter with step_by(2) performs slowly: https://github.com/rust-lang/rust/issues/59281
- What additional performance overhead does the use of iterators: https://internals.rust-lang.org/t/what-additional-performance-overhead-does-the-use-of-iterators-and-closures-cause/20296
- We all know `iter` is faster than `loop`, but why: https://users.rust-lang.org/t/we-all-know-iter-is-faster-than-loop-but-why/51486
- Why for_each is much faster than for loop in release mode: https://stackoverflow.com/questions/76091417/why-for-each-is-much-faster-than-for-loop-in-release-mode-cargo-run-r
- Huge performance gap in simple loop. Explanations? https://www.reddit.com/r/rust/comments/11f00kc/huge_performance_gap_in_simple_loop_explanations/
- Iterator::fold is a little slow compared to bare loop: https://github.com/rust-lang/rust/issues/76725

# Panics

- Rust panics under the hood: https://fractalfir.github.io/generated_html/rustc_codegen_clr_v0_2_1.html
  * Assignee: yugr
  * Status: DONE (15m)
  * Problem: just explanation of how panics were implemented in Rust CLR
  * Root cause: N/A
  * Solution: N/A
  * LLVM: N/A
  * More materials: no perf-relevant materials on blog (author mainly concerned with codegen for CLR)
- Unwind considered harmful? https://smallcultfollowing.com/babysteps/blog/2024/05/02/unwind-considered-harmful/
  * Assignee: yugr
  * Status: DONE (15m)
  * Problem: panics introduce perf/size overheads and complicate some aspects of Rust programming
  * Root cause: for perf/size they list landing pads and complicating compiler analyses
  * Solution: suggest to (partially) remove panics from language
  * LLVM: N/A
  * More materials: no perf-related materials in past years (mainly async Rust)
- Исключения C++ через призму компиляторных оптимизаций: https://www.youtube.com/watch?v=ItemByR4PRg
  * Assignee: yugr
  * Status: DONE (50m)
  * Problem: C++ code is less performant than C even if exceptions are not thrown
  * Root cause:
    + discussion starts at 16:20
    + more complex CFGs
    + fewer peephole opportunities
    + a lot of optimizations are (simplistically) disabled (this is also relevant for Rust !)
  * Solution: `noexcept`, `-fno-exceptions`
  * LLVM:
    + PruneEH pass already exists and should be enabled for Rust
    + ideally need to improve exceptions support in common opts (this would benefit C++ as well)
  * More materials: no links in video
- Zero-cost exceptions aren’t actually zero cost: https://devblogs.microsoft.com/oldnewthing/20220228-00/?p=106296
  * Assignee: yugr
  * Status: DONE (15m)
  * Problem: ditto
  * Root cause: article is too vague, it gives some ideas about what optimizations are disabled but then author retracts them in comments
  * Solution: N/A
  * LLVM: N/A
  * More materials: added P2544R0 link
- C++ exceptions are becoming more and more problematic: https://open-std.org/JTC1/SC22/WG21/docs/papers/2022/p2544r0.html

# Unsafe

- (!) Being Fair about Memory Safety and Performance: https://www.thecodedmessage.com/posts/unsafe/
  * need to be super-attentive to this post, this may be key to how we treat unsafe in our talk
- Implementing a VM: how unsafe should I go? https://www.reddit.com/r/rust/comments/n8yy7z/implementing_a_vm_how_unsafe_should_i_go/
- Good example of high performance Rust project without unsafe code? https://www.reddit.com/r/rust/comments/we91es/good_example_of_high_performance_rust_project/
- How do you all think about the `unsafe` vs zero-cost trade off? https://www.reddit.com/r/rust/comments/f5wgsn/how_do_you_all_think_about_the_unsafe_vs_zerocost/
- Unsafe Rust is Harder Than C: https://www.reddit.com/r/rust/comments/1gbqy6c/unsafe_rust_is_harder_than_c/
  * Russian translation: https://habr.com/ru/companies/ruvds/articles/858246/

# Code size

- Minimizing Rust Binary Size: https://github.com/johnthagen/min-sized-rust
  * Assignee: yugr
  * Status: DONE (30m)
  * Problem: Rust binaries are significantly larger
  * Root cause: there is a set of known causes (lack of ABI being the main)
  * Solution: all workarounds are known, added them to feature
  * LLVM: N/A
  * More materials: surveyed all links dating back to 2020 (incl.) and addded them to feature
- Tighten Rust’s Belt: Shrinking Embedded Rust Binaries: https://dl.acm.org/doi/pdf/10.1145/3519941.3535075
  * Assignee: yugr
  * Status: DONE (40m)
  * Problem: same as above
  * Root causes: save as above (+ also `.bss` problem with enum discriminators)
  * Solution: same as above
  * LLVM: paper suggests some optimizations: panic locations size (added to feature), devirtualization and interface minimization (do not look very promising so didn't copy them)
  * More materials (in "Related work"):
    + "Using C++ Efficiently In Embedded Applications" - nothing interesting
    + "RustyGecko - Developing Rust on Bare-Metal" - no deep comparison with C

# Other

- Leaving Rust gamedev after 3 years: https://loglog.games/blog/leaving-rust-gamedev/ (also comments in https://news.ycombinator.com/item?id=40172033 and https://habr.com/ru/articles/813597/)
- Why I hate Rust programming language? https://www.reddit.com/r/programming/comments/n9l68o/why_i_hate_rust_programming_language/ (comments)
- Rust inadequate for text compression codecs? https://news.ycombinator.com/item?id=43295908
- Rust: Not So Great For Codec Implementing: https://codecs.multimedia.cx/2017/07/rust-not-so-great-for-codec-implementing/
  * Assignee: zakhar
  * Status: DONE (80m)
  * Problem: Borrow-checker limitations, not enough allocation control, weak macro system
  * Solution: Wait until all the RFCs fixing these problems are implemented
  * More materials:
    + rust-brotli rewrite for vectorization example
    + Why you should, actually, rewrite some of it in Rust
    + Discussion about explicit SIMD in Rust
    + Reddit comments to the same post (https://codecs.multimedia.cx/2017/07/rust-not-so-great-for-codec-implementing/)
- Reddit comments to 'Rust: Not So Great For Codec Implementing' https://www.reddit.com/r/rust/comments/6qv2s5/rust_not_so_great_for_codec_implementing/
- Why you should, actually, rewrite some of it in Rust https://news.ycombinator.com/item?id=14753201

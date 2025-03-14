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
- Some general guidelines from Redox OS https://doc.redox-os.org/book/rusting-properly.html
- TODO(gh-3) survey [other projects](real-projects.md)

# C++ comparison

- C++ faster and safer by Rust: benchmarked by Yandex: https://habr.com/ru/articles/492410/
- The relative performance of C and Rust: https://bcantrill.dtrace.org/2018/09/28/the-relative-performance-of-c-and-rust/
- Speed of Rust vs C: https://kornel.ski/rust-c-speed
- An Optimization That’s Impossible in Rust! https://tunglevo.com/note/an-optimization-thats-impossible-in-rust/
  * Comments: https://www.reddit.com/r/rust/comments/1f87siw/an_optimization_thats_impossible_in_rust/
- Rust превосходит по производительности C++ согласно результатам Benchmarks Game: https://habr.com/ru/articles/480608/
- Rust vs. C++ на алгоритмических задачах: https://habr.com/ru/articles/344282/
- Небезопасный Rust сложнее C: https://habr.com/ru/companies/ruvds/articles/858246/
- Safety vs Performance. A case study of C, C++ and Rust sort implementations: https://github.com/Voultapher/sort-research-rs/blob/main/writeup/sort_safety/text.md
- Loop Performance in Rust: https://www.youtube.com/watch?v=E37rSIhWjso
- Rust vs C++ Theoretical Performance: https://users.rust-lang.org/t/rust-vs-c-theoretical-performance/4069/8
- Looking for help understanding Rust’s performance vs C++: https://users.rust-lang.org/t/looking-for-help-understanding-rusts-performance-vs-c/30469/27
- Performance of array access vs C: https://users.rust-lang.org/t/performance-of-array-access-vs-c/43522/13
- Looking for help understanding Rust’s performance vs C++: https://users.rust-lang.org/t/looking-for-help-understanding-rusts-performance-vs-c/30469/22
- Executable size and performance vs. C? https://users.rust-lang.org/t/executable-size-and-performance-vs-c/4496/30
- Rust vs. C vs. Go runtime speed comparison: https://users.rust-lang.org/t/rust-vs-c-vs-go-runtime-speed-comparison/104107/13
- Performance issue with C-array like computation: https://users.rust-lang.org/t/performance-issue-with-c-array-like-computation-2-times-worst-than-naive-java/9807/49
- Simple Rust and C# performance comparison: https://users.rust-lang.org/t/simple-rust-and-c-performance-comparison/42970/3
- Why is C++ still beating Rust at performance in some places? https://users.rust-lang.org/t/why-is-c-still-beating-rust-at-performance-in-some-places/95877/4
- Rust vs. C++: Fine-grained Performance: https://users.rust-lang.org/t/rust-vs-c-fine-grained-performance/4407
- A good performance comparision C and Rust: https://users.rust-lang.org/t/a-good-performance-comparision-c-and-rust/5901/7
- Rust-specific code optimisations vs other languages: https://users.rust-lang.org/t/rust-specific-code-optimisations-vs-other-languages/49663
- Rust-specific code optimisations vs other languages: https://users.rust-lang.org/t/rust-specific-code-optimisations-vs-other-languages/49663/9
- How to speed up this rust code? I’m measuring a 30% slowdown versus the C++ version: https://users.rust-lang.org/t/how-to-speed-up-this-rust-code-im-measuring-a-30-slowdown-versus-the-c-version/1488
- Goals and priorities for C++: https://internals.rust-lang.org/t/goals-and-priorities-for-c/12031/32 (some points on Rust perf features like lack of fast-math or move semantics)
- Zero cost abstractions: Rust vs C++: https://www.rottedfrog.co.uk/?p=24
- Evaluating Languages for Bioinformatics: https://github.com/rjray/mscs-thesis-project
- Rust is now overall faster than C in benchmarks: https://www.reddit.com/r/rust/comments/kpqmrh/rust_is_now_overall_faster_than_c_in_benchmarks/
- Rust Optimizations That C++ Can't Do: https://robert.ocallahan.org/2017/04/rust-optimizations-that-c-cant-do_5.html
- What makes Rust faster than C/C++? https://www.reddit.com/r/rust/comments/px72r1/what_makes_rust_faster_than_cc/
- Why ISN'T Rust faster than C? https://www.reddit.com/r/rust/comments/1at3r6d/why_isnt_rust_faster_than_c_given_it_can_leverage/
- Why is Rust not able to optimize this? https://www.reddit.com/r/rust/comments/181tp1a/why_is_rust_not_able_to_optimize_this/ (signed overflow)

# Rust-specific opts

- Non-aliasing guarantees of &mut T and rustc optimization: https://users.rust-lang.org/t/non-aliasing-guarantees-of-mut-t-and-rustc-optimization/34386
- Possible Rust-specific optimizations: https://users.rust-lang.org/t/possible-rust-specific-optimizations/79895/2 (also https://habr.com/ru/companies/beget/articles/842868/)
- What kind of performance rust is trying to achieve? https://users.rust-lang.org/t/what-kind-of-performance-rust-is-trying-to-achieve/1674/4

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
- How much does Rust's bounds checking actually cost?: https://blog.readyset.io/bounds-checks/
  * comments in https://news.ycombinator.com/item?id=33805419
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
- Auto-vectorization in Rust: https://users.rust-lang.org/t/auto-vectorization-in-rust/24379/14
- Understanding Rusts Auto-Vectorization and Methods for speed: https://users.rust-lang.org/t/understanding-rusts-auto-vectorization-and-methods-for-speed-increase/84891/5 (reslicing technique)
- We need to do better in the benchmarks game: https://users.rust-lang.org/t/we-need-to-do-better-in-the-benchmarks-game/7317/5
- Performance questions: https://users.rust-lang.org/t/performance-questions/45265
- bounds-check-cost: https://github.com/matklad/bounds-check-cost
- Nine Rules for SIMD Acceleration of Your Rust Code (Part 1): https://www.reddit.com/r/rust/comments/18hj1m6/nine_rules_for_simd_acceleration_of_your_rust/
- Taking Advantage of Auto-Vectorization in Rust: https://www.nickwilcox.com/blog/autovec/
- Auto-Vectorization for Newer Instruction Sets in Rust: https://www.nickwilcox.com/blog/autovec2/
- Can You Trust a Compiler to Optimize Your Code? https://matklad.github.io/2023/04/09/can-you-trust-a-compiler-to-optimize-your-code.html
  * Comments in https://www.reddit.com/r/rust/comments/15f5p94/can_you_trust_a_compiler_to_optimize_your_code/
- Iterator::max with reference-type items cannot leverage SIMD instructions: https://github.com/rust-lang/rust/issues/106539

# Manual optimizations

- Aliasing in Rust: https://www.reddit.com/r/rust/comments/1ery9dy/aliasing_in_rust/
- Rust’s iterators are inefficient, and here’s what we can do about it: https://medium.com/@veedrac/rust-is-slow-and-i-am-the-cure-32facc0fdcb
- Nethercote's posts: https://blog.mozilla.org/nnethercote/category/rust/
  * Nethercote is top industry expert, need to pay close attention to his posts
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
- Rust newbie: Algorithm performance question: https://users.rust-lang.org/t/rust-newbie-algorithm-performance-question/47413/11
- Why my Rust multithreaded solution is slow as compared: https://users.rust-lang.org/t/why-my-rust-multithreaded-solution-is-slow-as-compared-to-the-same-c-solution/95581
- A performance problem compared with Julia: https://users.rust-lang.org/t/a-performance-problem-compared-with-julia/51871/18
- Help comparing Rust vs Julia speed: https://users.rust-lang.org/t/help-comparing-rust-vs-julia-speed/54514/11
- Optimizing linear algebra code: https://users.rust-lang.org/t/optimizing-linear-algebra-code/39433/14
- Rust program has only 42% the speed of similar c++ program: https://users.rust-lang.org/t/rust-program-has-only-42-the-speed-of-similar-c-program/73738
- Performance issue - High complexity code: https://users.rust-lang.org/t/performance-issue-high-complexity-code/40241/17
- Performance question: https://users.rust-lang.org/t/performance-question/54977/8
- Rust performance help (convolution): https://users.rust-lang.org/t/rust-performance-help-convolution/44075
- Optimization comparison: Vec vs array and for vs while: https://internals.rust-lang.org/t/optimization-comparison-vec-vs-array-and-for-vs-while/16410
- Performance optimization, and how to do it wrong: https://genna.win/blog/convolution-simd/
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
- Unnecessary Optimization in Rust: https://www.reddit.com/r/rust/comments/1hk0bry/unnecessary_optimization_in_rust_hamming/
  * check comments
- From 'Very Fast' to '~Fastest': Helping rust unleash compiler optimizations: https://blog.anubhab.me/tech/optimizing-diff-match-patch/
  * comments in https://www.reddit.com/r/rust/comments/1hsnnat/40_boost_in_text_diff_flow_just_by_facilitating/

# Panics

- Rust panics under the hood: https://fractalfir.github.io/generated_html/rustc_codegen_clr_v0_2_1.html
- Unwind considered harmful? https://smallcultfollowing.com/babysteps/blog/2024/05/02/unwind-considered-harmful/

# Unsafe

- Being Fair about Memory Safety and Performance: https://www.thecodedmessage.com/posts/unsafe/
  * need to be super-attentive to this post, this may be key to how we treat unsafe in our talk
- Implementing a VM: how unsafe should I go? https://www.reddit.com/r/rust/comments/n8yy7z/implementing_a_vm_how_unsafe_should_i_go/
- Good example of high performance Rust project without unsafe code? https://www.reddit.com/r/rust/comments/we91es/good_example_of_high_performance_rust_project/

# Code size

- Minimizing Rust Binary Size: https://github.com/johnthagen/min-sized-rust

# Other

- Leaving Rust gamedev after 3 years: https://loglog.games/blog/leaving-rust-gamedev/ (also comments in https://news.ycombinator.com/item?id=40172033 and https://habr.com/ru/articles/813597/)
- Why I hate Rust programming language? https://www.reddit.com/r/programming/comments/n9l68o/why_i_hate_rust_programming_language/ (comments)
- Rust inadequate for text compression codecs? https://news.ycombinator.com/item?id=43295908
- Rust: Not So Great For Codec Implementing: https://news.ycombinator.com/item?id=14901443

Materials have been collected according to [collection methodology](materials/method.md).

Note that section split below is rather crude and may do more harm than good.
Please refactor mercilessly if you think it makes sense.
On the other hand, once all materials are analyzed we won't care about this file.

- TODO add more interesting materials from
  * MIR opts (gh-16): compiler/rustc_mir_transform/src and https://github.com/rust-lang/rust/issues?q=state%3Aopen%20label%3A%22A-mir-opt%22
  * compiler-team repo (gh-8): https://github.com/rust-lang/compiler-team
- TODO(gh-15) survey project goals for perf-related stuff
  * https://rust-lang.github.io/rust-project-goals

# Coding guidelines

- Rustc development guide: https://rustc-dev-guide.rust-lang.org/
  * Assignee: yugr
  * Status: DONE (5m)
  * Just general overview of compiler internals (infra, type checking, etc.)
  * No info about performance
- Rust design patterns: https://softwarepatternslexicon.com/patterns-rust/
  * Assignee: yugr
  * Status: Wontfix (5m)
  * A set of very high-level advices (ChatGPT ?)
  * Perf-related patterns are [here](https://softwarepatternslexicon.com/patterns-rust/23/)
  * Codegen-related advices:
    + [Match exprs](https://softwarepatternslexicon.com/patterns-rust/23/11/)
  * More materials: no new links
- Rust Performance Book (by Nethercote): https://nnethercote.github.io/perf-book/
  * Assignee: yugr
  * Status: DONE (45m)
  * Very common advices:
    + Iterators instead of indices
    + Slices instead of Vecs
    + Assertions
  * "I'm trying to keep the book practical by focusing on techniques that have been shown to be useful on real code" (as answer to why floating point is not covered)
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/jvmb8u/the_rust_performance_book/)
    + [GH issues](https://github.com/nnethercote/perf-book/issues)
- Some general guidelines from Redox OS: https://doc.redox-os.org/book/rusting-properly.html
  * Assignee: yugr
  * Status: DONE (5m)
  * Both performance and style guidelines w/o much explanation
  * No previously unknown perf hints (e.g. slices vs containers, use `box` to facilitate placement-new, etc.)
  * More materials: no new links
- Found no guidelines in [other projects](real-projects.md) in gh-3

# C/C++ comparison

- C++ faster and safer by Rust: benchmarked by Yandex: https://habr.com/ru/articles/492410/
  * Assignee: yugr
  * Status: DONE (15m)
  * Main idea: response to critique of Rust by Polukhin; they confirm that comparison of asm of microbenchmarks is pointless
  * More materials: no interesting mats in suggestions
- The relative performance of C and Rust: https://bcantrill.dtrace.org/2018/09/28/the-relative-performance-of-c-and-rust/
  * Assignee: yugr
  * Status: DONE (15m)
  * Main idea: studies performance of Rust data structures vs. some custom C equivalents (irrelevant)
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/9jsqyg/the_relative_performance_of_c_and_rust/)
    + no performance-related materials found in blog
- Speed of Rust vs C: https://kornel.ski/rust-c-speed
  * Assignee: yugr
  * Status: DONE (50m)
  * Main idea: basic comparison of Rust/C (not C++!) performance features; in particular
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
- Rust превосходит по производительности C++ согласно результатам Benchmarks Game: https://habr.com/ru/articles/480608/
  * Assignee: yugr
  * Status: DONE (15m)
  * Main idea: article itself just confirms Benchmarks Game results; an interesting discussion in comments about `unique_ptr`
  * More materials: added info about `unique_ptr` vs `Box` to features
- Rust vs. C++ на алгоритмических задачах: https://habr.com/ru/articles/344282/
  * Assignee: yugr
  * Status: DONE (10m)
  * Main idea: article compares C++ vs Rust on simple programs
  * More materials: nothing interesting in comments
- Safety vs Performance. A case study of C, C++ and Rust sort implementations: https://github.com/Voultapher/sort-research-rs/blob/main/writeup/sort_safety/text.md
  * Assignee: yugr
  * Status: DONE (10m)
  * Main idea: article benchmarks various sort implementations in Rust/C++ and their safety guarantees
    + Rust implementations also have to be memory-safe
  * Conclusion: the relevant part is perf comparison (Rust wins by Nx)
  * More materials: NA
- Loop Performance in Rust: https://www.youtube.com/watch?v=E37rSIhWjso
  * Assignee: yugr
  * Status: DONE (50m)
  * Main idea: discusses loop codegen :
    + autovec
    + lack of fast math
    + LLVM misopts
    + explicit SIMD
  * More materials: N/A
- Rust vs C++ Theoretical Performance: https://users.rust-lang.org/t/rust-vs-c-theoretical-performance/4069
  * Assignee: yugr
  * Status: DONE (30m)
  * Main idea: discusses potential Rust improvements over C++:
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
  * Assignee: zakhar
  * Status: DONE (10m)
  * Problem: Rust benchmark 10x slower than C
  * Root cause:
    + Rust code was compiled in debug mode
    + missing `assert`'s to disable bounds checking
    + some benchmark-specific code tweaking to please compiler
  * Solution: Do not use inclusive ranges, use `cmp::min` to allow the compiler to drop bounds-checks (or use unsafe).
    + [Explanation](https://users.rust-lang.org/t/rust-vs-c-vs-go-runtime-speed-comparison/104107/22) of problems with inclusive ranges
- Performance issue with C-array like computation: https://users.rust-lang.org/t/performance-issue-with-c-array-like-computation-2-times-worst-than-naive-java/9807
  * Assignee: zakhar
  * Status: DONE (15m)
  * Problem: Rust code slower than Java JIT equivalent
  * Root cause:
    + Use `-mcpu=native`
    + Low-level CPU architecture effects from different ways to find 3-element min (https://matklad.github.io/2017/03/12/min-of-three.html)
    + Also, JIT has access to runtime statistics (e.g. which allows better vectorization)
  * Solution: Maybe LLVM already generates better assembly
- Simple Rust and C# performance comparison: https://users.rust-lang.org/t/simple-rust-and-c-performance-comparison/42970
 * Assignee: zakhar
 * Status: DONE (10m)
 * Problem: Rust code slower than C# equivalent
 * Root cause: Benchmark to small to reliably measure it and errors in using the benchmarking framework
 * Solution: As author states, "building these into somewhat larger programs and the Rust code was about twice as fast in the final result".
- Why is C++ still beating Rust at performance in some places? https://users.rust-lang.org/t/why-is-c-still-beating-rust-at-performance-in-some-places/95877
  * Assignee: yugr
  * Status: DONE (2m)
  * OP asks why Rust is slower in general but gets no concrete answers
  * More materials: no new links
- Rust vs. C++: Fine-grained Performance: https://users.rust-lang.org/t/rust-vs-c-fine-grained-performance/4407
  * Assignee: yugr
  * Status: DONE (10m)
  * The article is more about Rust as a language, optimizations are not discussed
  * More materials:
    + [Original post](https://cantrip.org/rust-vs-c++.html)
    + no new links
- A good performance comparision C and Rust: https://users.rust-lang.org/t/a-good-performance-comparision-c-and-rust/5901/7
  * Assignee: yugr
  * Status: DONE (5m)
  * A superficial discussion of Rust vs C++ and benchmarks game
  * Nothing concrete mentioned except jemalloc and noalias
  * More materials: no new links
- Rust-specific code optimisations vs other languages: https://users.rust-lang.org/t/rust-specific-code-optimisations-vs-other-languages/49663
  * Assignee: yugr
  * Status: DONE (5m)
  * OP asks of Rust-specific perf optimizations
  * Comments include
    + noalias
    + C++ problem with `unique_ptr` parameter passing
    + niche opts
    + ZSTs
  * More materials: now new links
- How to speed up this rust code? I’m measuring a 30% slowdown versus the C++ version: https://users.rust-lang.org/t/how-to-speed-up-this-rust-code-im-measuring-a-30-slowdown-versus-the-c-version/1488
  * Assignee: yugr
  * Status: DONE (20m)
  * Problem: Rust code is slower than C++
  * Root cause: stack protection, bounds checking
  * More materials: no new links
- Goals and priorities for C++: https://internals.rust-lang.org/t/goals-and-priorities-for-c/12031/32
  * Assignee: yugr
  * Status: DONE (25m)
  * Discusses language goals but also some points on Rust perf features:
    + lack of fast-math
    + move semantics
    + noalias
  * Overall conclusion is that safety is most important and perf follows (one example is lack of fast math)
  * More materials: no new links
- Zero cost abstractions: Rust vs C++: https://www.rottedfrog.co.uk/?p=24
  * Assignee: yugr
  * Status: DONE (20m)
  * Main idea: compares performance of `unique_ptr` vs `Box`
    + code is larger to support panic unwinding
    + LLVM does not optimize dead code after tail call
    + significantly more code to support panicking (but it can be removed with `-C panic=abort`)
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/gqw2gj/zero_cost_abstractions_rust_vs_c/)
    + no more interesting posts in "performance site:https://www.rottedfrog.co.uk"
- Evaluating Languages for Bioinformatics: https://github.com/rjray/mscs-thesis-project
  * Assignee: yugr
  * Status: DONE (5m)
  * Main idea: thesis investigates applicability of diff. languages to bioinformatics
    + Author runs several domain-relevant benchmarks and compares results, without low-level analysis
  * Conclusion: not relevant
  * More materials: none
- Rust is now overall faster than C in benchmarks: https://www.reddit.com/r/rust/comments/kpqmrh/rust_is_now_overall_faster_than_c_in_benchmarks/
  * Assignee: yugr
  * Status: DONE (5m)
  * Main idea: just general rant about Benchmarks Game irrelevance
  * More materials: none
- Rust Optimizations That C++ Can't Do: https://robert.ocallahan.org/2017/04/rust-optimizations-that-c-cant-do_5.html
  * Assignee: yugr
  * Status: DONE (20m)
  * Main idea: just an example of aliasing optimization
  * More materials: scanned mats in
    + "rust performance site:https://robert.ocallahan.org"
    + [Reddit](https://www.reddit.com/r/rust/comments/63ijkw/rust_optimizations_that_c_cant_do/)
    + [HN](https://news.ycombinator.com/item?id=14040021)
- What makes Rust faster than C/C++? https://www.reddit.com/r/rust/comments/px72r1/what_makes_rust_faster_than_cc/
  * Assignee: yugr
  * Status: DONE (50m)
  * Main idea: a lot of high quality comments (a must-read for us):
    + [this](https://www.reddit.com/r/rust/comments/px72r1/comment/hem26o0/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
    + other comments mention known issues: stdlib data structures, aliasing, moves, etc.
    + a [linked article](https://matklad.github.io/2020/09/20/why-not-rust.html) mentions [expression templates](https://en.wikipedia.org/wiki/Expression_templates) which are very important to linear algebra code but impossible in Rust
  * More materials: added relevant links
- Why ISN'T Rust faster than C? https://www.reddit.com/r/rust/comments/1at3r6d/why_isnt_rust_faster_than_c_given_it_can_leverage/
  * Assignee: yugr
  * Status: DONE (30m)
  * Main idea: general discussion; mentioned topics :
    + aliasing
    + niche opts
    + high-level data structures
    + Pascal strings
    + bounds checks hurting autovec
  * Commenters conclude that it's not valid to compare Rust to pure C (C++ should be used)
  * More materials: nothing unseen before in links
- Is bound checking the only runtime cost of Rust? https://users.rust-lang.org/t/is-bound-checking-the-only-runtime-cost-of-rust/66661
  * Assignee: zakhar
  * Status: DONE (10m)
  * Problems:
    + Method calls on `dyn Trait` objects are always indirect ("virtual")
    + Function pointer calls are indirect
    + Checked arithmetic
    + RefCel, Rc, Arc checks
 * Solution: For less bounds checking use iterators or provide compiler with more info (e.g. using asserts)
- Why is Rust slightly slower than C? https://news.ycombinator.com/item?id=20944403
  * Assignee: yugr
  * Status: DONE (50m)
  * Problem: userspace network driver was up to 10% slower compared to C (although much faster than other langs)
  * Root cause:
    + authors claim that main slowdown is due to bounds checking
    + enabling integer overflows did not change performance
  * Solution:
    + using unsafe Rust code (obtained via `c2rust` tool) fixed performance
  * More materials:
    + original post: https://github.com/ixy-languages/ixy-languages/blob/master/Rust-vs-C-performance.md
    + paper: https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/the-case-for-writing-network-drivers-in-high-level-languages.pdf
    + video: https://media.ccc.de/v/35c3-9670-safe_and_secure_drivers_in_high-level_languages (Rust performance discussed at 53:00)
    + Reddit: https://www.reddit.com/r/rust/comments/d2rpsa/a_highspeed_network_driver_written_in_c_rust_go_c/
- Rewrite the VP9 codec library in Rust: https://news.ycombinator.com/item?id=39537735
  * Assignee: yugr
  * Status: DONE (10m)
  * Main idea: post is just about example kernel driver written in Rust; commenters discuss cost of bounds checks at some length but nothing new
  * More materials: none
- Is C++ more performant than Rust? https://www.reddit.com/r/cpp/comments/17zaiu6/is_c_more_performant_than_rust/
  * Assignee: yugr
  * Status: DONE (20m)
  * Comments:
    + known stuff: aliasing, bounds checks
    + interesting discussion here: https://www.reddit.com/r/cpp/comments/17zaiu6/comment/k9zhm09/
      - in particular they mention lack of placement new as performance problem (created gh-7 to add materials on this)
  * More materials: no new links
- Why Not Rust ? https://github.com/guevara/read-it-later/issues/8279
  * Assignee: yugr
  * Status: DONE (10m)
  * Main idea: post lists several Rust perf problems:
    + `memcpy`'s and placement new
    + LLVM `noalias` problems
    + no expression templates
    + all mentioned issues are fixed by now
  * More materials: added links
- What kind of performance rust is trying to achieve? https://users.rust-lang.org/t/what-kind-of-performance-rust-is-trying-to-achieve/1674
  * Assignee: yugr
  * Status: DONE (20m)
  * Main idea: user asked whether Rust tries to be as fast as C and why; answers:
    + Steven Klabnik: yes, C is reference
    + opts: noalias, codegen via macro (e.g. in Servo), fearless concurrency
  * More materials: couldn't find any relevant links for improving performance by codegen via macro
- Battle Of The Backends: Rust vs. Go vs. C# vs. Kotlin - inovex GmbH: https://www.inovex.de/de/blog/rust-vs-go-vs-c-vs-kotlin
  * Assignee: yugr
  * Status: DONE (0m)
  * Main idea: just comparing performance of some network app (no analysis)
- Comparing Pythagorean triples in C++, D, and Rust: https://atilaoncode.blog/2018/12/31/comparing-pythagorean-triples-in-c-d-and-rust/
  * Assignee: yugr
  * Status: DONE (40m)
  * Problem: Rust program runs 2x slower than C++/D
  * Root cause: inclusive ranges `..=`
  * Solution: replace `a..=b` with `a..(b + 1)`
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/ab7hsi/comparing_pythagorean_triples_in_c_d_and_rust/)
      - [interesting discussion](https://www.reddit.com/r/rust/comments/ab7hsi/comment/ed0u11h/) of how integer checks were optimized in different toolchain
      - (single instruction for overflow arithmetic, expanded late in pipeline)
    + [HN](https://news.ycombinator.com/item?id=18794363)
- Possible Rust-specific optimizations: https://users.rust-lang.org/t/possible-rust-specific-optimizations/79895
  * Assignee: yugr
  * Status: DONE (5m)
  * Main idea: user wonders what are potential, NYI optimizations; the only answer is `noalias`
  * More materials: added links
- What languages (other than Rust) have "zero cost abstraction"? https://www.reddit.com/r/rust/comments/zkr3xm/what_languages_other_than_rust_have_zero_cost/
  * Assignee: yugr
  * Status: DONE (50m)
  * General discussion of various perf. features which are not 0-cost:
    + bounds checks
    + panics can't be coalesced (but what about delayed panics ?)
  * What allows Rust to be 0-cost (e.g. iterators):
    + monomorphization
    + inlining
  * More materials: no new links
- NPB-Rust: NAS Parallel Benchmarks in Rust: https://arxiv.org/abs/2502.15536
  * Assignee: yugr
  * Status: DONE (15m)
  * Article discusses porting of NASA benchmarks to Rust
  * Opts are mainly unsafe code and parallel iterators
  * Does not discuss low-level performance issues like bounds checks or autovec so not relevant for us
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/1jz504y/is_rust_faster_than_fortran_and_c_a_case_study/)
    + no new links
- Rust now, on average, outperforms C++ in The Benchmarks Game: https://www.reddit.com/r/rust/comments/akluxx/rust_now_on_average_outperforms_c_in_the/
  * Assignee: yugr
  * Status: DONE (10m)
  * A general discussions of benchmarks game, no relevant info
  * More materials: none
- Rust 2019: Beat C++: https://www.reddit.com/r/rust/comments/acjcbp/rust_2019_beat_c/
  * Assignee: yugr
  * Status: DONE (20m)
  * Problem: OP wonders how to write equally performant code in Rust
  * Root cause: need to enable autovec
  * Solution: `exact_chunks`, unchecked ops, use `&[T]` instead of `&Vec<T>`
  * More materials: no new links
- zlib-rs is faster than C: https://trifectatech.org/blog/zlib-rs-is-faster-than-c/
  * Assignee: yugr
  * Status: DONE (50m)
  * Optimizations:
    + multiversioning is important feature for autovec but has to be done manually now
    + manually rearrange fields according to frequency of access (for better cache locality)
    + perf issue in Rust: slow switch-cases
  * Extensive iscussion of unsafe on HN:
    + even though zlib-rs uses unsafe, it's very localized
    + general critics of Rust being unable to implement basic data structs w/o unsafe (double linked list)
    + unsafe still has many checks one e.g. borrow checker
    + correctness of unsafe block can't be verified in isolation, via local reasoning (so unsafe behavior is not localized in unsafe blocks)
  * More materials:
    + [Tweedegolf](https://tweedegolf.nl/en/blog/149/zlib-rs-is-faster-than-c) - dup of Trifecta blogpost
    + [Reddit](https://www.reddit.com/r/rust/comments/1ixt1ei/zlibrs_is_faster_than_c_trifecta_tech_foundation/?rdt=48389)
    + [HN](https://news.ycombinator.com/item?id=43381512)
    + added some links
- Making Rust faster than C: https://trifectatech.org/initiatives/codegen/
  * Assignee: yugr
  * Status: DONE (10m)
  * Mentioned [here](https://trifectatech.org/blog/zlib-rs-is-faster-than-c/) that C switch-cases are much faster
  * Describes work on state machine codegen improvements:
    + idea [taken](https://github.com/ziglang/zig/pull/21257) from Zig language
  * Plans to make more perf improvements (w/o details)
  * More materials: added links
- Improve state machine codegen: https://rust-lang.github.io/rust-project-goals/2025h1/improve-rustc-codegen.html
  * Assignee: yugr
  * Status: DONE (50m)
  * Crux of the problem:
    + Current state machines are `loop` + `match`
    + They suffer from mispredicted branch (at start of `match`)
  * New language construct `loop match` with `continue` to arms of match to implement state machines
    + Basically a "controlled" goto
    + "irreducible control flow primitive"
    + improves readability and allows better codegen (up to 10-20% improvement)
  * Pushback from maintainers against initial version due to alternative proposals (TCO) and ability to implement this as MIR optimization or macro
    + Fixed by author
  * Computed goto can be added in future
  * There seems to be duplication with existing LLVM optimization `-C llvm-args=-enable-dfa-jump-thread`
  * More materials:
    + [RFC](https://github.com/rust-lang/rfcs/pull/3720)
    + [Draft impl](https://github.com/trifectatechfoundation/rust/tree/labeled-match)
    + [Work plan](https://trifectatech.org/initiatives/workplans/codegen/)
    + [Pre-RFC Zulip discussion](https://rust-lang.zulipchat.com/#narrow/channel/213817-t-lang/topic/Fallthrough.20in.20Match.20Statements/near/474669655)
- Better rust codegen @ unconf 2024: https://hackmd.io/@Q66MPiW4T7yNTKOCaEb-Lw/gosim-unconf-rust-codegen
  * Assignee: yugr
  * Status: DONE (30m)
  * Several perf-related proposals:
    + `loop match`
    + multiversioning for SIMD
    + MIR opts (disabled for large funs, no funding atm)
    + inefficient default symbol visibility (no details)
    + inefficient TLS model
  * More materials:
    + added links
    + failed to locate info on symbol visibility issue...
- RFC 1909: Unsized locals: https://github.com/rust-lang/rfcs/blob/master/text/1909-unsized-rvalues.md
  * Assignee: yugr
  * Status: DONE (90m)
  * Proposes to add dynamic arrays to Rust (to avoid using `Box`'es)
  * Not fully equivalent to C's VLAs: values allocated inside block are destroyed at `}`:
    + this is necessary for constructing [complex data structures](https://github.com/rust-lang/rfcs/pull/1808#issuecomment-266225999)
      (e.g. ASTs, arrays of arrays, etc.)
    + [citation](https://github.com/rust-lang/rfcs/pull/1808#issuecomment-266200526):
> ... this is less powerful than a proper alloca;
> the lifetimes are restricted to just the closure body
> whereas in reality they are the same as the entire calling function's frame.
  * Pros: locality, no alloc overhead
  * Alternatives: `SmallVec`
  * Other materials:
    + Continuation of [RFC 1808](https://github.com/rust-lang/rfcs/pull/1808)
    + [Tracking issue](https://github.com/rust-lang/rust/issues/48055)
    + [Pull request](https://github.com/rust-lang/rfcs/pull/1909)
- Impact of Undefined Behavior on Performance: https://news.ycombinator.com/item?id=27745755
  * Status: DONE (3h)
  * Makes a classical example of loop where undefinedness of signed overflow allows better codegen in C
  * Compares with Rust which is much worse
    + unfortunately no investigation why Rust is so bad
    + (most likely because equivalent C code may loop forever)
  * More materials: added to respective feature
- Why my Rust multithreaded solution is slow as compared: https://users.rust-lang.org/t/why-my-rust-multithreaded-solution-is-slow-as-compared-to-the-same-c-solution/95581
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: multithreaded Rust program is much slower than equivalent C
  * Root cause: `--release` and `f64::to_int_unchecked`
  * More materials: no new links
- Rust program has only 42% the speed of similar c++ program: https://users.rust-lang.org/t/rust-program-has-only-42-the-speed-of-similar-c-program/73738
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: Rust code slower than C++
  * Root cause: different PRNG, bounds checks
  * Solution: iterators, `SmallRng`, replace `&Vec<T>` with `&[T]` (that actually gave perf in 2022!), make some params `const`
  * More materials: no new links
- Performance question: https://users.rust-lang.org/t/performance-question/54977
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: Rust code is much slower than C
  * Root cause: lack of autovec
  * Solution: iterators, `assert!`
  * More materials: no new links
- Rust performance help (convolution): https://users.rust-lang.org/t/rust-performance-help-convolution/44075
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: Rust code much slower than C `-Ofast`
  * Root cause: lack of autovec
  * Solutions: iterators (`windows` instead of `exact_chunks`), `target-cpu=native`, fast FP operations
  * More materials: no new links
- n times faster than C: https://ipthomas.com/blog/n-times-faster-than-c/
  * Assignee: yugr
  * Status: DONE (10m)
  * Rewriting the code in several steps: use iterators (14x improvement for unclear reasons), remove branches, manual SIMD
  * No asm analysis and no general recommendations
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/14yvlc9/n_times_faster_than_c_where_n_128/)
    + no more relevant posts in blog
- Rust loop speed: https://www.reddit.com/r/rust/comments/1aumq2h/rust_loop_speed/
  * Status: DONE (5m)
  * Problem: loop much slower in Rust
  * Root cause: no `--release` and inclusive range
  * Solution: use `--release` and `..`
  * More materials: no new links

# UB in C++

- Updated Field Experience With Annex K — Bounds Checking Interfaces: https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1969.htm (2015)
  * Assignee: yugr
  * Status: DONE (20m)
  * Field report on integration of `XXX_s` APIs from Annex K of C standard
  * Not very portable (MSVC has slightly different APIs)
  * Adopting is non-trivial:
    + need to get buffer size somewhere, somehow
    + need to check return codes
  * Common mistakes:
    + passing size of wrong buffers (e.g. source instead of dst)
    + just use `strlen` to compute buffer size in `strcpy_s` (this is useless)
    + duplicated `strlen` calls
    + return values are hard to check (need new error handling strategy across app) and are poorly tested
  * Design problems:
    + allow custom design handlers (instead of pure trap)
  * Conclusions:
> The design of the Bounds checking interfaces, though well-intentioned, suffers from far too many problems to correct.
> Using the APIs has been seen to lead to worse quality, less secure software than relying on established approaches or modern technologies.
> More effective and less intrusive approaches have become commonplace and are often preferred by users and security experts alike.
- Visual C++: Iterator Checks and Slow STL Code: https://codeyarns.com/tech/2010-09-10-visual-c-iterator-checks-and-slow-stl-code.html#gsc.tab=0 (pre-2010)
  * Assignee: yugr
  * Status: DONE (15m)
  * Debug (not hardening) feature
  * One of the first debug STLs
  * Performs some iterator checks but interestingly does not check `operator[]`
  * Controlled via
    + high-level flags (`_SECURE_SCL`, `_HAS_ITERATOR_DEBUGGING`)
    + low-level flag (`_ITERATOR_DEBUG_LEVEL`)
  * `_ITERATOR_DEBUG_LEVEL=1` is for hardening and `2` is for debug (`2` is 100x slower)
- RFC: C++ Buffer Hardening: https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734 (2022)
  * Assignee: yugr
  * Status: DONE (2h)
  * Proposal by Apple
  * Replacement for pre-existing libc++ debug mode (`_LIBCPP_ENABLE_DEBUG_MODE` ?)
    + ABI changing
    + too slow
  * Two proposals:
    + hardened C++ dialect to avoid potentially unsafe pointer arithmetic (warnings, fixits)
      - later became [Safe Buffers](https://clang.llvm.org/docs/SafeBuffers.html)
      - Dergachev [argues](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734/8) that (massive) fixits is a distinguishing feature of this proposal
    + debug checks in STL containers
      - Very similar to `_GLIBCXX_ASSERTIONS`
  * Explicitly allow ABI changes in containers but make them controllable via macro
  * Perf difference between `std::vector::operator[]` and `std::vector::at` is non-trivial:
    + [20%](https://quick-bench.com/q/o9du22dYmO0BCs5YqJ9gEKPyQ10) on simple benchmark (but this may be due to exception overhead)
    + loops no longer vectorized (hello Rust!)
    + finally no real consensus on perf implications (whether compiler with "catch up")
  + Strong support from kcc and many others
  + Positive comments on similar feature in MSVC
  + Bounds checks are similar to common C++ opt: replace `reserve` + `push_back` with `resize`
  + `__builtin_assume` are [not always beneficial](https://discourse.llvm.org/t/llvm-assume-blocks-optimization/71609)
  * Conclusion: general push back from AaronBallman in fear of experimental language dialect which will not be broadly used
  * More materials:
    + [Video](https://www.youtube.com/watch?v=nPRY8-FtzZg)
    + [Reddit](https://www.reddit.com/r/cpp/comments/xwtzro/rfc_c_buffer_hardening_clang_frontend/)
    + [HN](https://news.ycombinator.com/item?id=33103464)
    + Added tons of links
- [-Wunsafe-buffer-usage] WIP: RFC: NFC: User documentation: https://reviews.llvm.org/D136811 (2022)
  * Assignee: yugr
  * Status: DONE (20m)
  * Formal RFC for previous discussion
  * RFC does not touch the actual libc++ hardening part, only warnings and fixits
  * This is specifically a buffer overflow solution (not UAF, UAR, etc.)
  * Other materials: no links
- RFC: Hardening in libc++: https://discourse.llvm.org/t/rfc-hardening-in-libc/73925 (2023)
  * Assignee: yugr
  * Status: DONE (15m)
  * Update on previous RFC, concentrates specifically at libc++ isntrumentation
  * By default ABI is not changed (unless `_LIBCPP_ABI_BOUNDED_ITERATORS_...` is defined)
  * Many operations are not hardened and it's unclear whether it's possible in future
  * Plan for compatibility with GCC's `-fhardened`
  * Already used by [Chrome](https://issues.chromium.org/issues/40228527) and Gentoo Hardened
  * Discusses minor questions e.g. naming, how to override handlers
- libc++ documentation: Hardening Modes: https://libcxx.llvm.org/Hardening.html
  * Assignee: yugr
  * Status: DONE (30m)
  * A bunch of hardening (not debug) checks in libc++:
    - `operator[]`, strict weak order, etc.
    - full list [here](https://libcxx.llvm.org/Hardening.html#id12)
  * Controlled via macro `_LIBCPP_HARDENING_MODE` (or `-flibc++-hardening` flag)
  * Similar checks available in GCC's libstdc++ (under `_GLIBCXX_ASSERTIONS` i.e. `-fhardened`)
  * Most likely misses many types of bugs
- Retrofitting spatial safety to hundreds of millions of lines of C++: https://security.googleblog.com/2024/11/retrofitting-spatial-safety-to-hundreds.html (2024)
  * Assignee: yugr
  * Status: DONE (1h)
  * Post about hardened Libc++ integration to Google codebase
  * Report just 0.3% performance overhead and 0.5% size increase in Chrome binary !
  * Plan to use [Safe Buffers](https://clang.llvm.org/docs/SafeBuffers.html) in future
  * More materials:
    + [Reddit](https://www.reddit.com/r/cpp/comments/1gs5bvr/retrofitting_spatial_safety_to_hundreds_of/)
    + [Reddit 2](https://www.reddit.com/r/cpp/comments/1h9hsax/google_retrofits_spatial_memory_safety_onto_c/)
    + [HN](https://news.ycombinator.com/item?id=42150550)
- Security in C++ - Hardening Techniques From the Trenches - Louis Dionne - C++Now 2024: https://www.youtube.com/watch?v=t7EJTO0-reg
  * Assignee: yugr
  * Status: DONE (45m)
  * Overview of libc++ hardening, generall follows the docs
  * WebKit also uses hardened libc++
  * More materials:
    + [Reddit](https://www.reddit.com/r/cpp/comments/1g8pgzu/security_in_c_hardening_techniques_from_the/)
    + no new links
- LLVM's 'RFC: C++ Buffer Hardening' at Google: https://bughunters.google.com/blog/6368559657254912/llvm-s-rfc-c-buffer-hardening-at-google
  * Assignee: yugr
  * Status: DONE (15m)
  * Hardening integration report for Google Cloud Platform
  * Report 1-2.5% perf degradation (bandwidth, latency) but 4x improved with FDO
  * Can work around hardening overhead via `std::vector::data` or iterators (instead of indices)
  * More materials:
    + [Reddit](https://www.reddit.com/r/cpp/comments/1b6zxee/llvms_rfc_c_buffer_hardening_at_google/)
- Story-time: C++, bounds checking, performance, and compilers: https://chandlerc.blog/posts/2024/11/story-time-bounds-checking/
  * Assignee: yugr
  * Status: DONE (40m)
  * Driving factors for spatial safety checks:
    + improvements in LLVM due to support for safe languages (Azul, Rust, Swift, etc.), UBsan adoption
    + PGO infra and improvements
> Without PGO infrastructure, I do not think the overhead of these checks would be tolerable for most performance sensitive workloads
    + eventually
> radically reduce the practical costs of these kinds of checks and make them affordable by default and pervasively
  * Temporal safety can be enabled by refcounting but overheads need to be checked
  * Unfortunately not too many tech. details
  * More materials:
    + [Reddit](https://www.reddit.com/r/cpp/comments/1gtos7w/storytime_c_bounds_checking_performance_and/)
      - Huge discussion of Rust `unsafe`
    + No more links
- Exploiting Undefined Behavior in C/C++ Programs for Optimization: A Study on the Performance Impact: https://web.ist.utl.pt/nuno.lopes/pubs/ub-pldi25.pdf
  * Assignee: yugr
  * Status: DONE (70m)
  * This is very similar to our goal but for C++
  * Investigates perf effects when disabling different types of UB in C++:
    + integer/shift overflows (masking + remove `nsw`)
    + strict aliasing
    + `__builtin_assume`/`__builtin_unreachable`
    + const/pure annotations
    + `restrict` annotations
    + etc.
  * Somehow used Alive2 to detect missing disabled UBs
  * Benchmarks based on Phoronix testsuite
  * Results are weird:
    + UB is much more critical for AArch64 than for X86 (most likely X86 machines are more powerful and can compensate for perf loss)
    + non-LTO AArch64:
      - average: 3% loss for each UB type, 5% net
      - worst: up to 10% for each UB type, up to 13% net
    + LTO AArch64:
      - average: 3% gain (!) for each UB type, 0% net
      - worst: up to 5% for each type, up to 5% net
  * Also contains analysis of some regressions:
    + some can be fixed by more clever LLVM opts (e.g. more aggressive CSE caused more spills)
    + some are totally random (e.g. loop align)
  * More materials:
    + [Reddit](https://www.reddit.com/r/Compilers/comments/1k658fw/exploiting_undefined_behavior_in_cc_programs_for/)
    + [HN](https://news.ycombinator.com/item?id=43766263)
    + Also cites some relevant papers (in "Related work: Performance studies" section):
      - (Secure compiler) Prevention of vulnerabilities arising from optimization of code with Undefined Behavior
        * has too few perf measurements
      - (Secure compiler) Developing a clang-based safe compiler
        * has too few perf measurements
      - Doerfert's papers on optimistic annotations and ORAQL
        * rely on unsafe optimizations so are not relevant
      - (Autovec) Performance Left on the Table: An Evaluation of Compiler Autovectorization for RISC-V
      - (Autovec) Evaluating Auto-Vectorizing Compilers through Objective Withdrawal of Useful Information
- Performance Left on the Table: An Evaluation of Compiler Autovectorization for RISC-V: https://par.nsf.gov/servlets/purl/10426592
  * Status: DONE (5m)
  * Investigates RISCV-specific autovec issues
  * Not relevant
- Evaluating Auto-Vectorizing Compilers through Objective Withdrawal of Useful Information: https://ora.ox.ac.uk/objects/uuid:eac7b135-e92b-48dc-a1f7-4de66a441390/files/szg64tk95s
  * Status: DONE (5m)
  * Investigates how various additional info influences efficacy of vectorization in TSVC:
    + conditions, potential aliasing, non-trivial indexing
  * Not very useful for us
- C++ Safe Buffers: https://clang.llvm.org/docs/SafeBuffers.html
  * Assignee: yugr
  * Status: DONE (5m)
  * Docs for `-Wunsafe-buffer-usage`
  * Basically just warns on any unsafe pointer arithmetic
  * Experimental `-fsafe-buffer-usage-suggestions` to generate fixits
  * Bunch of pragmas to turn off
  * More materials: no new links
- Historical Clang Language WG Meeting Minutes (Apr 2024 - Mar 2025): https://discourse.llvm.org/t/historical-clang-language-wg-meeting-minutes-apr-2024-mar-2025/85638
  * Status: DONE (15m)
  * Discussed various topics: profiles, state of the language, etc.
  * No discussion of performance
  * More materials: added one more post by Herb
- P3471: Standard library hardening: https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2025/p3471r4.html
  * Status: DONE (20m)
  * Based on C++ hardening work
  * In general repeats LLVM RFCs
  * Proposes to add special Hardened Preconditions to Standard (accepted for C++26)
  * Some useful discussions in FAQ:
    + Admits that checks are not exhaustive:
> [some] precondition[s] can only be checked for some containers and not others
    + Omitted checks: `erase` methods, associative containers, limited checking of algorithms, `valarray` (planned to cover in dedicated papers...)
  * More materials: no new links
- Legacy Safety: The Wrocław C++ Meeting: https://cor3ntin.github.io/posts/profiles/
  * Status: DONE (20m)
  * Confirms that effort is due to US government's recommendations
  * Making sets of small changes [works](https://security.googleblog.com/2024/09/eliminating-memory-safety-vulnerabilities-Android.html)
  * Large companies are (rapidly?) [moving from C++](https://security.googleblog.com/2022/12/memory-safe-languages-in-android-13.html)
  * Commitee is clear that moving to borrow checker is not possible (e.g. [Safe C++](https://safecpp.org/draft.html))
  * Profiles generally accepted as solution to safety problem
    + aimed at C++26
    + mix of static analysis and runtime checks
- Sutter's Mill: Trip report: November 2024 ISO C++ standards meeting: https://herbsutter.com/2024/11/24/wg21-2024-11/
  * Status: DONE (10m)
  * Just briefly mentions P3471 and [basic safety profiles proposal](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2025/p3081r2.pdf)
  * Confirms that Safe C++ will not be part of Standard in foreseeable future
  * More materials: no more new/relevant links
- Sutter's Mill: Trip report: February 2025 ISO C++ standards meeting: https://herbsutter.com/2025/02/17/trip-report-february-2025-iso-c-standards-meeting-hagenberg-austria/
  * Status: DONE (5m)
  * Cites parts of P3471 but does not add any new info
  * More materials: no more new/relevant links
- ThinkCell: Trip Report: Fall ISO C++ Meeting in Wrocław, Poland: https://www.think-cell.com/en/career/devblog/trip-report-fall-iso-cpp-meeting-in-wroclaw-poland
  * Status: DONE (0m)
  * Irrelevant - does not mention P3471 at all
  * Other materials:
    + [Reddit](https://www.reddit.com/r/cpp/comments/1h33srd/trip_report_fall_iso_c_meeting_in_wroc%C5%82aw_poland/)
- ThinkCell: Trip Report: Winter ISO C++ Meeting in Hagenberg, Austria: https://www.think-cell.com/en/career/devblog/trip-report-winter-iso-cpp-meeting-in-hagenberg-austria
  * Status: DONE (5m)
  * A brief discussion of profiles and P3471, nothing new
  * More materials: none
- Meaning of Undefined and Justification for UB: https://github.com/rust-lang/unsafe-code-guidelines/issues/253
  * Status: DONE (10m)
  * Just general discussion of UB concept in Rust and C++
  * Mentions some optimizations but overall nothing new
  * More materials: no new links

# Expression templates

ET's is an important patern for writing linear algebra code in C++. Can it be used in Rust ?
  - Yes !

- Expression templates: https://en.wikipedia.org/wiki/Expression_templates
  * Status: DONE (15m)
  * Expression templates are a foundation block of C++ linear algebra packages (like Eigen)
  * Allow to avoid generating intermediate results and codegen loop only at end of expression
  * More materials:
    + Seems to be [entirely possible](https://www.reddit.com/r/rust/comments/xidgcq/a_rust_linear_algebra_library_based_on_expression/)
      to implement in Rust
- Expression Templates in Rust? https://www.reddit.com/r/rust/comments/1f0hi5k/expression_templates_in_rust
  * Status: DONE (10m)
  * Nothing prevents usage of Expression Template pattern in Rust
  * Rust iterator combinators are implemented using similar pattern
  * More materials: no new links

# Overflow checks

- Why is Rust not able to optimize this? https://www.reddit.com/r/rust/comments/181tp1a/why_is_rust_not_able_to_optimize_this/ (signed overflow)
  * Assignee: yugr
  * Status: DONE (20m)
  * Problem: `(num * 2) / 2` not optimized in Rust
  * Root cause: overflow is defined in Rust
  * Solutions: `unchecked` methods, `unchecked_math` pragma, compiler hints
  * More materials: nothing in links
- Thought: switch the default on overflow checking: https://internals.rust-lang.org/t/thought-switch-the-default-on-overflow-checking-and-provide-rfc-560s-scoped-attribute-for-checked-arithmetic/15118
  * Assignee: yugr
  * Status: DONE (10m)
  * Discussion of RFC 560 and changing integer overflow checks to be enabled in release by default
  * More materials: added link to great article by John Regher about overflow overheads
- Check for Integer Overflow by Default: https://github.com/rust-lang/rust/issues/47739
  * Status: DONE (50m)
  * Assignee: yugr
  * OP suggests to enable overflow checking in release by default
  * Other people also complain how `as` is unchecked
  * More materials: added more links
- Myths and Legends about Integer Overflow in Rust: https://huonw.github.io/blog/2016/04/myths-and-legends-about-integer-overflow-in-rust/
  * Status: DONE (40m)
  * Assignee: yugr
  * Author surveys RFC 560; discusses semantics of integer overflows and reasoning behind it
    + In particular he mentions that main source of overhead is inhibiting vectorization (not the checks themselves)
  * More materials:
    + [User forum](https://users.rust-lang.org/t/myths-and-legends-about-integer-overflow-in-rust/5612)
    + [Reddit](https://www.reddit.com/r/rust/comments/4gz93u/myths_and_legends_about_integer_overflow_in_rust/)
    + [HN](https://news.ycombinator.com/item?id=11595398)
- [RFC 560](https://github.com/rust-lang/rfcs/blob/master/text/0560-integer-overflow.md)
  * Status: DONE (1.5h)
  * Assignee: yugr
  * RFC talks about background and compromises of decision to diff debug and release behavior
    + I tried to merge all relevant info to section about overflow checks
  * More materials:
    + [GH discussion](https://github.com/rust-lang/rfcs/pull/560)
      - added all relevant links/citations
      - many good objections which mainly revolve around performance hit for debug builds and integer overflows being too rare (e.g. not found in Rustc codebase at that time)
      - on rareness of overflows in real-world [this](https://github.com/rust-lang/rfcs/pull/560#issuecomment-72352420) comment states that such bugs can only be triggered in extreme cases (via fuzzing), not in "normal" tests
- Square powers not being fully optimized? https://www.reddit.com/r/rust/comments/exojhk/square_powers_not_being_fully_optimized/
  * Assignee: yugr
  * Status: postponed (awaiting response, 20m)
  * Problem: `2.pow(n)` not optimized to `1 << n`
  * Root cause: missing optimization in LLVM
  * Solution: was fixed in LLVM in [upstream #47234](https://github.com/rust-lang/rust/issues/47234) but the reverted due to [upstream #120537](https://github.com/rust-lang/rust/issues/120537); current status unclear so I asked in first issue
  * More materials: no interesting mats in suggestions
- Integer overflow checking cost: http://danluu.com/integer-overflow/
  * Status: DONE (70m)
  * Assignee: yugr
  * Author gives some insights on performance of checks in modern X86
  * He also gives some ballpark estimates of checking overhead which do not match the benchmarks
  * Overall the post looks quite superficial
  * More materials:
    + [HN](https://news.ycombinator.com/item?id=8765714)
      - [Extensive critique](https://news.ycombinator.com/item?id=8766264) of hardware overflow checking by thesz and others (5% clock cycle increase due to serialization and flags)
      - nkurz [measured](https://news.ycombinator.com/item?id=8766009) UBsan to have 7% overhead (which confirms danluu's estimates)
    + [Reddit](https://www.reddit.com/r/programming/comments/2po703/the_performance_cost_of_integer_overflow_checking/)
      - `panic`'s make leaf functions non-leaf which may hurt optimizations, introduce reg spills, etc.
    + [Reddit](https://www.reddit.com/r/rust/comments/2pp9lh/the_performance_cost_of_integer_overflow_checking/)
      - just reiterates on previous post

# Bounds checks

- How much does Rust's bounds checking actually cost? https://blog.readyset.io/bounds-checks/
  * Assignee: yugr
  * Status: DONE (75m)
  * Problem: investigates overhead of bounds checking operations
  * Solution:
    + experiments with replacing accesses with `get_unchecked` and modifying compiler (!)
    + does not provide any analysis of results, asm, etc.
    + no noticeable changes on her machine but up to 4x according to comments on Reddit
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/z92vid/measuring_how_much_rusts_bounds_checking_actually/)
    + [Reddit](https://www.reddit.com/r/programming/comments/z9hjpk/how_much_does_rusts_bounds_checking_actually_cost/)
    + [HackerNews](https://news.ycombinator.com/item?id=33805419)
    + added new materials
- Inefficient codegen when accessing a vector with literal indices: https://github.com/rust-lang/rust/issues/50759
  * Assignee: yugr
  * Status: DONE (20-30m)
  * Problem: repetative indexing checks when Vec/slice is accessed multiple times
  * Root cause: Rust has to preserve order of checks (for not so clear reason)
  * Solution: can be worked around via `assert!` hint (looks like generic solution for such situations)
  * LLVM: no good/generic way to solve this in LLVM
  * More materials: NA
- How are bounds checks optimized away? https://users.rust-lang.org/t/how-are-bounds-checks-optimized-away/91737
  * Status: DONE (10m)
  * Assignee: yugr
  * OP asks how bounds checking elimination works
  * Answers: unsafe code in iterators, polyhedral optimization in LLVM (?)
  * More materials: nothing interesting in suggested links
- Rust's Vec indexing is bound-checked by default: https://news.ycombinator.com/item?id=30867188
  * Status: DONE (30m)
  * Assignee: yugr
  * Problem: Rust Vec's are bounds checked which hurts performance (corresponding C++ microbenchmarks shows 2x overhead)
  * Root cause: due to calling extern function it's not possible to move checks outside the loop
  * Solution:
    + use subslicing to avoid checks
    + limit iteration count by vector length
    + code is much better in trunk
  * More materials: added relevant info
- Iterators and eliminating all runtime bounds checks: https://users.rust-lang.org/t/iterators-and-eliminating-all-runtime-bounds-checks/13935
  * Assignee: yugr
  * Status: DONE (5m)
  * Compares Rust to some other language, no relevant info
  * More materials: no new links
- How to zip two slices efficiently: https://users.rust-lang.org/t/how-to-zip-two-slices-efficiently/2048
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: `iter1.zip(iter2)` does not optimize very well
  * Root cause: compiler needs to check if both iterators are not terminated
  * Solution:
    + for slices use explicit subslicing to `len1.min(len2)` to tell compiler that bounds checks can be removed
    + (this is a common technique)
  * More materials: no new links
- How to avoid bounds checks in Rust without unsafe: https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e
  * Assignee: yugr
  * Status: DONE (1h)
  * And oft cited article on avoiding bounds checks
  * Instructions for avoiding bounds checks in Rust programs:
    + subslicing
    + asserts
    + iterators
    + forcing index into bounds via `% len` or `& (len - 1)`
  * Mentions that overhead is small in practice (10%) w/o hard evidence
  * More materials:
    + [bounds-check-cookbook](https://github.com/Shnatsel/bounds-check-cookbook/)
      - companion code for the article
    + [Reddit](https://www.reddit.com/r/rust/comments/10edmjf/how_to_avoid_bounds_checks_in_rust_without_unsafe/)
      - interesting trick to replaced `x[i..(i + 2)]` with `x[i..][..2]` to avoid potential overflow; not sure how it's used though
      - another trick: `let [a, b, c] = data[..3] else { panic!() }`
    + no more relevant articles in blog
- How to avoid bounds checking: https://users.rust-lang.org/t/how-to-avoid-bounds-checking/4433
  * Status: DONE (5m)
  * Assignee: yugr
  * OP asks how to disable bounds checks to measure overhead
  * People suggest potential fixes in stdlib (added to bounds checking section)
  * More materials: nothing new
- Is bound checking the only runtime cost of Rust? https://users.rust-lang.org/t/is-bound-checking-the-only-runtime-cost-of-rust/66661/19
  * Status: DONE (5m)
  * Assignee: yugr
  * OP asks what are the overheads of Rust language
  * People suggest various issues (UFT8 checks, `Rc`, error checking, etc.) but all known by us
  * More materials: nothing new
- How to avoid bounds checks in Rust: https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e
  * Assignee: yugr
  * Status: DONE (30m)
  * This article is very important for bounds checking part
  * It contains
    + motivation behind bounds checks (example, Heartbleed)
    + overheads (avg. 1-3%, max. 15% so nothing like 4-8x in microbenches)
    + all examples are based on Fibonacci
    + how to remove (use explicit `Vec::len()`), reslicing, iterators, `for_each`, `assert!`
    + profiling primer
    + anti-patterns: `debug_assert!`, unsafe
  * Some interesting points:
> I’ve found the optimizations that remove bounds checks to be very reliable —
> once you get them working, they tend to keep workin
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/10edmjf/how_to_avoid_bounds_checks_in_rust_without_unsafe/)
    + [Russian translation](https://habr.com/ru/companies/otus/articles/718012/)
    + [GitHub](https://github.com/Shnatsel/bounds-check-cookbook)
    + no more relevant posts in blog
- Safe elimination of unnecessary bound checks: https://www.reddit.com/r/rust/comments/1iqev5s/safe_elimination_of_unnecessary_bound_checks/
  * Assignee: yugr
  * Status: DONE (30m)
  * Problem: OP loads index from one const table and uses it to index another; he wonders how to get rid of bounds checks in this case
  * Usual suggestions: unsafe, extend tables to power-of-two and use `&`, `cmp::min`
  * Finally he just used power-of-two approach
  * More materials:
    + no new links

# Copy elision/NRVO and placement new

- Does the compiler optimize moves? https://www.reddit.com/r/rust/comments/ykku69/does_the_compiler_optimize_moves/
  * this should be a dedicated perf issue
  * Assignee: yugr
  * Status: DONE (at least 4h)
  * Discusses a known problem when compiler fails to remove `memcpy`'s
  * More materials: added a lot of links
- Does Rust have return value optimization? https://users.rust-lang.org/t/does-rust-have-return-value-optimization/10389
  * Assignee: yugr
  * Status: DONE (5m)
  * General question on how to avoid moves on return w/o good answers
  * More materials: no relevant links
- Copy elision & RVO optimization: https://internals.rust-lang.org/t/copy-elision-rvo-optimization/17276
  * Assignee: yugr
  * Status: DONE (35m)
  * Author proposes to change some pass-by-value calls to pass-by-mut-reference to avoid copying in recursive function
  * The conclusion seems to be that this is not generally correct
  * Not relevant for us
  * More materials: added mats on stack probing
- C++ vector::emplace_back vs rust Vec::push: https://www.reddit.com/r/rust/comments/1eeuqtc/c_vectoremplace_back_vs_rust_vecpushf_copying_v/
  * Assignee: yugr
  * Status: DONE (20m)
  * OP asks whether compiler can do placement new and copy elision
  * SkiFire13 answers that
    + this has been discussed many times but no concrete plans yet
    + implementation existed in the past but wasn't stable
    + compiler tries hard to elide copies
    + it may help to pass lambda that creates struct to `new` function (because then buffer will already be available when creator is called)
  * Other comments:
    + issue is more important for C++ because copies are potentially more expensive (not just `memcpy`)
  * More materials: added links
- How to create large objects directly in heap: https://users.rust-lang.org/t/how-to-create-large-objects-directly-in-heap/26405
  * Assignee: yugr
  * Status: DONE (15m)
  * Problem: OP wants to avoid allocating large struct on stack when calling `Box::new`
  * Root cause: no placement new in Rust and copy elision does not work in such cases
  * Solution: use unsafe APIs (e.g. `Box::alloc`)
    + "Does that mean I cannot create a struct that is bigger than the stack allows? And it will always be created on the stack first and then copied to the heap?"
    + "Semantically yes" (Klabnik)
  * More materials: added
- Introduce deduced parameter attributes: https://github.com/rust-lang/rust/pull/103172
  * Assignee: yugr
  * Status: DONE (15m)
  * A highly technical discussion about addition of new attributes to generated LLVM IR
  * No direct discussions of copy elision so not very relevant for us
  * More materials: issue 103103 (see below)
- Not using the byval attribute loses memcpy optimizations: https://github.com/rust-lang/rust/issues/103103
  * Assignee: yugr
  * Status: DONE (5m)
  * A highly technical discussion of how to avoid `memcpy` in trampoline function
  * The issue is no longer relevant because there is no longer a copy in recent rustc's
  * More materials: none
- Do move forwarding in MIR: https://github.com/rust-lang/rust/issues/32966
  * Assignee: yugr
  * Status: DONE (5m)
  * This is an old issue which suggests to do move elision at MIR level
  * It's unclear why it's still open because move elision already seems to work
  * More materials: nothing relevant
- Pre-RFC: Move-or-borrow elision: https://internals.rust-lang.org/t/pre-rfc-move-or-borrow-elision/13181
  * Assignee: yugr
  * Status: DONE (5m)
  * Author proposes new special syntax to make code with `clone`'s more ergonomic
  * Proposal is not relevant for performance
  * More materials: none
- Stack overflow with Boxed array: https://github.com/rust-lang/rust/issues/53827
  * Assignee: yugr
  * Status: postponed (waiting for joonazan reply, 40m)
  * Problem: stack overflow when trying to initialize large boxed value
  * Root cause: Rust does not have placement new
  * Solution: several approaches based on `unsafe`
  * More materials: references many more issues:
    + [#28008](https://github.com/rust-lang/rust/issues/28008), [#58570](https://github.com/rust-lang/rust/issues/58570), [#40862](https://github.com/rust-lang/rust/issues/40862)
    + (no additional info in them)
    + some downstream issues: [windows-drivers-rs](https://github.com/microsoft/windows-drivers-rs/issues/326), [slint](https://github.com/slint-ui/slint/pull/5415), [iceoryx2](https://github.com/eclipse-iceoryx/iceoryx2/issues/220)
    + joonazan [mentioned](https://github.com/rust-lang/rust/issues/53827#issuecomment-2086359730) that the issue also happens when deriving `Clone` for a large struct but I couldn't repro (just one `memcpy` is present):
```
#[derive(Clone)]
struct S {
    data: [u8; 1 << 24],
}

#[inline(never)]
pub fn foo(p: Box<S>) {
    let p2 = p.clone();
    black_box(p2);
}
```
  I [asked](https://github.com/rust-lang/rust/issues/53827#issuecomment-2798771056) for reprocase.
- Tracking issue for placement new: https://github.com/rust-lang/rust/issues/27779
  * Assignee: yugr
  * Status: DONE (10m)
  * This is RFC about special syntax for placement new which got removed
  * More materials: bugreports in real code:
    + [BTreeMap](https://github.com/rust-lang/rust/issues/81444)
    + [rust-gamedev](https://github.com/rust-gamedev/wg/issues/48)
- Semantics of MIR function calls: https://github.com/rust-lang/rust/issues/71117
  * Status: Wontfix
  * Highly technical, low priority
- Move semantics in C and Rust: https://radekvit.medium.com/move-semantics-in-c-and-rust-the-case-for-destructive-moves-d816891c354b
  * Assignee: yugr
  * Status: DONE (5m)
  * A general comparison of move semantics in Rust and C++ (correctness, exception guarantees, etc.)
  * No performance comparison => irrelevant for us
- Are rust moves of structs, copies or moves Zero Cost Abstractions: https://www.reddit.com/r/rust/comments/1ibjnka/are_rust_moves_of_structs_copies_or_moves_zero/
  * Assignee: yugr
  * Status: DONE (10m)
  * It's not really clear what OP is asking about
  * Basically replies are the usual memcpy not guaranteed to be removed (best effort)
  * More materials: none
- rust ref vs clone performance for POD: https://www.reddit.com/r/rust/comments/1ilt0d3/rust_ref_vs_clone_performance_for_pod/
  * Assignee: yugr
  * Status: DONE (5m)
  * OP asks whether he should prefer pass by copy or by reference
  * No good answers
  * More materials: no links
- Performance Costs/Benefits of Moving vs referencing? https://www.reddit.com/r/rust/comments/10vlec0/performance_costsbenefits_of_moving_vs_referencing/
  * Assignee: yugr
  * Status: DONE (5m)
  * OP asks whether he should prefer pass by copy or by reference
  * No good answers
  * More materials: no links
- RFC: Placement by return: https://github.com/rust-lang/rfcs/pull/2884
  * Assignee: yugr
  * Status: DONE (35m)
  * A follow-up for [issue #27779](https://github.com/rust-lang/rust/issues/27779)
  * Proposes
    + C++-like guaranteed (unnamed) RVO (i.e. elide copies in function returns)
    + `new_with(|| MyStruct { ... })` methods in containers for inplace construction
  * RFC still not accepted but overall positive

# Iterators

- Costs of iterators and Zero Cost Abstractions in Rust: https://github.com/mike-barber/rust-zero-cost-abstractions
  * Assignee: yugr
  * Status: DONE (10m)
  * Main idea: analyzes simple loop in multiple languages
  * Conclusion: no new info for us
  * More materials:
    + [video](https://www.youtube.com/watch?v=mX1BsqTfy6E)
- Big performance problem with closed intervals looping: https://github.com/rust-lang/rust/issues/45222
  * Status: DONE (10m)
  * Assignee: yugr
  * Problem: low performance of closed-interval loops (e.g. no vectorization)
  * Root cause: LLVM does not optimize `RangeInclusive` well
  * Solution: working on different implementation for `..=` syntax in [issue #123741](https://github.com/rust-lang/rust/issues/123741) which will resolve this at runtime
  * More materials: added
- Pre-RFC: Fixing ranges by 2027: https://internals.rust-lang.org/t/pre-rfc-fixing-range-by-2027/19936
  * Assignee: yugr
  * Status: DONE (1h)
  * Core of proposal is to change Ranges (`..`, `..=`) to implement `IntoIterator` instead of `Iterator`
  * Main motivation is better design (e.g. `exhausted` flag is no longer part of `RangeInclusive` so its shorter)
  * Also this allows to replace `x..=y` with `x..(y + 1)` internally in `into_iter` and thus move check outside of the loop
  * Unfortunately
    + will likely result in code bloat (3x for loop bodies)
    + proposal targets 2027 edition
    + maintainer is not very interested in `RangeInclusive` optimization (just included it to "Future possibilities" section and [not implemented in initial PR](https://github.com/rust-lang/rust/pull/136167/))
  * More materials:
    + [RFC](https://github.com/rust-lang/rfcs/pull/3550)
    + [Tracking issue](https://github.com/rust-lang/rust/issues/123741)
- Rust’s iterators are inefficient, and here’s what we can do about it: https://medium.com/@veedrac/rust-is-slow-and-i-am-the-cure-32facc0fdcb
  * Assignee: yugr
  * Status: DONE (50m)
  * Paper is rather old (2016)
  * Paper outlines
    + History of Rust iterators
    + Problems w/ internal iteration (lack of control flow, usability, etc.)
    + Performance issues w/ external iteration
  * Paper suggests
    + Seems to suggest using `iterator::all` with specialized versions for chained iterators
    + Not expressed directly but it seems this is better than `for_each` because it allows `break`'ing
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/5ez38g/rusts_iterators_are_inefficient_and_heres_what_we/)
    + Added more links
- Iterators vs index loops performance: https://users.rust-lang.org/t/iterators-vs-index-loops-performance/52131
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: simple iterator loop is 2x faster than indexing
  * Root-cause:
    + in that version of compiler `&mut` made compiler think that size may be modified
    + both programs are vectorized in trunk
  * Solution: proposed to reslice
  * More materials: no new links
- Performance difference between iterator and for loop: https://users.rust-lang.org/t/performance-difference-between-iterator-and-for-loop/50254
  * Assignee: yugr
  * Status: DONE (5m)
  * OP asks if there's difference between for-loop and external iteration
  * The only main difference is automatic prelloc for external iteration case
  * More materials: added link
- Performance of iterator over for-loops without boundry check: https://users.rust-lang.org/t/performance-of-iterator-over-for-loops-without-boundry-checks/96162
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: comparing slices is faster than comparing via per-element loop (unrelated to iterators really)
  * Root cause: no def answer but most likely slice comparison compiles to `memcmp`
  * Solution: NA
  * More materials: no new links
- Are iterators even efficient? https://users.rust-lang.org/t/are-iterators-even-efficient/36050
  * Assignee: yugr
  * Status: DONE (25m)
  * OP asks for best practices for using iterators
    + He uses some concrete microbenchmark and compares asm size
  * Suggestions:
    + Use open intervals
    + Use `for_each` instead of loop for "chained" iterators (`chain`, `flat_map`, etc.)
      - "If you use combinators that change the control flow, use for_each, otherwise for loops are fine. This includes flat_map, flatten, chain, and a few others" (from [here](https://users.rust-lang.org/t/are-iterators-even-efficient/36050/11))
      - Nice hint !
    + Preallocate vectors
  * More materials: added
- Iter with step_by(2) performs slowly: https://github.com/rust-lang/rust/issues/59281
  * Assignee: yugr
  * Status: DONE (5m)
  * The issue has been fixed in rustc, no new info in this issue
  * More materials: [#57517](https://github.com/rust-lang/rust/issues/57517) also has been fixed (same perf for all benches)
- What additional performance overhead does the use of iterators: https://internals.rust-lang.org/t/what-additional-performance-overhead-does-the-use-of-iterators-and-closures-cause/20296
  * Assignee: yugr
  * Status: DONE (10m)
  * OP asked about potential performance of iterators
  * The only suggestion was to replace `Vec<u8>` with `&mut [u8]
  * More materials: added link
- We all know `iter` is faster than `loop`, but why: https://users.rust-lang.org/t/we-all-know-iter-is-faster-than-loop-but-why/51486
  * Assignee: yugr
  * Status: DONE (15m)
  * OP wonders why iterators (with `for_each`) are faster than loops
  * Answers:
    + First of ["looping and iterators have approximately the same performance on average"](https://users.rust-lang.org/t/we-all-know-iter-is-faster-than-loop-but-why/51486/4)
    + Also [experience shows a lot of variability of performance](https://users.rust-lang.org/t/we-all-know-iter-is-faster-than-loop-but-why/51486/10)
    + Iterators allow elimination of bounds checks (through unchecked accesses), pre-allocation and other iterator specializations
  * Finally all OP's loops produce same asm on recent rustc
  * More materials: links added
- Why for_each is much faster than for loop in release mode: https://stackoverflow.com/questions/76091417/why-for-each-is-much-faster-than-for-loop-in-release-mode-cargo-run-r
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: external inclusive range loop runs much faster than internal
  * Root cause: external iteration optimized by LLVM to simple arithmetic formula
  * Solution: `for_each` is special-cased for `RangeInclusive` and should be used
  * More materials:
- Iterator::fold is a little slow compared to bare loop: https://github.com/rust-lang/rust/issues/76725
  * Assignee: yugr
  * Status: DONE (30m)
  * Problem: replacing `Vec` accumulator in `fold` with `&mut Vec` improves performance
  * Root cause: compiler failed to eliminate move
  * Solution:
    - Proposed `fold_mut` for [stdlib](https://github.com/rust-lang/rust/pull/76746) and [itertools](https://github.com/rust-itertools/itertools/pull/481)
    - PRs rejected as too niche
    - scottmcm suggested to [use lint](https://github.com/rust-lang/rust-clippy/issues/6053) instead (to replace `fold` with `for_each` with `FnMut`)
- Iterator-based approach performs 10x worse than manual implementation https://github.com/rust-lang/rust/issues/80416
    * Assignee: zakhar
    * Status: DONE (15m)
    * Problem: FFT implementation takes 10x more time than manual implementation
    * Root cause: compiler seems to be unable to propagate compile-time knowledge when .cycle() and .skip() are used together
    * Solution: use mutable iterator with .nth() instead of .skip()
- Why are cartesian iterators slower than nested fors? https://users.rust-lang.org/t/why-are-cartesian-iterators-slower-than-nested-fors/42847
  * Assignee: yugr
  * Status: DONE (15m)
  * Problem: iterator loop is 3x slower than indexing
  * Root cause: internal iteration + bounds checking
  * Solution: should use external iteration for chained iters, remove bounds checking via `get_unchecked`
  * More materials: no new links
- Why iterating over the iterator is 3x slower: https://users.rust-lang.org/t/why-iterating-over-the-iterator-is-3x-slower/62098
  * Assignee: yugr
  * Status: DONE (5m)
  * A highly niche issue with iterator code, not relevant for us
  * More materials: no new links
- Is manually looping through a vector always strictly worse then using iterators? https://users.rust-lang.org/t/is-manually-looping-through-a-vector-always-strictly-worse-then-using-iterators/5098
  * Assignee: yugr
  * Status: DONE (5m)
  * This is a discussion of Dijkstra algorithm implementation
  * There are no perf analysis, just suggestions that iterators are generally preferred
  * More materials: none
- Why is iterator so much faster? https://www.reddit.com/r/rust/comments/eiwhkn/why_is_iterator_so_much_faster/
  * Assignee: yugr
  * Status: DONE (20m)
  * Problem: loop w/ external iteration is much faster
  * Root cause: `..=` is slow for internal iteration due to additional check inside loop
  * Solution: replace with `..`
  * More materials: no new links
- About optimizations of for loops: https://internals.rust-lang.org/t/about-optimizations-of-for-loops/18896
  * Assignee: yugr
  * Status: DONE (10m)
  * A highly technical discussion w/o concrete conclusions
  * Problems of for-loops are
    + Lowering happens early (at AST->HIR stage w/o typeinfo)
- Why does iteration over an inclusive range generate longer assembly in Rust than in C++? https://stackoverflow.com/questions/70672533/why-does-iteration-over-an-inclusive-range-generate-longer-assembly-in-rust-than/70680224
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: loop with inclusive range is much more verbose
  * Root cause: usual problem w/ inclusive ranges
  * Root cause: LLVM fails to split loops
  * Solutions: exclusive intervals and `for_each`
- Zero-cost iterator abstractions...not so zero-cost? https://www.reddit.com/r/rust/comments/yaft60/zerocost_iterator_abstractionsnot_so_zerocost/
  * Assignee: yugr
  * Status: DONE (30m)
  * Problem: complex iterator combination results in 10x overhead
  * Root cause: not defined precisely, seems that compiler fails to optimize several combinators in chain and also inlining is not triggered reliably
  * Solution: do not use overly complex iterators
  * More materials: added links
- Why is this functional version faster than my for loop? https://old.reddit.com/r/rust/comments/xtiqj8/why_is_this_functional_version_faster_than_my_for/iqq5v6u/
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: iterator version is much faster than loop
  * Root cause: one of combinators includes a reservation for `collect` call
  * Solution: do manual `with_capacity` in raw loop
- We all know iter is faster than loop: https://users.rust-lang.org/t/we-all-know-iter-is-faster-than-loop-but-why/51486?u=scottmcm
  * Assignee: yugr
  * Status: DONE (5m)
  * OP wonders why iterators are generally faster than loops
  * Not all people agree that they are
  * Iterators may be faster because they avoid bounds checks
  * Bounds checks are not expensive on their own but may hinder other opts
- Map of a Lifetime: https://llogiq.github.io/2017/03/06/lifetime.html
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: `flat_map` much slower than simple nested loop
  * Root cause: not analyzed but most likely a slowdown due to state handling
  * More materials:
    + no new links

# Noalias

- Non-aliasing guarantees of &mut T and rustc optimization: https://users.rust-lang.org/t/non-aliasing-guarantees-of-mut-t-and-rustc-optimization/34386
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: Rust aliasing info not used for optimization
  * Root cause: aliasing used to be disabled by default back then
  * Solution: force enable via flag
  * More materials: N/A
- Why does the Rust compiler not optimize code assuming that two mutable references cannot alias? https://stackoverflow.com/questions/57259126/why-does-the-rust-compiler-not-optimize-code-assuming-that-two-mutable-reference
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: Rust code is less efficient than equivalent C++ code with `restrict`'s
  * Root cause: Rust aliasing optimizations were [disabled by default](https://github.com/rust-lang/rust/issues/54878) back then (and enabled now)
  * More materials: N/A
- Aliasing in Rust: https://www.reddit.com/r/rust/comments/1ery9dy/aliasing_in_rust/
  * Assignee: yugr
  * Status: DONE (30m)
  * OP asks whether Rust analog of C++ strict aliasing (for raw pointers)
  * And it does not (which is not necessarily a bad thing as it makes code more predictable)
  * More materials: no new links
- Enable mutable noalias for LLVM >= 12 by nikic merged: https://www.reddit.com/r/rust/comments/maix26/enable_mutable_noalias_for_llvm_12_by_nikic_merged/
  * Assignee: yugr
  * Status: DONE (20m)
  * A general discussion of Rust noalias
  * No new information but good comparison with C/C++ situation
  * More materials: added links

# Compiler codegen

- Rust under the hood: https://www.youtube.com/watch?v=L8caNpK3Shs
  * Assignee: yugr
  * Status: DONE (20m)
  * Main idea: discusses codegen for some common constructs
    + mentions niche opt but otherwise nothing relevant for us
- Rust loves LLVM: https://www.youtube.com/watch?v=Kqz-umsAnk8 (https://llvm.org/devmtg/2024-10/slides/keynote/Popov-Rust_Heart_LLVM.pdf)
  * Assignee: yugr
  * Status: DONE (15m)
  * General overview of Rust-LLVM integration, touches several perf-related topics but no new info:
    + bounds checks
    + memcpy elimination
    + inclusive ranges
  * More materials: none
- Rust and LLVM in 2021: https://llvm.org/devmtg/2021-02-28/slides/Patrick-rust-llvm.pdf
  * Assignee: yugr
  * Status: DONE (20m)
  * Slides for LLVM dev meeting
    + A general overview of new features
    + Discusses CGU problem (and how ThinLTO fixes it), PGO, aliasing, various LLVM fixes
  * More materials: no new links
- Improving crypto code in Rust using LLVM’s optnone: https://blog.trailofbits.com/2022/02/01/part-2-rusty-crypto/
  * Assignee: yugr
  * Status: DONE (5m)
  * Author needs constant time execution in crypto code so he disables optimizations
    + There are instructions on building and small updates of compiler
  * More materials: no relevant materials in https://blog.trailofbits.com/categories/rust/
- Why Rust doesn't need a standard div_rem: An LLVM tale: https://codspeed.io/blog/why-rust-doesnt-need-a-standard-divrem
  * Assignee: yugr
  * Status: DONE (35m)
  * Author investigates why Rust does not have `div_rem` API in stdlib
    + Rust relies on LLVM to combine `div` and `rem` in IR
    + Fusion happens but Rust also inserts checks
    + Checks can be avoided by using unchecked intrinsics
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/173wr86/why_rust_doesnt_need_a_standard_div_rem_an_llvm)
    + no more relevants posts
- Asm snippets: https://www.eventhelix.com/rust/
  * Status: backlog
- A cool Rust optimization story: https://quickwit.io/blog/search-a-sorted-block
  * Assignee: yugr
  * Status: DONE (10m)
  * Main idea: OP used different implementations of binary search in his library
    + Basically the conclusion is that compiler is not always perfect e.g. [stopped generating branchless code](https://bugs.llvm.org/show_bug.cgi?id=40027) at some point
  * More materials:
    + Reddit comments: https://www.reddit.com/r/rust/comments/qde4w7/a_cool_rust_optimization_story/ (nothing relevant)
- Addressing Rust optimization failures in LLVM: http://www.khei4.com/gsoc2023/
  * Assignee: yugr
  * Status: DONE (5m)
  * Main idea: just solved some LLVM bugs, no generalizations
  * More materials: N/A
- Why isn't the for loop optimized better (in this one example)? https://www.reddit.com/r/rust/comments/15tvuio/why_isnt_the_for_loop_optimized_better_in_this/
  * Assignee: yugr
  * Status: DONE (30m)
  * Problem: loop slowdown when using inclusive ranges
  * Root cause: inclusive ranges are slower by design (explained in comments)
  * Solution: replace with exclusive range with explicit addition
  * LLVM: one of commenters suggest how it can be fixed in LLVM (via loop splitting)
  * More materials: no new mats in suggestions
- Assembly examples of missed Rust compiler optimizations: https://www.reddit.com/r/rust/comments/14zhb0s/assembly_examples_of_missed_rust_compiler/
  * Assignee: yugr
  * Status: DONE (10m)
  * Main idea: two examples of missed LLVM optimizations
    + Not relevant
  * More materials: none
- Rust `[#inline]` annotations discussion https://github.com/rust-lang/hashbrown/pull/119
  * Assignee: zakhar
  * Status: DONE (15m)
  * Main idea: mostly discusses about `[#inline]` effect on compile time
    + Not our topic
  * More materials: N/A
- Inline In Rust: Inline In Rust: https://matklad.github.io/2021/07/09/inline-in-rust.html
  * Status: DONE (5m)
  * Assignee: yugr
  * Articles describes what `#[inline]` does
    + it is different from C `inline` (embeds function IR into crate's .o, allowing it to be inlined into dependents)
    + template functions are already `#[inline]`
  * More materials: no relevant mats
- Why doesn't the Rust optimizer remove those useless instructions: https://stackoverflow.com/questions/45586159/why-doesnt-the-rust-optimizer-remove-those-useless-instructions-tested-on-godb
  * Status: DONE (30m)
  * Assignee: yugr
  * Problem: useless `push`/`pop` in function
    * Need to add `#[inline(never)]`, otherwise `rustc` won't generate body (see [issue #119850](https://github.com/rust-lang/rust/issues/119850) for details)
  * Root cause: Godbolt uses some spurious debug flags which trigger this
    + This is no longer an issue
    + See https://github.com/rust-lang/rust/issues/11906
  * Solution: not a problem for real code
  * More materials: none
- How the Rust Compiler Works, a Deep Dive: https://www.youtube.com/watch?v=Ju7v6vgfEt8
  * Status: DONE (2h)
  * Assignee: yugr
  * Video about Rust compiler:
    + walk though different IRs (AST, HIR, THIR, MIR)
    + some info on rustc driver
    + not too many details
- Should small Rust structs be passed by-copy or by-borrow? https://www.forrestthewoods.com/blog/should-small-rust-structs-be-passed-by-copy-or-by-borrow/
  * Assignee: yugr
  * Status: DONE (15m)
  * Investigates whether passing by value is faster than by reference
  * No investigation of ABI or optimizer effects (e.g. author assumes it's equivalent to passing in regs)
  * No relevant information in this article
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/zzxz2e/should_small_rust_structs_be_passed_bycopy_or/)
    + No more links in blog
- Inline in Rust: https://matklad.github.io/2021/07/09/inline-in-rust.html
  * Assignee: yugr
  * Status: DONE (5m)
  * Just general discussion of `#[inline]` enabling inlining across crates (mini-LTO)
  * No new info
- Rust staticlibs and optimizing for size: https://internals.rust-lang.org/t/rust-staticlibs-and-optimizing-for-size/5746
  * Assignee: yugr
  * Status: DONE (20m)
  * Rust compiles with `-ffunction-sections -Wl,--gc-sections
  * This is not always working as well as LTO because Rust may export unnecessary symbols
    + post is old, not clear if this problem is still relevant ?
    + i wasn't able to find relevant discussions...
- Inspecting rustc LLVM optimization remarks using cargo-remark: https://kobzol.github.io/rust/cargo/2023/08/12/rust-llvm-optimization-remarks.html
  * Assignee: yugr
  * Status: DONE (15m)
  * Author has added `cargo remark` tool for emitting opt. remarks for Rust code
    + Wrapper for `RUSTFLAGS="-Cdebuginfo=1 -Cremark=all -Zremark-dir=/tmp/remarks" cargo build --release`
    + Specifically for autovec: `-g -O -C llvm-args='--pass-remarks-missed=loop-vectorize --pass-remarks-analysis=loop-vectorize'`
    + Compatible with optview2 tool
  * Experience in real projects: too many remarks, hard to understand how to fix code
  * Little interest/adoption in community
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/15p4thi/cargoremark_examine_rustc_llvm_optimization/)

# Niches

- RFC: Alignment niches for references types: https://github.com/rust-lang/rfcs/pull/3204
  * Assignee: yugr
  * Status: DONE (15m)
  * Proposal to extend niche optimizer to use alignment padding in references for discriminators
  * Prototype available under [-Z reference-niches](https://github.com/rust-lang/rust/pull/113166)
  * More materials: no new links
- Niches: https://github.com/rust-lang/rfcs/pull/3334
  * Assignee: yugr
  * Status: DONE (30m)
  * Proposal to allow users to specify "invalid" values in their types via annotations (to be used by niche optimization)
  * Also contains ideas on other niche opportunities:
    + use pointer/reference alignment padding
    + Use invalid pointer/reference ranges (e.g. addresses in zero memory page)
    + Various invalid OS-specific pointer patterns
  * Closed in favor of [#103724](https://github.com/rust-lang/rust/pull/103724)

# Data structures performance

If a common advice for complex (self-ref) structs is to use `Rc`/`Arc`,
we should add them to overheads.

- Learn Rust With Entirely Too Many Linked Lists: https://rust-unofficial.github.io/too-many-lists/
  * Status: backlog
- https://dev.to/arunanshub/self-referential-structs-in-rust-33cm
  * Status: backlog
- An Optimization That’s Impossible in Rust! https://tunglevo.com/note/an-optimization-thats-impossible-in-rust/
  * Status: backlog
  * Translation: https://habr.com/ru/companies/beget/articles/842868/
  * Comments: https://www.reddit.com/r/rust/comments/1f87siw/an_optimization_thats_impossible_in_rust/
- How can we teach people about self-referential types? https://users.rust-lang.org/t/how-can-we-teach-people-about-self-referential-types/65362
  * Assignee: yugr
  * Status: DONE (30m)
  * List of general methods for dealing with self-ref:
    + dedicated object for owning referenced entities (e.g. allocator) in caller
      - the most recommended approach
      - e.g. Parser does not need to own the buffer
    + indices
      - e.g. store graph as array of nodes + pred/succ indices
    + Rc/RefCell
    + (for performance-critical code) raw pointers and unsafe
      - easy to make mistakes even when using wrappers like Pin
  * More materials:
    + no relevant links
- Is RefCell a zero-cost abstraction: https://users.rust-lang.org/t/is-refcell-a-zero-cost-abstraction/61888
  * Assignee: yugr
  * Status: DONE (20m)
  * General conclusion is RefCell/Rc are not zero-cost abstractions because they exist to verify language invariants
  * Discussion then devolved into how non-trivial reference graphs are/should be represented in language (not relevant for us)
  * More materials:
    + no relevant links
- Optimization of RefCell borrow operations: https://users.rust-lang.org/t/optimisation-of-refcell-borrow-operations/65214
  * Assignee: yugr
  * Status: DONE (5m)
  * OP wondered whether RefCell's checks could be removed if compiler can prove (via global analysis) that they are not needed
  * Answers are that
    + language designers try not to rely on global analyses
    + it'll not work in many practical cases
    + whenever access can be proven user can simply use normal refs
- RefCell, why borrowing is checked only in runtime: https://users.rust-lang.org/t/refcell-why-borrowing-is-checked-only-in-runtime/52721/5
  * Assignee: yugr
  * Status: DONE (5m)
  * Very similar to "Optimization of RefCell borrow operations"
  * "RefCell is specifically intended for the cases that are too complicated for the compiler's checks to verify"
  * "RefCell is for those times it is NOT provable"
  * More materials:
    + no relevant links
- How heavy is Rc<RefCell<T>? https://www.reddit.com/r/rust/comments/jkh99u/how_heavy_is_rcrefcellt/
  * Assignee: yugr
  * Status: DONE (15m)
  * Just some general comments w/o concrete numbers:
    + e.g. also suggest to use dedicated owners e.g. [slabs](https://www.reddit.com/r/rust/comments/jkh99u/comment/gajrru9/)
      or [arenas](https://www.reddit.com/r/rust/comments/jkh99u/comment/gakm1bn/)
    + a user claims that dedicated ownership is ["slightly faster"](https://www.reddit.com/r/rust/comments/jkh99u/comment/lw33boh/)
  * More materials:
    + no new links
- How expensive is Rc<RefCell> + .borrow_mut() ? https://users.rust-lang.org/t/how-expensive-is-rc-refcell-borrow-mut/26713
  * Assignee: yugr
  * Status: DONE (10m)
  * Lists out [overheads](https://users.rust-lang.org/t/how-expensive-is-rc-refcell-borrow-mut/26713/5)
    but no concrete measurements:
    + calls to borrow/borrow_mut require a write so an exclusive cache-line access
    + it's ok for borrow_mut (it'll likely write anyway) but not for read-only borrow
    + extra fields may increase D$ pressure
- Rust — performance overhead of RefCell: https://medium.com/@techhara/rust-performance-overhead-of-refcell-adaa634b6490
  * Status: backlog

# Fast math

- Imprecise floating point operations: https://github.com/rust-lang/rust/issues/21690
  * Assignee: yugr
  * Status: DONE (30m)
  * This is a request for `-ffast-math` for Rust
  * A lot of links to related issues
  * A lot of discussions of alternatives but only 2 clear results:
    + Maintainers will _never_ allow a global `-ffast-math` flag (which will cover dependencies)
    + Maintainers consider fast intrinsics to be enough
  * More materials: no new links

# Autovec

- Unleash the Power of Auto-Vectorization in Rust with LLVM: https://www.luiscardoso.dev/blog/auto-vectorization/
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: there is not problem actually, the article just illustrates how autovec works, etc.
  * More materials: no more interesting mats on this blog
- Taking Advantage of Auto-Vectorization in Rust: https://www.nickwilcox.com/blog/autovec/
  * Assignee: yugr
  * Status: DONE (20m)
  * OP investigates ways to improve simple loop with autovec
    + A useful hint to detect missing autovec is to look for "ss"-suffixed SSE instructions (Single Scalar) in asm
    + Reslicing does not help in this case
    + Replacing vector with raw arithmetic with vector of structs fixes it
    + Reddit provides [solution](https://www.reddit.com/r/rust/comments/gkq0op/comment/fqsuzrk/) w/ iterators
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/gkq0op/taking_advantage_of_autovectorization_in_rust/)
    + added more links
- Nine Rules for SIMD Acceleration of Your Rust Code: https://towardsdatascience.com/nine-rules-for-simd-acceleration-of-your-rust-code-part-1-c16fe639ce21 and https://medium.com/towards-data-science/nine-rules-for-simd-acceleration-of-your-rust-code-part-2-6a104b3be6f3
  * Assignee: yugr
  * Status: DONE (10m)
  * The article is a general intro to SIMD programming in Rust (crates e.g. core::simd, techniques, algorithms)
  * Not relevant for compiler performance optimizations
  * More materials:
    + [Reddit pt. 1](https://www.reddit.com/r/rust/comments/18hj1m6/nine_rules_for_simd_acceleration_of_your_rust/)
    + [Reddit pt. 2](https://www.reddit.com/r/rust/comments/18lccf4/part_2_nine_rules_for_simd_acceleration_of_your/)
- Taming Floating-Point Sums: https://orlp.net/blog/taming-float-sums/
  * Assignee: yugr
  * Status: DONE (15m)
  * OP suggests to use FP intrinsics to enable vectorization of FP loop
  * He suggests that using `-ffast-math` in presence of non-finite numbers is UB but does not give any proof
  * More links:
    + [Reddit](https://www.reddit.com/r/rust/comments/1d0jrpe/taming_floatingpoint_sums/)
    + [HN](https://news.ycombinator.com/item?id=40477604)
- Auto-vectorization in Rust: https://users.rust-lang.org/t/auto-vectorization-in-rust/24379
  * Assignee: yugr
  * Status: DONE (35m)
  * Problem: simple numeric loops fails to vectorize in Rust (but does in C++/Fortran)
  * Root cause: lack fast math (so `fmadd` not used), `y/sqrt(x)` not replaced with `y * 1/sqrt(x)`
  * Solution: use `-C llvm-args=-ffast-math` (does not seem to work) and float intrinsics
  * More materials: added links
- Understanding Rusts Auto-Vectorization and Methods for speed: https://users.rust-lang.org/t/understanding-rusts-auto-vectorization-and-methods-for-speed-increase/84891
  * Assignee: yugr
  * Status: DONE (25m)
  * OP wonders how to achieve autovec and optimize Rust numeric code in general
  * Suggestions:
    + fast math intrinsics
    + use iterators and internal iteration to avoid bounds checking
    + reslicing
    + slices instead of `Vec`'s
  * More materials: no new links
- We need to do better in the benchmarks game: https://users.rust-lang.org/t/we-need-to-do-better-in-the-benchmarks-game/7317
  * Assignee: yugr
  * Status: DONE (0m)
  * Some random old discussion of benchmarks game results, not relevant
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
- Can You Trust a Compiler to Optimize Your Code? https://matklad.github.io/2023/04/09/can-you-trust-a-compiler-to-optimize-your-code.html
  * Assignee: yugr
  * Status: DONE (15m)
  * A very high-level article
  * Suggests using flat data structures and `chunks_exact` iterator and avoiding dependencies across iterations (e.g. `&&`, `break`)
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/15f5p94/can_you_trust_a_compiler_to_optimize_your_code/)
    + [Russian translation](https://habr.com/ru/companies/timeweb/articles/759326/)
    + no new links
- Iterator::max with reference-type items cannot leverage SIMD instructions: https://github.com/rust-lang/rust/issues/106539
  * Assignee: yugr
  * Status: DONE (20m)
  * Problem: finding maximum of slice via `iter().max()` is much slower than special crafted iterator
  * Root cause: `max()` does not require `Copy` types so works on references; LLVM has hard time optimizing pointer accesses
  * Solutions:
    + use `iter().copied().max()` to remove dereference and allow autovec
    + specialize `max()` for `Copy`able types (NYI)
    + improve LLVM to handle this case better (seems to be [fixed](https://github.com/rust-lang/rust/issues/129583) already)
  * More materials:
    + one of suggestions (to use `copied()`) is actually a suggested perf guideline (see [perf-book #83](https://github.com/nnethercote/perf-book/issues/83))
    + added links
- SIMD Vector/Slice/Chunk Addition: https://www.reddit.com/r/rust/comments/154vowr/simd_vectorslicechunk_addition/
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: simple `slice.iter().sum()` is faster than SIMD-friendly iteration with `chunks_exact()`
  * Root cause: compiler failed to remove bounds check in intra-vector loop
  * Solution: use `zip` or other simple code
- simd-itertools: simd-accelerated iterators for "find", "filter", "contains" and many more: https://www.reddit.com/r/rust/comments/1e3ps2a/simditertools_simdaccelerated_iterators_for_find/
  * Assignee: yugr
  * Status: DONE (10m)
  * A small wrapper on top of standard iterators which does `chunks_exact` internally to facilitate autovec
  * More materials: no new links
- Memory-safe PNG decoders now vastly outperform C PNG libraries: https://www.reddit.com/r/rust/comments/1ha7uyi/memorysafe_png_decoders_now_vastly_outperform_c/
  * Assignee: yugr
  * Status: DONE (50m)
  * Rust PNG libs outperform C ones
  * The winning package (png by Shnatsel) is based on autovec
    + Code is specifically structured to enable it
  * A lot of interesting discussions of autovec:
    + What enables and disables it in Rust
    + How to track if it worked
  * More materials: no new links
- Mir optimization pass that implements auto-vectorization: https://internals.rust-lang.org/t/mir-optimization-pass-that-implements-auto-vectorization/16360
  * Assignee: yugr
  * Status: DONE (10m)
  * OP proposes a MIR-level vectorization; it supersedes LLVM vectorizer in some cases (e.g. when bounds checks are in place)
  * Proposal violates safety guarantees so was rejected
  * Suggested alternatives: reslicing, iterators
- Speeding up RGB to grayscale conversion in Rust: https://coaxion.net/blog/2018/01/speeding-up-rgb-to-grayscale-conversion-in-rust-by-a-factor-of-2-2-and-various-other-multimedia-related-processing-loops/
  * Assignee: yugr
  * Status: DONE (20m)
  * OP investigates various methods to speed up his kernel:
    + `assert!` (`assert_eq!` caused slowdown !)
    + `exact_chunks` iterator (it was first introduced to stdlib as part of this work)
  * Finally he was able to fully eliminate bounds checks
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/7rxrka/speeding_up_rgb_to_grayscale_conversion_in_rust/)
    + no new links
- Auto-vectorization fails in a for-loop: https://users.rust-lang.org/t/auto-vectorization-fails-in-a-for-loop/62612
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: autovec started to fail when using `marbles[8*i..8*(i+1)]` syntax
  * Root cause: unclear, most likely LLVM IR was too complex for vectorizer
  * Solution: help vectorizer with `chunks_exact`
  * More materials: added links
- Rust autovectorization issues: https://users.rust-lang.org/t/rust-autovectorization-issues/126386
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: C++ `-Ofast` code much faster than Rust due to autovec
  * Root cause: FP computations not vectorized due to fast math
  * Solution: in this case it's possible to simply rewrite the algorithm to enable autovec
  * More materials: no new links
- Rust and C++ on Floating-point Intensive Code: https://www.reidatcheson.com/hpc/architecture/performance/rust/c++/2019/10/19/measure-cache.html
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: C++ `-Ofast` code much faster than Rust due to autovec
  * Root cause: FP computations not vectorized due to fast math
  * Solution: same as in "Rust autovectorization issues"
  * More materials:
    + [HN](https://news.ycombinator.com/item?id=21342501)
    + no new links
- SIMD in zlib-rs: https://tweedegolf.nl/en/blog/153/simd-in-zlib-rs-part-1-autovectorization-and-target-features
  * Assignee: yugr
  * Status: DONE (10m)
  * A ver y recent article
  * General overview of autovec:
    + start with simple loop (based on iterators, autovectorizes)
    + get rid of epilig loop via `exact_chunks` iterator
    + then manually multiversion (via `target_feature` and const template param) for AVX2 vector size (dispatched via wrapper)
  * More materials:
    + Added "zlib-rs is faster than C" post
- Unnecessary Optimization in Rust: https://emschwartz.me/unnecessary-optimization-in-rust-hamming-distances-simd-and-auto-vectorization/
  * Assignee: yugr
  * Status: DONE (10m)
  * Compares several SIMD implementations of Hamming distance
  * The fastest uses autovec (based on `exact_chunks`)
  * More materials:
    + no more perf-relevant posts in blog
    + [Reddit](https://www.reddit.com/r/rust/comments/1hk0bry/unnecessary_optimization_in_rust_hamming/)

# Stack probing

- Replace stack overflow checking with stack probes: https://github.com/rust-lang/rust/issues/16012
  * Assignee: yugr
  * Status: DONE (20m)
  * Proposes stack probes (analog of GCC's `-fstack-check`)
  * Discusses implementation in detail
  * More materials: a lot of links to stackoverflow bugs
- probestack.rs: https://github.com/rust-lang/compiler-builtins/blob/master/compiler-builtins/src/probestack.rs
  * Assignee: yugr
  * Status: DONE (5m)
  * Typical stack probing asm implementation
  * More materials: none
- Is rust guaranteed to detect stack overflows? https://users.rust-lang.org/t/is-rust-guaranteed-to-detect-stack-overflows/52593
  * Assignee: yugr
  * Status: DONE (5m)
  * OP expected Rust to panic on stack overflow but it turns out that panicking in such cases is best effort
  * More materials: a lot of similar posts, added the most popular
- Bringing Stack Clash Protection to Clang / X86: https://blog.llvm.org/posts/2021-01-05-stack-clash-protection/
  * Assignee: yugr
  * Status: DONE (15m)
  * Overview of stack probing support in LLVM (both Clang and Rust):
    + Motivation (Qualys report)
    + Algorithm
    + No perf overhead detected
  * More materials: none

# Nethercote

Taken from https://nnethercote.github.io/2025/03/19/how-to-speed-up-the-rust-compiler-in-march-2025.html

Nethercote is top industry expert, need to pay close attention to his posts

- [How to speed up the Rust compiler](https://blog.mozilla.org/nnethercote/2016/10/14/how-to-speed-up-the-rust-compiler/)
  * Assignee: yugr
  * Status: DONE (25m)
  * Overview of Rust build systems and dev process (useful reading if doing some rustc work):
    + Used [rustc-benchmarks](https://github.com/rust-lang-deprecated/rustc-benchmarks) (no longer used)
  * Optimizations:
    + Mostly high-level opts (making allocations lazy, replacing `String` with `Cow<str>`)
    + Mentions problem with CGUs
- [How to speed up the Rust compiler some more](https://blog.mozilla.org/nnethercote/2016/11/23/how-to-speed-up-the-rust-compiler-some-more/)
  * Assignee: yugr
  * Status: DONE (15m)
  * Optimizations:
    + High-level (avoiding unnecessary work, less aggressive compression, different hash function, etc.)
    + Fixed outsized enum
    + Pass references instead of copies
    + [#36933](https://github.com/rust-lang/rust/pull/36993):
      - Replace enums with bitmasks
      - Replace `match` with if-else ordered by frequency
- [How to speed up the Rust compiler in 2018](https://blog.mozilla.org/nnethercote/2018/04/30/how-to-speed-up-the-rust-compiler-in-2018/)
  * Assignee: yugr
  * Status: DONE (5m)
  * LLVM starts to take 50% of compile time
  * New benchmark suite is [rustc-perf](https://github.com/rust-lang/rustc-perf)
  * Optimizations:
    + High-level (reduce data type, `ok_or` -> `ok_or_else`, laziness, etc.)
- [The Rust compiler is getting faster](https://blog.mozilla.org/nnethercote/2018/05/17/the-rust-compiler-is-getting-faster/)
  * Assignee: yugr
  * Status: DONE (5m)
  * Just intro to rustc perf GUI
- [How to speed up the Rust compiler some more in 2018](https://blog.mozilla.org/nnethercote/2018/06/05/how-to-speed-up-the-rust-compiler-some-more-in-2018)
  * Assignee: yugr
  * Status: DONE (15m)
  * LLVM starts to dominate compile time
  * Optimizations:
    + High-level (SmallVec, laziness, change data types, etc.)
    + Manual `#[inline]` annotations
- [How to speed up the Rust compiler in 2018: NLL edition](https://blog.mozilla.org/nnethercote/2018/11/06/how-to-speed-up-the-rust-compiler-in-2018-nll-edition/)
  * Assignee: yugr
  * Status: DONE (5m)
  * Optimizations:
    + High-level (avoid realloc, change container, etc.)
    + Force inlining
- [How to speed up the Rust compiler in 2019](https://blog.mozilla.org/nnethercote/2019/07/17/how-to-speed-up-the-rust-compiler-in-2019/)
  * Assignee: yugr
  * Status: DONE (5m)
  * Optimizations:
    + High-level (move rare large state to separate data structure, avoid repeated checks, etc.)
    + Change `assert!` to `debug_assert!`
    + Preallocate less aggressively
- [The Rust compiler is still getting faster](https://blog.mozilla.org/nnethercote/2019/07/25/the-rust-compiler-is-still-getting-faster/)
  * Assignee: yugr
  * Status: DONE (5m)
  * Just analysis of compiler speed improvements
- [How to speed up the Rust compiler some more in 2019](https://blog.mozilla.org/nnethercote/2019/10/11/how-to-speed-up-the-rust-compiler-some-more-in-2019/)
  * Assignee: yugr
  * Status: DONE (15m)
  * Optimizations:
    + High-level (reduce size of data structures, boxing large results, etc.)
    + Splitting some function to two variants: hot `#[inline(always)]` and cold `#[inline(never)]` wrapper which calls it
    + Try to specialize debug impls via
      - `if cfg!(debug_assertions)`
      - `#[cfg(debug_assertions)]`
      - `#[cfg_attr(debug_assertions, inline)]`
      (no benefit overall)
    + Avoid `chain` iterator (by manually doing two loops)
- [How to speed up the Rust compiler one last time in 2019](https://blog.mozilla.org/nnethercote/2019/12/11/how-to-speed-up-the-rust-compiler-one-last-time-in-2019/)
  * Assignee: yugr
  * Status: DONE (5m)
  * High-level opts
- [How to speed up the Rust compiler in 2020](https://blog.mozilla.org/nnethercote/2020/04/24/how-to-speed-up-the-rust-compiler-in-2020/)
  * Assignee: yugr
  * Status: DONE (20m)
  * Optimizations:
    + High-level (do not produce both IRs at same time, specialize function for common case, reusing parser, etc.)
- [How to speed up the Rust compiler some more in 2020](https://blog.mozilla.org/nnethercote/2020/08/05/how-to-speed-up-the-rust-compiler-some-more-in-2020/)
  * Assignee: yugr
  * Status: DONE (20m)
  * Optimizations:
    + High-level (refactor `Iterator` methods to do less function calls, increase initial `Vec` alloc, boxing, etc.)
    + Extract non-generic part of generic `RawVec::grow`
- [How to speed up the Rust compiler one last time](https://blog.mozilla.org/nnethercote/2020/09/08/how-to-speed-up-the-rust-compiler-one-last-time/)
  * Assignee: yugr
  * Status: DONE (5m)
  * Wrap-up and summary of previous work after switch to other tasks at Mozilla
- [The Rust compiler has gotten faster again](https://nnethercote.github.io/2021/11/12/the-rust-compiler-has-gotten-faster-again.html)
  * Assignee: yugr
  * Status: DONE (0m)
  * Summary of rustc performance changes w/o any analysis
- [How to speed up the Rust compiler in 2022](https://nnethercote.github.io/2022/02/25/how-to-speed-up-the-rust-compiler-in-2022.html)
  * Assignee: yugr
  * Status: DONE (20m)
  * Optimizations:
    + High-level (do not search empty hashtab, change unlikely `Result` to panic, interning, etc.)
    + Replace `assert!` w/ `debug_assert!`
- [How to speed up the Rust compiler in April 2022](https://nnethercote.github.io/2022/04/12/how-to-speed-up-the-rust-compiler-in-april-2022.html)
  * Assignee: yugr
  * Status: DONE (5m)
  * Optimizations:
    + High-level (reduce `SmallVec` default size, avoid excessive cloning, [match to table-driven](https://github.com/rust-lang/rust/pull/94776), etc.)
    + Forced inline
- [How to speed up the Rust compiler in July 2022](https://nnethercote.github.io/2022/07/20/how-to-speed-up-the-rust-compiler-in-july-2022.html)
  * Assignee: yugr
  * Status: DONE (20m)
  * Optimizations:
    + High-level (reduce code in derived traits, fast checks, `SmallVec::insert` at end of vector, etc.)
    + Jemalloc update
- [How to speed up the Rust compiler in October 2022](https://nnethercote.github.io/2022/10/27/how-to-speed-up-the-rust-compiler-in-october-2022.html)
  * Assignee: yugr
  * Status: DONE (10m)
  * Optimizations:
    + High-level (enum shrinkage, replacing containers, etc.)
    + Bump LLVM version, use LTO and BOLT
- [How to speed up the Rust compiler in March 2023](https://nnethercote.github.io/2023/03/24/how-to-speed-up-the-rust-compiler-in-march-2023.html)
  * Assignee: yugr
  * Status: DONE (10m)
  * Optimizations:
    + Codegen opts (change LLVM IR to satisfy FastISel, larger BBs)
    + High-level opts (data structure shrinkage, replace `Vec` w/ `ThinVec`)
- [Back-end parallelism in the Rust compiler](https://nnethercote.github.io/2023/07/11/back-end-parallelism-in-the-rust-compiler.html)
  * Assignee: yugr
  * Status: duplicate (zakhar)
- [How to speed up the Rust compiler: data analysis assistance requested!](https://nnethercote.github.io/2023/07/25/how-to-speed-up-the-rust-compiler-data-analysis-assistance-requested.html)
  * Assignee: yugr
  * Status: DONE (0m)
  * Just a request for help with building simple cost model for CGU split
- [How to speed up the Rust compiler: data analysis update](https://nnethercote.github.io/2023/08/01/how-to-speed-up-the-rust-compiler-data-analysis-update.html)
  * Assignee: yugr
  * Status: DONE (0m)
  * Results from previous analysis were inconclusive
  * This is another request, this time with more data
- [How to speed up the Rust compiler in August 2023](https://nnethercote.github.io/2023/08/25/how-to-speed-up-the-rust-compiler-in-august-2023.html)
  * Assignee: yugr
  * Status: DONE (30m)
  * Explains why Rustc speed improvements are small
  * Optimizations:
    + High-level (fast hash funcs, fix buf size, mark derived hash as inline, caching)
    + CGU tuning
    + LLVM bump
  * More materials:
    + Several good posts at kobzol.github.io (post about opt remarks already added)
    + [Talk at RustNL 2023](https://www.youtube.com/watch?v=q2vJ8Faundw)
- [How to speed up the Rust compiler in March 2024](https://nnethercote.github.io/2024/03/06/how-to-speed-up-the-rust-compiler-in-march-2024.html)
  * Assignee: yugr
  * Status: DONE (5m)
  * Profiles are now flat
  * Optimizations:
    + High-level (cache, inline fmt())
    + Rustc now built w/ single CGU
    + Llvm bump
- [How to speed up the Rust compiler in March 2025](https://nnethercote.github.io/2025/03/19/how-to-speed-up-the-rust-compiler-in-march-2025.html)
  * Assignee: yugr
  * Status: DONE (10m)
  * Optimizations:
    + LLD and PGU used by default to build rustc
    + LLVM bump
    + Use protected visibility to speedup startup
    + Faster hardware feature checking
  * More materials: added visibility section

# Visibility

Note that currently Rustc is NOT using non-default (protected) ELF visibility by default
(no pun intended). Can be checked via
```
for t in `rustc --print target-list`; do
  echo "### $t"
  rustc +nightly -Z unstable-options --target=$t --print target-spec-json | grep protect
done
```

- Expose default_hidden_visibility as a rustc command line option: https://github.com/rust-lang/compiler-team/issues/656
  * Assignee: yugr
  * Status: DONE (5m)
  * This is where it all started
  * Added flag is analog of `-fvisibility=hidden`
- Use protected visibility by default on ELF platforms: https://github.com/rust-lang/rust/issues/105518
  * Assignee: yugr
  * Status: DONE (1h)
  * This first proposed to change default visibility to protected
  * It was merged in
    + [initial attempt](https://github.com/bjorn3/rust/commit/0a413310130d61e362cc1ec3dd956e6f8b128725)
      - set `protected` for all Rust symbols (if `hidden` not selected via cmdline flag)
      - failed rustc bootstrap due to issue in GNU ld
    + [#130005](https://github.com/rust-lang/rust/pull/130005)
      - this PR uses ELF-default visibility for C symbols (`no_mangle`?) and default visibility for Rust symbols
      - default visibility can be selected (in order of prio) via cmdline flag, target default, interposable
    + [#131634](https://github.com/rust-lang/rust/pull/131634)
      - set `protected` default visility in rustc bootstrap if built with LLD
- Rust dylib rabbit holes: https://davidlattimore.github.io/posts/2024/08/27/rust-dylib-rabbit-holes.html
  * Assignee: yugr
  * Status: DONE (20m)
  * Summary of discussion
- -Z default-visibility option: https://github.com/rust-lang/compiler-team/issues/782
  * Assignee: yugr
  * Status: DONE (10m)
  * This discussion started as part of work on 105518
  * Two proposals here:
    + Extend visibility flag to cover any visibility
    + Make `protected` the default visibility

# Thread-locals

From [here](https://hackmd.io/@Q66MPiW4T7yNTKOCaEb-Lw/gosim-unconf-rust-codegen):
> Thread-local storage (TLS) model is very pessimistic by default.
> Makes rayon much slower (tls_get_addr very high in profiles).

- Rust thread_local bad performance? https://users.rust-lang.org/t/rust-thread-local-bad-performance/4385
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: Rust version with `thread_local!` is much slower than C `__thread`
  * Root cause: `borrow_mut` on every iteration
  * Solution: remove borrowing, use `Cell`, use `#[thread_local]`
  * More materials: no new links
- Rust `thread_local!`s are surprisingly expensive: https://swatinem.de/blog/slow-thread-local/
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: `thread_local!` too slow
  * No details, investigation or explanation
  * More materials: no relevant links in blog
- Fast Thread Locals In Rust: https://matklad.github.io/2020/10/03/fast-thread-locals-in-rust.html
  * Assignee: yugr
  * Status: DONE (30m)
  * There are 2 APIs for TLS in Rust:
    + `#[thread_local]`
      - transforms directly to LLVM attribute but not stable/finalized
      - hint for compiler, basically just forwards to LLVM IR
    + `thread_local!` macro
      - has perf overhead due to lazy creation (this was fixed since then via `const {}` syntax)
      - uses `#[thread_local]` internally
  * Contains good example of custom `build.rs` to link C part to Rust program
  * C version is 2x faster:
    + in C memory accesses moved out of loop
    + in Rust init checks prevent this
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/j4iy50/blog_post_fast_thread_locals_in_rust/)
- TLS implementation: https://github.com/rust-lang/rust/blob/master/library/std/src/thread/local.rs
  * Assignee: yugr
  * Status: DONE (75m)
  * `thread_local!` based on `#[thread_local]` internally
  * Runtime checks for non-trivial init or destructor
  * Can be implemented via native LLVM support (if available) or OS
  * Remaining info added to [feature](../features/cons/tls)
- Request for prioritization: fast thread locals: https://internals.rust-lang.org/t/request-for-prioritization-fast-thread-locals/13982
  * Assignee: yugr
  * Status: DONE (5m)
  * Two things:
    + do not pay for runtime check for vars w/o destructor (already done)
    + change default TLS model (already available)
  * Nothing was decided
  * Other materials: no links
- Tracking issue for thread-local stabilization: https://github.com/rust-lang/rust/issues/29594
  * Assignee: yugr
  * Status: DONE (10m)
  * Issue about stabilizing `#[thread_local]`
  * In general there does not seem to be much interest across maintainers
  * More materials: no links
- Fast thread locals: TLS model: https://internals.rust-lang.org/t/fast-thread-locals-tls-model/17032
  * Assignee: yugr
  * Status: DONE (5m)
  * Just some random discussion of `-Z tls-model` without any insights or conclusions

# Stdlib

- stdin and stdout performance considerations are not documented: https://github.com/rust-lang/rust/issues/106133
  * Assignee: yugr
  * Status: DONE (20m)
  * OP was interested in locking but others also mentioned
    + buffering
    + unnecessary allocations in `BufRead`
  * More materials:
    + added relevant links
- io::Stdout should use block bufferring when appropriate: https://github.com/rust-lang/rust/issues/60673
  * Assignee: yugr
  * Status: DONE (30m)
  * Issue created by BurntSushi
  * Problem: Rust's non-interactive stdout is much slower than Python
  * Root cause: Rust line-buffers stdout both for interactive and non-interactive output whereas Python/Glibc block-buffer for non-interactive
  * Solution:
    + PR to change default behavior [exists](https://github.com/rust-lang/rust/pull/60904) but was abandoned
    + More broad [PR](https://github.com/rust-lang/rust/pull/78515) which
      - adds API to control buffering and enable it for Stdout
      - committee requested large refactor and PR was abandoned
    + Use `grep_cli` crate instead of stdlib
  * More materials:
    + [Fix in Voila](https://github.com/Alonely0/Voila/issues/2)
    + [Fix in inferno](https://github.com/jonhoo/inferno/issues/193)
    + [URLO report](https://users.rust-lang.org/t/reading-and-writing-file-speed-problems/34498)
- RFC 1884: Sort unstable: https://github.com/rust-lang/rfcs/blob/master/text/1884-unstable-sort.md
  * Assignee: yugr
  * Status: DONE (15m)
  * RFC proposes to add unstable sort API to stdlib because
    + it can be efficiently implemented without allocation
    + can be 1.5x faster
  * `slice::sort_unstable` has been merged
  * More materials:
    + [Original issue](https://github.com/rust-lang/rfcs/issues/790)
    + [PR](https://github.com/rust-lang/rfcs/pull/1884)
- Extend io::BufRead to read multiple lines at once: https://internals.rust-lang.org/t/extend-io-bufread-to-read-multiple-lines-at-once/10196
  * Assignee: yugr
  * Status: DONE (20m)
  * OP complains that default Rust BufRead method `lines` is returning `String`'s:
    + cost of allocation
    + cost of UTF-8 verification
  * More materials:
    + no new links
- Why using read_lines iterator is much slower than using read_line? https://users.rust-lang.org/t/why-using-the-read-lines-iterator-is-much-slower-than-using-read-line/92815
  * Assignee: yugr
  * Status: DONE (15m)
  * Problem: `BufRead::read_line` is much faster than `BufRead::lines`
  * Root cause: `lines()` allocate every returned element
  * Solution: use `read_line`, update docs to mention it
  * More materials:
    + no new links
- My gripes with BufReader and BufWriter: https://users.rust-lang.org/t/my-gripes-with-bufreader-and-bufwriter/108557
  * Assignee: yugr
  * Status: DONE (5m)
  * OP suggests to make buffering (`BufReader`, `BufWriter`) default
  * Comments are that Rust's policy is to avoid leaky abstractions
    + buffers are leaky because they do not improve perf in all cases (e.g. due to additional copies from internal to user's buffer)
  * More materials:
    + no relevant links
- How to do Fast File IO: https://users.rust-lang.org/t/how-to-do-fast-file-io/8278
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: `BufReader`-based IO was slower than unbuffered
  * Root cause: not identified because OP didn't present his code
  * In general `BufReader` should never slow down the code
- BetterBufRead: Faster Reads in Rust: https://graphallthethings.com/posts/better-buf-read
  * Assignee: yugr
  * Status: DONE (15m)
  * OP implements alternative `BufRead`-like interface:
    + allow user to request arbitrary number of bytes
    + direct access to underlying buffer to avoid zero-copy
  * More materials:
    + no relevant links in blog
- Read::bytes() is a performance trap: https://github.com/rust-lang/rust/issues/28073 (2015)
  * Assignee: yugr
  * Status: DONE (5m)
  * efriedman reports 20x improvement when using `BufReader` (implying that it should be the default ?)
  * Docs updated to recommend using `BufRead` on top of `Read`
  * More materials:
    + no new links
- Performance reading file: https://users.rust-lang.org/t/performance-reading-file-parse-from-io-read-vs-from-u8/91948
  * Assignee: yugr
  * Status: DONE (10m)
  * OP wonders at perf different between `BufReader` and read-file-at-once approaches
  * No clear conclusions or advices in follow-up discussion
  * More materials:
    + added relevant link
- Is it possible to parse the file line by line without doing an allocation per line: https://users.rust-lang.org/t/is-it-possible-to-parse-the-file-line-by-line-without-doing-an-allocation-per-line/68639
  * Assignee: yugr
  * Status: DONE (5m)
  * OP wonders why `lines()` return `String`'s instead of `&str`
  * Instructed to use `read_line()` for such interface
  * More materials:
    + no new links
- Parsing 20MB file using from_reader is slow: https://github.com/serde-rs/json/issues/160#issuecomment-349943856
  * Assignee: yugr
  * Status: DONE (20m)
  * Problem: JSON deserialization is very slow
  * Root cause: lack of buffering
  * Solution: `BufReader` is still slow (2x slower than Python) so read-at-once (`from_slice`) is suggested
  * More materials:
    + no more relevant links

# Manual optimizations

- I sped up serde_json strings by 20%: https://purplesyringa.moe/blog/i-sped-up-serde-json-strings-by-20-percent/
  * Assignee: yugr
  * Status: DONE (1h)
  * Opts:
    + replace simple string parsing loop with `memchr` (library function, implemented in asm and heavy SIMD)
      - weird that compiler was unable to autovec the loop...
    + manual SWAR (SIMD-within-a-register) vectorization
    + manual LUTs for hex conversion
    + avoid redundant initialization for `encode_utf8`
  * More materials:
    + [Russian translation](https://habr.com/ru/articles/838404/)
    + [Reddit](https://www.reddit.com/r/rust/comments/1eyxspu/i_sped_up_serde_json_strings_by_20/)
    + [HN](https://news.ycombinator.com/item?id=41316807)
    + added more posts from blog to this file
- Improve an algorithm performance step by step: https://blog.mapotofu.org/blogs/rabitq-bench/
  * Assignee: yugr
  * Status: DONE (15m)
  * Contains several optimizations of some math code
  * Contains some useful info on profiling Rust apps
  * Starts with nalgebra-based implementation
  * Some interesting notes:
    + `if` faster than `f32::min` (?)
    + joining multiple iterators into single loop is faster
    + manual SIMD
    + strategic `#[inline]`'s may improve perf
    + no improvements with common techniques (CGU=1, LTO, PGO, BOLT, jemalloc)
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/1g4ums2/improve_an_algorithm_performance_step_by_step/)
    + [Russian translation](https://habr.com/ru/articles/852974/)
- Benchmarking and Optimization of Rust Libraries by Paul Mason: https://youtu.be/d2ZQ9-4ZJmQ?t=1001
  * Assignee: yugr
  * Status: DONE (15m)
  * Author optimizes small kernels using various techniques
  * Notable optimization suggestions:
    + use fixed size slices (`&[u32; 3]` instead of `&[u32]`) to allow LLVM to hoist bounds checks
    + avoid copies
  * More materials: no new links
- Rust newbie: Algorithm performance question: https://users.rust-lang.org/t/rust-newbie-algorithm-performance-question/47413
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: prime numbers computation is much slower than JS
  * Root cause: not defined but it seems that JS JIT replaces 64-bit `%` with 32-bit one
  * Solution: use 32-bit `%` in Rust code
  * More materials: no new links
- A performance problem compared with Julia: https://users.rust-lang.org/t/a-performance-problem-compared-with-julia/51871
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: nested Rust loop slower than equivalent Julia code
  * Root cause: lack of autovec
  * Solution: replace `..=` with `..`, `for_each` for inner loops, `-C target-cpu=native`
    + Julia is a JIT to optimizes for `native`
  * More materials: no new links
- Help comparing Rust vs Julia speed: https://users.rust-lang.org/t/help-comparing-rust-vs-julia-speed/54514
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: Rust loop slower than equivalent Julia code
  * Root cause: `powi` should be replaced with manual accumulation (not clear if LLVM can do this because Rust prohibits FP associativity changes)
  * Solution: code change
  * More materials: no new links
- Optimizing linear algebra code: https://users.rust-lang.org/t/optimizing-linear-algebra-code/39433
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: math code with complex indexing much slower in Rust than in C++/Julia
  * Root cause: bounds checks, `..=`
  * Solution: `get_unchecked`, replace `..=`, fast FP operations
  * Nice but sad quote:
> Rust bounds checking is the HPC killer.
  * More materials:
    + [Followup issue](https://github.com/rust-lang/rust/issues/45222) about `..=`
- Performance issue - High complexity code: https://users.rust-lang.org/t/performance-issue-high-complexity-code/40241
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: Rust code much slower than Java
  * Root cause: fix `! x == y` to `x != y`
  * More materials: no new links
- Optimization comparison: Vec vs array and for vs while: https://internals.rust-lang.org/t/optimization-comparison-vec-vs-array-and-for-vs-while/16410
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: Rust code with `Vec` slower than slice
  * Root cause: `Vec`'s are known to not optimize well
  * Solution: reslicing
  * More materials: no new links
- Performance optimization, and how to do it wrong: https://genna.win/blog/convolution-simd/
  * Assignee: yugr
  * Status: DONE (40m)
  * OP optimized 2D-convolution code
  * Code already implemented via intrinsics
  * Several interesting techniques:
    + poor-man's function specialization: replace
```
f(x, y, z);
```
      with
```
if (x, y) == (1, 1) {
  f(x, y, z);
} else {
  f(x, y, z);
}
```
    + split loop to aligned part and remainder to avoid `if`'s
      - no more than 1 branch in single fetch/decode block on most microarches => may limit FMA saturation
    + all funs must be annotated with `#[target_feature(enable = "avx2")]`
      - otherwise lack of inlining may prevent attribute propagation to callees
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/1j2iqhq/performance_optimization_and_how_to_do_it_wrong/)
    + [HN](https://news.ycombinator.com/item?id=43257460)
    + no more blogposts :(
- Code critique/review request: https://www.reddit.com/r/learnrust/comments/xllzqm/code_critiquereview_request/ (comments)
  * Assignee: yugr
  * Status: DONE (5m)
  * Request to review Rust code
  * Mostly code style comments except
    + use `Vec::with_capacity`
    + use `&[T]` instead of `&Vec<T>`
  * More materials: no new links
- When Zero Cost Abstractions Aren’t Zero Cost: https://blog.polybdenum.com/2021/08/09/when-zero-cost-abstractions-aren-t-zero-cost.html
  * Assignee: yugr
  * Status: DONE (20m)
  * Discusses how newtype pattern sometimes disables optimizations:
    + zero-init is faster w/o newtype due to stdlib specialization
    + spurious spills for newtype in some cases (no asm proof given and can't repro in current rustc)
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/p0ul6b/when_zero_cost_abstractions_arent_zero_cost/)
    + added other relevant links from blog
- Achieving warp speed with Rust: https://gist.github.com/jFransham/369a86eff00e5f280ed25121454acec1
  * Assignee: yugr
  * Status: DONE (10m)
  * Various high-level suggestions about optimization (caches, LTO, parallelization, `#[inline]`, etc.)
  * Low-level opts: `assert!` to void bounds checks
  * More materials: no new links
- From 48s to 5s - optimizing a 350 line raytracer in Rust: https://medium.com/@cfsamson/from-48s-to-5s-optimizing-a-350-line-pathtracer-in-rust-191ab4a1a412
  * Assignee: yugr
  * Status: DONE (5m)
  * Just few opt advices: use multithreading, iterators
  * More materials: no new links
- Using break in for loop takes even 100ms in release mode: https://www.reddit.com/r/rust/comments/1738kd7/using_break_in_for_loop_takes_even_100ms_in/
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: `break` in `for`-loop over container was taking a lot of time
  * Root cause: iteration was done using owning iterator so `break` had to drop all remaining elements
  * Solution: N/A
  * More materials: no new links
  * Overhead of consuming iterators
- 5x Slower than Go? Optimizing Rust Protobuf Decoding Performance: https://www.greptime.com/blogs/2024-04-09-rust-protobuf-performance
  * Assignee: yugr
  * Status: DONE (5m)
  * Performance of protobuf decoding is sifnificantly faster in Go
  * Eventually optimized via high-level transformations to match Go implementation:
    * reuse allocations
    * avoid using Strings
    * avoid refcounting via unsafe
  * More materials:
    + no new links
- Rust Performance Pitfalls: https://llogiq.github.io/2017/06/01/perf-pitfalls.html
  * Assignee: yugr
  * Status: DONE (20m)
  * Goes over common Rust perf caveats:
    + lack of `--release` or `-C target-cpu=native`
    + unbuffered IO
    + stream locking in `print!`
    + `Read::lines()` constructs new `String` for every line (this can be avoided)
    + overhead of `String` construction (to check invariants)
    + use iterators
    + avoid intermediate `collect()`'s in iterator chains
  * More materials:
    + [HN](https://news.ycombinator.com/item?id=14514591)
    + [Reddit](https://www.reddit.com/r/rust/comments/6ep1ao/blog_rust_performance_pitfalls/)
- Where should I start if I want to squeeze out as much performance as I can from my rust code? https://www.reddit.com/r/rust/comments/bb5lnj/where_should_i_start_if_i_want_to_squeeze_out_as/
  * Assignee: yugr
  * Status: DONE (5m)
  * OP asks for general methods for improving perf of Rust programs
  * General advices: iterators, `#[inline]`, `Vec::with_capacity`, avoid `clone()`
  * More materials: added links
- From 'Very Fast' to '~Fastest': Helping rust unleash compiler optimizations: https://blog.anubhab.me/tech/optimizing-diff-match-patch/
  * Assignee: yugr
  * Status: DONE (25m)
  * Good log of low-level optimizations in computation-heavy benchmark
  * Contains several low-level opts:
    + replace `* 2^n`, `/ 2^n`, `x % 2 != 0` with shifts
      - already optimized by modern rustc
    + replace 2 `Vec`'s with one + `split_at_mut`
    + replace `while` loop with `chunk_exact` iterators to foster autovec
      - didn't result in improvement/autovec
      - asm is better with iterators so it's unclear what went wrong
    + replace bounds checks with explicit index checks
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/1hsnnat/40_boost_in_text_diff_flow_just_by_facilitating/)
    + no more relevant posts in blog
- Example of loop rewrite for vectorization: https://github.com/dropbox/rust-brotli/blob/238c9c539b446d7d980e0a50795752c45dd3359e/src/enc/static_dict.rs lines 122 and 131
  * Assignee: yugr
  * Status: DONE (5m)
  * In both cases two string were resliced to common length
- Optimizing rav1d, an AV1 Decoder in Rust: https://www.memorysafety.org/blog/rav1d-performance-optimization/
  * Assignee: yugr
  * Status: DONE (70m)
  * Porting done in 2 steps:
    + c2rust conversion of existing dav1d codec (implemented in C)
    + rewrite c2rust output to idiomatic Rust (remove unsafe, etc.)
  * c2rust code had 4% perf loss
    + c2rust compiles C indexing to unchecked Rust indexing
    + tried to verify reasons for perf loss via compiler patching:
      - bounds checks - 1%
      - wrapping signed overflow - no influence
  * Safe code initially had 11% overhead which was reduced to 6%
  * Main perf issue was bounds checking
    + iterators were too simple for complex decoder loops
    + used reslicing and `assert_unchecked` to inform compiler about valid indexing
    + in final (idiomatic) code bounds checking resulted in "small" (1%?) perf loss (verified using compiler patch)
  * Other optimizations:
    + move error checking code to `#[inline(never)]` helpers (improves inlining of hot code and cache utilization)
    + avoid redundant initialization via `MaybeUninit`
  * Remaining problems:
    + Rust has overall higher stack usage (most likely due to panics)
    + some conditional assignments are implemented via branches instead of `csel` (for unclear reasons)
    + a lot of manually written asm; maybe it could be replaced with Rust SIMD? Codec people share different opinions in comments.
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/1fdzu7z/optimizing_rav1d_an_av1_decoder_in_rust/)
    + added more mats
- Porting C to Rust for a Fast and Safe AV1 Media Decoder: https://www.memorysafety.org/blog/porting-c-to-rust-for-av1/
  * Assignee: yugr
  * Status: DONE (15m)
  * Predecessor to previous post
  * Explains overall approach (c2rust, then rewrite to idiomatic Rust)
  * In general no info on perf optimizations
  * Explains how shared parallel state was changed for Rust
  * More materials:
    + [Russian translation](https://habr.com/ru/companies/ruvds/articles/842970)
    + [Reddit](https://www.reddit.com/r/rust/comments/1fcxxg5/porting_c_to_rust_for_a_fast_and_safe_av1_media/)
    + [HN](https://news.ycombinator.com/item?id=41493568)
- Huge performance gap in simple loop. Explanations? https://www.reddit.com/r/rust/comments/11f00kc/huge_performance_gap_in_simple_loop_explanations/
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: a loop much faster in C
  * Root cause: not defined (many people can't repro + benchmarks changed several times)
  * Solution: `chunk_exact`/`array_chunks`
  * More materials: no new links
- Rust: A better C++ than C++: Safety and performance: https://www.thecodedmessage.com/rust-c-book/safety.html
  * Assignee: yugr
  * Status: DONE (5m)
  * A more philosophical post about safe vs unsafe operations in Rust vs C++
  * No relevant info
  * More materials: no new links
- The Humble For Loop in Rust: https://blog.startifact.com/posts/humble-for-loop-rust/
  * Assignee: yugr
  * Status: DONE (5m)
  * Discussion of iterator capabilities, unrelated to performance
  * No relevant info
  * More materials: no perf-relevant posts in blog
- Why can deriving Copy pessimize performance by 60%? https://www.reddit.com/r/rust/comments/1h8dj64/why_can_deriving_copy_pessimize_performance_by_60/
  * Assignee: yugr
  * Status: DONE (10m)
  * [Known issue](https://github.com/memorysafety/rav1d/issues/1332) with `Copy` traits
  * Most likely will be fixed soon so no need to investigate/mention in slides
  * More materials: no new links
- Porting EBU R128 audio loudness analysis from C to Rust: https://coaxion.net/blog/2020/09/porting-ebu-r128-audio-loudness-analysis-from-c-to-rust-porting-details/
  * Assignee: yugr
  * Status: DONE (10m)
  * Another approach to porting (instead of `c2rust`): rewrite one function at a time
  * Just outlines some porting hints (binding, iterators, data structures, etc.)
  * No perf-relevant info
  * More materials:
    + Sadly part 3 (about optimizations) was not written
    + No more perf-relevant posts
- Pursuit of Performance on Building a JavaScript Compiler: https://oxc.rs/docs/learn/performance.html
  * Assignee: yugr
  * Status: DONE (10m)
  * Various high-level optimization techniques: string interning, string inlining, copy-on-write, SIMD
  * Good links about IO performance
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/1fuj0qg/rust_performance_tricks_from_a_javascript_compiler/)
    + added link on IO perf
- Cheap tricks for high-performance Rust: https://deterministic.space/high-performance-rust.html
  * Assignee: yugr
  * Status: DONE (5m)
  * Just general stuff: LTO, PGO, CGU, target-cpu=native, panic=abort, allocators
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/fdbszu/cheap_tricks_for_highperformance_rust/)
    + [Reddit](https://www.reddit.com/r/rust/comments/he8zky/cheap_tricks_for_highperformance_rust/)
    + no new links
- On Maximizing Your Rust Code's Performance: https://jbecker.dev/research/on-writing-performant-rust
  * Assignee: yugr
  * Status: DONE (5m)
  * Various high-level suggestions: right data structs, parallelization, algorithms
  * Rust-specific suggestions: `with_capacity`, reuse `Vec`'s, avoid intermediate `collect`'s, LTO, allocators, CGUs, `target-cpu=native`, `panic=abort`
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/14y2kej/maximizing_your_rust_codes_performance/)
    + no new links
- How copying an int made my code 11 times faster: https://blog.polybdenum.com/2017/02/19/how-copying-an-int-made-my-code-11-times-faster.html
  * Assignee: yugr
  * Status: DONE (30m)
  * Article is old but the issue still reproduces on trunk rustc
  * Passing local variable to `println!` macro implicitly borrows it (i.e. applies `&`, regardless of `Copy`)
  * After that LLVM fails to realize that the variable remains constant
  * Can be solved via
    + resetting variable after `println!`
    + using `{var}` (or `var + 0`, or `var.clone()`) when calling `println!`
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/5uvwur/how_copying_an_int_made_my_code_11_times_faster/)
    + [HN](https://news.ycombinator.com/item?id=13682929)
    + no new links
- Acheiving warp speed with Rust: http://troubles.md/posts/rust-optimization/
  * Assignee: yugr
  * Status: DONE (5m)
  * A bunch of generic advices (better cache utilization, etc.)
  * Only Rust-specific advice is to `assert!` to avoid bounds checks
  * More materials:
    + no new links
- Rust faster! https://llogiq.github.io/2015/10/03/fast.html
  * Assignee: yugr
  * Status: DONE (15m)
  * Analysis of benchmarks from Benchmarks Game:
    + fasta: cache results for each RNG output and some manual string printing opt
    + spectralnorm: manual vectorization via tuple structs
    + k_nucleotide: replace linked-list hash map with open addressing, replace `lines()` with `read_until()`, replace match-based encoding with byte manipulation
    + thread_ring: improve synchronization between threads
- Опыт переноса cpu-bound задач дата-аналитики с Python на Rust: https://www.youtube.com/watch?v=7vE6T5UX2Hc
  * Assignee: yugr
  * Status: DONE (30m)
  * Compares 3 data analytics tasks on Python vs Rust (comb. optimization, linear programming, linear regression)
  * Development costs ~5x
  * Speed up via parallelism (+15%, don't forget to use `-C target-cpu=... -C target-feature=...`):
    + threads:
      * author suggests to use Rayon (a work-stealing thread pool)
    + SIMD:
      * autovec does not not work for floats
      * explicit intrinsics from std::arch are unsafe and target-specific
      * author recommends safe cross-platform std::SIMD
    + ILP:
      * iterator_ilp crate
  * Speed up via PGO (+6%)

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
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: exceptions are very slow in mulithreaded programs
  * Root cause: stack unwinding is done in global critical section
  * Solution: alternative exception implementations or no exceptions at all
  * More materials: no relevant links
- Panics in rust consuming some extra resources. Can we disable it? https://www.reddit.com/r/rust/comments/12qhynj/panics_in_rust_consuming_some_extra_resources_can/
  * Assignee: yugr
  * Status: DONE (10m)
  * OP wonders whether he can disable safety checks to avoid overheads
  * He is educated that safety is whole point of Rust and is given alternative solutions:
    + `assert`'s
    + unsafe
- RFC 1513: Less unwinding: https://github.com/rust-lang/rfcs/blob/master/text/1513-less-unwinding.md
  * Assignee: yugr
  * Status: DONE (5m)
  * This is a proposal to add `panic=abort`
  * More materials: no new links
- Is Rust leaving performance on the table by eliminating exceptions? https://www.reddit.com/r/rust/comments/k5wk7r/is_rust_leaving_performance_on_the_table_by/
  * Assignee: yugr
  * Status: DONE (30m)
  * General discussion of exceptions (panics) vs. error codes (`Option` or `Result`)
  * Point is that error codes hurt I$ and BTB and prevent optimizations, whereas exceptions do not
  * On the other hand exceptions call blackbox personality functions which hurt optimizer's abilities
  * A very important comment: Rust marks `Some()` and `Ok()` branches as likely
  * Other materials:
    + [video](https://youtu.be/NH1Tta7purM?t=1152)
    + No new links
- How to Panic in Rust: https://www.ralfj.de/blog/2019/11/25/how-to-panic-in-rust.html
  * Assignee: yugr
  * Status: DONE (5m)
  * Describes how panics are handled in stdlib, unrelated to performance
  * More materials:
    + [IRLO](https://internals.rust-lang.org/t/how-to-panic-in-rust/11368)
    + Another post on panic internals: https://github.com/rust-lang/rustc-dev-guide/pull/521
    + no more relevant posts in blog
- Сompiler can't remove panic locations if they are not used in panic handler: https://github.com/rust-lang/rust/issues/129330
  * Assignee: yugr
  * Status: DONE (5m)
  * Just a random bug in compiler but it mentions `panic_immediate_abort` which gets cheapest possible panics
  * More materials: none
- RFC: Abort by default: https://github.com/rust-lang/rfcs/pull/1759
  * Assignee: yugr
  * Status: DONE (15m)
  * Proposal to make `panic=abort` the default choice
  * Rejected because that will be a disrupting change
  * More materials: no new links
- Abort by default v2: https://github.com/rust-lang/rfcs/pull/1765
  * Assignee: yugr
  * Status: DONE (15m)
  * Proposal suggested to make panic=abort default for new Cargo projects
  * Rejected for lack of benchmarks and clear arguments against panicking
  * More materials: no new links
- Pros and cons of catch_unwind: https://users.rust-lang.org/t/pros-and-cons-of-std-catch-unwind/65417
  * Assignee: yugr
  * Status: DONE (10m)
  * Just general discussion of when to use panics (invariant violations, programmer errors) and error handling (logical errors, env errors)
  * More materials: no new links
- You might want to use panics for error handling: https://purplesyringa.moe/blog/you-might-want-to-use-panics-for-error-handling/
  * Assignee: yugr
  * Status: DONE (15m)
  * Introduces `iex` - a drop-in solution which replaces distributed error handling (`Result`, `?`) with exceptions (panics)
  * Show that happy path for real-world code may speed up a lot (5-20%)
  * More materials:
    + no new links
- Bringing faster exceptions to Rust: https://purplesyringa.moe/blog/bringing-faster-exceptions-to-rust/
  * Assignee: yugr
  * Status: DONE (90m)
  * Continuation of previous article
  * Contains highly-technical analysis of implementation of panics in Rust and how it can be sped up
  * New exceptions are 2-4x faster
  * Some interesting takes in comments:
    + a lot of hate/downvotes from fans of traditional error handling
    + `Result`'s are currently very inefficient due to enum calling convention
    + whether exceptions inhibit other optimizations (no clear and proved conclusion)
    + Alisa says she has draft impl of exceptions not based on exception tables which are 100x (!) faster
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/1gl050z/bringing_faster_exceptions_to_rust/)
    + [HN](https://news.ycombinator.com/item?id=42072750)
    + [GitHub](https://github.com/iex-rs/lithium)
- The Error Model: https://joeduffyblog.com/2016/02/07/the-error-model/
  * Assignee: yugr
  * Status: DONE (10m)
  * (Only checked performance-related parts)
  * A general discussion of error handling in new language
  * Just briefly touches on performance issues:
    + error codes may be slower due to I$/TLB pressure, additional code (cmp + branch), confusing optimizer
    + exceptions are implemented in inefficient way
  * More materials:
    + no new links
- Efficiently bubbling Results: https://internals.rust-lang.org/t/efficiently-bubbling-results/20120
  * Assignee: yugr
  * Status: DONE (15m)
  * OP notes that passing of `Result`'s is done on stack which makes work with them very inefficient
  * Propose to pass separate pointers to arms but commenters point out problems with aliasing
  * More materials:
    + no new links
- C++ Exceptions for Smaller Firmware: https://www.youtube.com/watch?v=bY2FlayomlE&t=2671s
  * Assignee: yugr
  * Status: DONE (40m)
  * Overview of C++ Itanium ABI exceptions implementation
  * Discusses centralized vs distributed error handling (i.e. exceptions vs retcodes) from code size POV
  * In comments also [mentions](https://www.reddit.com/r/cpp/comments/1ejpgbe/comment/lhqecdg/) ~20% performance improvement
  * More materials:
    + [Reddit](https://www.reddit.com/r/cpp/comments/1fkvj00/c_exceptions_for_smaller_firmware_khalil_estell/)
    + [Reddit](https://www.reddit.com/r/cpp/comments/1ejpgbe/c_exceptions_reduce_firmware_code_size_khalil/)
- Is it okay to let some errors panic? https://www.reddit.com/r/rust/comments/1ad7xyn/is_it_okay_to_let_some_errors_panic/
  * Assignee: yugr
  * Status: DONE (10m)
  * OP wonders if it's ok to use exceptions for rare errors
  * Most commenters (e.g. [burntsushi](https://burntsushi.net/unwrap/#why-are-panics-so-great)
    and [algesten](https://github.com/algesten/str0m#panics-errors-and-unwraps))
    exceptions to be appropriate only for bugs (violation of invariants)
  * More materials:
    + added links
- Optimisation of Exceptions and Repeated Return of Error Types: https://www.reddit.com/r/rust/comments/13fqdcs/optimisation_of_exceptions_and_repeated_return_of/
  * Assignee: yugr
  * Status: DONE (10m)
  * OP wonders whether exceptions are more beneficial than error codes
  * Various opinions (inhibit opts, overhead too large, etc.) but no clear benchmarks or evidence
  * `Result` calling convention is inefficient
  * More materials:
    + no new links
- In realistic scenarios, exceptions are a much faster way to handle rare errors than error codes: https://web.archive.org/web/20230605115838/https://lordsoftech.com/programming/error-codes-are-far-slower-than-exceptions/
  * Assignee: yugr
  * Status: DONE (40m)
  * OP measures typical gamedev scenarios for overhead of branches (5% on average)
  * Criteria for using exceptions for error handling: error frequency >= 0.01%
  * Commenters mention that
    + exceptions block optimizations: inlining is harder due to code bloat and `throw` is a blackbox
    + likely directives not used (but most code does not use them)
  * More materials:
    + [Reddit](https://www.reddit.com/r/cpp/comments/k08g89/in_realistic_scenarios_exceptions_are_a_much/)
    + added links from [this comment](https://www.reddit.com/r/cpp/comments/k08g89/comment/gektp1k/)
    + site has been wiped out so can't survey
- Measuring execution performance of C++ exceptions vs error codes: https://nibblestew.blogspot.com/2017/01/measuring-execution-performance-of-c.html
  * Assignee: yugr
  * Status: DONE (10m)
  * Compares exceptions vs error codes performance on synthetic benchmark
  * Exceptions are faster as stack depths increase and error rates decrease
  * More materials:
    + no new links
- P1886R0: Error speed benchmarking: https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1886r0.html
  * Assignee: yugr
  * Status: DONE (15m)
  * Another comparison of exceptions vs error codes
  * Results match other posts: exceptions are 5-10% faster on happy path, 100x slower on sad path
    + For some reason exceptions are slower in MSVC 32-bit
  * More materials:
    + [P1640R1: Error size benchmarking: Redux](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1640r1.html)
    + no new links

# Uninit

- Uninitialized Memory: Unsafe Rust is Too Hard: https://lucumr.pocoo.org/2022/1/30/unsafe-rust/
  * Assignee: yugr
  * Status: DONE (30m)
  * An example of how to uninitialize a struct with non-trivial fields
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/sg6pp5/uninitialized_memory_unsafe_rust_is_too_hard/)
    + [HN](https://news.ycombinator.com/item?id=30135758)
    + no more materials in blog
- Fast vector initialization without default value: https://users.rust-lang.org/t/fast-vector-initialization-without-default-value/34857
  * Assignee: yugr
  * Status: DONE (10m)
  * Problem: OP claimed that he had a slowdown due to unnecessary vector initialization
  * Root cause: not clear because kernel code wasn't provided
  * Solution: use `vec![MaybeUninit::uninit(); n]`, `Vec::set_len`, `Vec::with_capacity`
  * More materials: no relevant suggested links
- Is there a way to express buffer need not be zeroed? https://users.rust-lang.org/t/is-there-a-way-to-express-a-buffer-need-not-be-zeroed/65785
  * Assignee: yugr
  * Status: DONE (5m)
  * OP wondered how to avoid initializing buffer with values which won't be read
  * Solution: `MaybeUninit<[u8; 1024]>`
  * More materials: no new links
- Idiomatic way of working with uninitialized dynamic memory: https://users.rust-lang.org/t/idiomatic-way-of-working-with-uninitialized-dynamic-memory/50642
  * Assignee: yugr
  * Status: DONE (10m)
  * OP wondered about recommended way to work with uninitialized vector
  * Solution: `Vec::with_capacity` + `Vec::spare_capacity_mut` + `Vec::set_len`
  * More materials: no new links
- Nomicon: Unchecked Uninitialized Memory: https://doc.rust-lang.org/nomicon/unchecked-uninit.html
  * Assignee: yugr
  * Status: DONE (5m)
  * Gives some more examples of `MaybeUninit` but nothing new overall
  * More materials: no new links
- RFC 2930: Reading into uninitialized buffers: https://github.com/rust-lang/rfcs/pull/2930
  * Assignee: yugr
  * Status: DONE (40m)
  * Proposes new API in `Read` trait to support uninitialized buffers
  * Cites some performance numbers
  * The feature has been merged and available in nightly
  * More materials:
    + [Tracking issue](https://github.com/rust-lang/rust/issues/78485)
    + [Discussion in IRLO](https://internals.rust-lang.org/t/readbuf-as-part-of-rust-edition-2021/14256)
    + [Read::initializer (old solution)](https://github.com/rust-lang/rust/pull/42002)
    + [Implementation](https://github.com/rust-lang/rust/pull/81156)
- Uninit Read/Write: https://blog.yoshuawuyts.com/uninit-read-write/
  * Assignee: yugr
  * Status: DONE (10m)
  * An overview of `read_buf` and `spare_capacity_mut`
  * Discusses some more ideas on hwo uninitialized buffers could be used
  * More materials: no new links or perf-relevant articles in blog
- "What The Hardware Does" is not What Your Program Does: Uninitialized Memory: https://www.ralfj.de/blog/2019/07/14/uninit.html
  * Assignee: yugr
  * Status: DONE (5m)
  * Discusses the concept of uninitialized memory in high-level languages and how it's different from hardware
    + not just random bytes
    + e.g. `x + 0 != x` for uninitialized x
  * More materials: no new perf-relevant links
- Rust's worst feature: https://mina86.com/2025/rusts-worst-feature/
  * Assignee: yugr
  * Status: DONE (15m)
  * Critique of `BorrowedBuf`:
    + optionality: many `Read` instances do not implement it
    + not generic: provides `[u8]` for underlying contents
    + hard to use
  * Alternative: concept of "freezing" for `MaybeUninit` values
    + but this may cause info leaks
    + also need to write every page due to potential `MADV_FREE`
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/1iad0lk/rusts_worst_feature_spoiler_its_borrowedbuf_i/)
- Rustonomicon: Working With Uninitialized Memory: https://doc.rust-lang.org/nomicon/uninitialized.html
  * Status: backlog

# Unsafe

- Being Fair about Memory Safety and Performance: https://www.thecodedmessage.com/posts/unsafe/
  * Assignee: yugr
  * Status: DONE (5m)
  * A rather long artile which boils down to
    + Rust indexing being equivalent of `at` (not `operator []`) in C++
    + `unsafe` (e.g. `get_unchecked`) being ok because it's usage is limited
  * Basically Rust makes safer defaults in hope that this is what's needed most of them time
  * More materials:
    + no more relevant links in blog
- Implementing a VM: how unsafe should I go? https://www.reddit.com/r/rust/comments/n8yy7z/implementing_a_vm_how_unsafe_should_i_go/
  * Assignee: yugr
  * Status: DONE (5m)
  * OP wonders how to avoid large amount of unsafe code needed for GC and other low-level VM stuff
  * No definite answers, some people arguing that unsafe is inevitable and some that it should only be needed in very few places
  * More materials:
    + no new links
- Good example of high performance Rust project without unsafe code? https://www.reddit.com/r/rust/comments/we91es/good_example_of_high_performance_rust_project/
  * Assignee: yugr
  * Status: DONE (20m)
  * OP asked whether some high-perf crates are written w/o unsafe and whether it's possible in general
  * Useful comments:
    + SIMD is unsafe but mandatory for any HPC algo
    + unsafe code can typically be hidden behind safe abstractions
      - e.g. many parts of stdlib are unsafe
    + small amount of unsafe is typically needed
    + unsafe if hard to get right (too many cases for UB e.g. create reference to uninit data to initialize it)
  * More materials:
    + added links
- How do you all think about the `unsafe` vs zero-cost trade off? https://www.reddit.com/r/rust/comments/f5wgsn/how_do_you_all_think_about_the_unsafe_vs_zerocost/
  * Assignee: yugr
  * Status: DONE (20m)
  * OP wonders what are the criteria for using unsafe
  * No general guidance except that unsafe is indeed sometimes needed for performance
  * More materials:
    + no links
- Unsafe Rust is Harder Than C: https://www.reddit.com/r/rust/comments/1gbqy6c/unsafe_rust_is_harder_than_c/
  * Status: backlog
  * Russian translation: https://habr.com/ru/companies/ruvds/articles/858246/
  * More materials:
    + [HN](https://news.ycombinator.com/item?id=41944121)
- Comments for "Story-time: C++, bounds checking, performance, and compilers": https://www.reddit.com/r/cpp/comments/1gtos7w/storytime_c_bounds_checking_performance_and/
  * Assignee: yugr
  * Status: DONE (90m)
  * General comments:
    + Lots of language safety discussions
    + Many claim that Rust unsafe is harder than C++
    + Some claim that unsafe is (often, sometimes ?) mandatory for high-performance code
  * More materials:
    + added links
- Unsafe Rust: How and when (not) to use it: https://blog.logrocket.com/unsafe-rust-how-and-when-not-to-use-it
  * Assignee: yugr
  * Status: DONE (15m)
  * Debunks some myths about unsafe:
    + Less than 1% of code on crates.io is unsafe
    + Unsafe does not turn off borrow checker
    + Unsafe is not always faster because compiler has less info
  * Also provide examples on dealing with some unsafe usecases:
    + uninit memory
    + intrinsics
    + inline asm
    + FFI
  * More materials:
    + added links
    + no more relevant posts in blog in past 3 years
- Unsafe Rust is not C: https://www.youtube.com/watch?v=DG-VLezRkYQ
  * Assignee: yugr
  * Status: DONE (15m)
  * Some examples of why unsafe Rust is hard (need to ensure that reference rules are still not violated) and how this allows compiler to optimize code
  * More materials:
    + no new links
- Learn Rust the Dangerous Way: https://cliffle.com/p/dangerust/
  * Status: backlog
- Unsafe in Rust: Syntactic Patterns: https://cs.stanford.edu/~aozdemir/blog/unsafe-rust-syntax/
  * Status: backlog
- Stdlib: optimization of reverse: https://github.com/rust-lang/rust/commit/71f5cfb21f3fd2f1740bced061c66ff112fec259
  * Status: backlog

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

# Codegen unit

- Huge performance gap between lto="fat",cgu=1 and default release profile https://github.com/rust-lang/rust/issues/93321
  * Assignee: zakhar
  * Status: DONE (15m)
  * Problem: 4x perf difference between base compile flags and lto="fat", cgu=1
  * Root cause: Different inlining with different number of CGUs
  * Solution: Careful addition of extra `[#inline]` tags and/or using fat LTO.
    Possible future "become" keyword (tail call optimization) is stated as a fix from the issue creator.
  * More materials:
    + Some possibly interesting benchmark https://github.com/ggwpez/substrate-bench/tree/master/reports/01-first-findings
    + CGUs may cause unpredictable behaviour when comparing pointers https://github.com/rust-lang/rust/issues/46139
    + TCO in Rust blogpost https://seanchen1991.github.io/posts/tco-story/
    + Explicit Tail Call RFC https://github.com/rust-lang/rfcs/pull/3407
- CGUs may cause unpredictable behaviour when comparing pointers https://github.com/rust-lang/rust/issues/46139
  * Assignee: zakhar
  * Status: DONE (15m)
  * Problem: Comparison of vtable pointers can be true or false depending of number of CGU in build configuration
  * Reasons: Seems that uniqueness of vtables is not guaranteed, so strange behaviour is expected
             vtables get duplicated between CGUs and are sometimes different between different CGUs (possibly a bug)
  * Solution: Discussion suggests using `linkonce_odr` in LLVM IR as a partial solution.
- Compiler flag's impact on benchmarks: https://github.com/ggwpez/substrate-bench/tree/master/reports/01-first-findings
  * Assignee: yugr
  * Status: Wontfix (5m)
  * Some possibly interesting benchmark (low CGU and fat LTO not always better) ?
  * Unfortunately I (yugr) couldn't make sense of graphs in this post
- Performance regressions of compiled code over the last year: https://github.com/rust-lang/rust/issues/47561
  * Assignee: yugr
  * Status: DONE (10m)
  * An old regression caused insufficient inlining (perf can be restored with inline threshold and CGU=1)
  * Nothing new here
- 2x benchmark loss in rayon-hash from multiple codegen-units https://github.com/rust-lang/rust/issues/47665
  * Assignee: zakhar
  * Status: DONE (10m)
  * Problem: Using multiple CGUs reduces benchmark performance by half
  * Reason: Inlining is not performed across multiple CGUs
  * Solution: Use LTO or compile with one CGU (adding inline tag into stdlib isn't feasible for a user)
- rustc: Default 32 codegen units at O0: https://github.com/rust-lang/rust/pull/44853
  * Assignee: yugr
  * Status: Wontfix (0m)
  * This is about debug builds, not relevant for us
- 32 codegen units may not always be better at -O0: https://github.com/rust-lang/rust/issues/44941
  * Assignee: yugr
  * Status: DONE (5m)
  * Problem: compile time increases with CGU=16/32
  * Root cause: "Increasing the number of codegen units is not purely dividing the work, it's also increasing the total amount of work being done"
  * Solution: some fixes were done
  * More materials: added linked issue
- Back-end parallelism in the Rust compiler: https://nnethercote.github.io/2023/07/11/back-end-parallelism-in-the-rust-compiler.html
  * Assignee: zakhar
  * Status: DONE (30m)
  * Problem: Nethercote's investigation on how to improve compilation times using CGUs. He also confirms that multiple CGUs with thin LTO is still worse than using one CGU.
  * More materials:
    + [Reddit](https://news.ycombinator.com/item?id=36678457)
    + [HN](https://www.reddit.com/r/rust/comments/14wcezs/backend_parallelism_in_the_rust_compiler/)
- Let’s talk about parallel codegen https://internals.rust-lang.org/t/lets-talk-about-parallel-codegen/2759
  * Assignee: zakhar
  * Status: DONE (25m)
  * Problem: A prolonged discussion about default number of codegen units. Brings up a point about builds with multiple CGUs being non-deterministic. Contains some perf overhead measurements.
- codegen-units + ThinLTO is not as good as codegen-units=1: https://github.com/rust-lang/rust/issues/47745
  * Assignee: yugr
  * Status: DONE (5m)
  * General discussion that ThinLTO is not always better than CGU=1
  * No technical investigation
  * More materials: a lot of linked use-cases
- Adding --emit=asm speeds up generated code because of codegen units https://github.com/rust-lang/rust/issues/57235
  * Assignee: zakhar
  * Status: DONE (10m)
  * Problem: `--emit=asm` flag drastically improves small benchmark performance
  * Root cause: `--emit-asm` disables CGUs; with multiple codegen units compiler is unable to detect that loop does not do anything
  * Solution: Use cgu=1 for building (especially for small projects)
- Speeding up rustc by being lazy: https://davidlattimore.github.io/posts/2024/06/05/speeding-up-rustc-by-being-lazy.html
  * Assignee: yugr
  * Status: DONE (15m)
  * Explores various issues in rustc which slow down compile time or generate worse code:
    + monomorphization duplication (due to CGU=32 and separate compilation)
      - could be solved by various means: CGU=1, LTO, weak symbols, `-Z share-generics`, etc.
    + compiler produces dead code which is later dropped at link-time (due to `--gc-sections`)
      - could be solved by MIR-only rlibs
    + CGUs are too large
      - ideally per-function CGU (that's what Cranelift does)
  * Conclusion: could improve efficiency by deferring compilation to link time when all deps are known
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/1d9b36j/speeding_up_rustc_by_being_lazy/)
    + No relevant materials in blog
- Tracking issue for enabling multiple CGUs in release mode by default: https://github.com/rust-lang/rust/issues/45320
  * Assignee: yugr
  * Status: DONE (15m)
  * General perf data discussion of various combinations of ThinLTO, CGUs, etc. for various codebases
  * A common case is that CGUs distribute work very unevenly and compile time is totally dominated by single CGU
  * More materials: no relevant links

# TCO

- Explicit Tail Call RFC https://github.com/rust-lang/rfcs/pull/3407
  * Assignee: zakhar
  * Status: DONE (10m)
  * Problem: RFC for explicit tail calls. Still in development
- TCO in Rust blogpost https://seanchen1991.github.io/posts/tco-story/
  * Assignee: zakhar
  * Status: DONE (15m)
  * Problem: Rust does not have TCO
  * Solution: Some crates (tco, tramp) provide macros to optimize tail-calling functions.
    + These crates are not well-developed and are either in POC state or do not provide 'real' (constant memory usage) TCO

# Other

- Leaving Rust gamedev after 3 years: https://loglog.games/blog/leaving-rust-gamedev/ (also comments in https://news.ycombinator.com/item?id=40172033 and https://habr.com/ru/articles/813597/)
  * Status: backlog
- Why I hate Rust programming language? https://www.reddit.com/r/programming/comments/n9l68o/why_i_hate_rust_programming_language/ (comments)
  * Status: backlog
- Rust inadequate for text compression codecs? https://news.ycombinator.com/item?id=43295908
  * Status: backlog
- Rust: Not So Great For Codec Implementing: https://codecs.multimedia.cx/2017/07/rust-not-so-great-for-codec-implementing/
  * Assignee: zakhar
  * Status: DONE (80m)
  * Problem: Borrow-checker limitations, not enough allocation control, weak macro system
  * Solution: Wait until all the RFCs fixing these problems are implemented
  * More materials:
    + rust-brotli rewrite for vectorization example
    + Why you should, actually, rewrite some of it in Rust
    + Discussion about explicit SIMD in Rust
    + [Reddit](https://www.reddit.com/r/rust/comments/6qv2s5/rust_not_so_great_for_codec_implementing/)
- Why you should, actually, rewrite some of it in Rust: https://news.ycombinator.com/item?id=14753201
  * Status: backlog
-  Rust and Scientific/High-Performance Computing: https://www.reddit.com/r/rust/comments/smdl3m/rust_and_scientifichighperformance_computing/
  * Status: backlog

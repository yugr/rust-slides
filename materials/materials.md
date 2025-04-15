Materials have been collected according to [collection methodology](materials/method.md).

Note that section split below is rather crude and may do more harm than good.
Please refactor mercilessly if you think it makes sense.
On the other hand, once all materials are analyzed we won't care about this file.

- TODO(gh-2) add more interesting materials from
  * rejected opts: https://github.com/rust-lang/rust/issues?q=is%3Aissue%20state%3Aclosed%20reason%3Anot-planned%20label%3AI-slow
  * compiler RFCs: https://github.com/rust-lang/rust/issues?q=is%3Aissue%20label%3AT-compiler%20rfc
  * MIR opts: https://github.com/rust-lang/rust/issues?q=state%3Aopen%20label%3A%22A-mir-opt%22
- TODO(gh-8) add more interesting materials from
  * https://github.com/rust-lang/compiler-team
- TODO(gh-10) add more interesting materials from RFCs

# Coding guidelines

- Rustc development guide: https://rustc-dev-guide.rust-lang.org/
- Rust design patterns: https://softwarepatternslexicon.com/patterns-rust/
- Rust Performance Book (by Nethercote): https://nnethercote.github.io/perf-book/
  * pay attention to links at https://nnethercote.github.io/perf-book/bounds-checks.html
  * comments: https://www.reddit.com/r/rust/comments/jvmb8u/the_rust_performance_book/
  * additions: https://github.com/nnethercote/perf-book/issues
- Some general guidelines from Redox OS https://doc.redox-os.org/book/rusting-properly.html
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
  * More materials: no performance-related materials found in blog
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
- An Optimization That’s Impossible in Rust! https://tunglevo.com/note/an-optimization-thats-impossible-in-rust/
  * Translation: https://habr.com/ru/companies/beget/articles/842868/
  * Comments: https://www.reddit.com/r/rust/comments/1f87siw/an_optimization_thats_impossible_in_rust/
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
- Rust vs. C++: Fine-grained Performance: https://users.rust-lang.org/t/rust-vs-c-fine-grained-performance/4407
- A good performance comparision C and Rust: https://users.rust-lang.org/t/a-good-performance-comparision-c-and-rust/5901/7
- Rust-specific code optimisations vs other languages: https://users.rust-lang.org/t/rust-specific-code-optimisations-vs-other-languages/49663
- How to speed up this rust code? I’m measuring a 30% slowdown versus the C++ version: https://users.rust-lang.org/t/how-to-speed-up-this-rust-code-im-measuring-a-30-slowdown-versus-the-c-version/1488
- Goals and priorities for C++: https://internals.rust-lang.org/t/goals-and-priorities-for-c/12031/32 (some points on Rust perf features like lack of fast-math or move semantics)
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
  * Statis: DONE (30m)
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
- Is Rust faster than Fortran and C++? A case study with scientific applications: https://www.reddit.com/r/rust/comments/1jz504y/is_rust_faster_than_fortran_and_c_a_case_study/

# Expression templates

- Expression Templates in Rust? https://www.reddit.com/r/rust/comments/1f0hi5k/expression_templates_in_rust
  * Assignee: yugr
  * Status: in progress
- Expression templates in Eigen: https://eigen.tuxfamily.org/index.php?title=Expression_templates
  * Assignee: yugr
  * Status: in progress

# Overflow checks

- Why is Rust not able to optimize this? https://www.reddit.com/r/rust/comments/181tp1a/why_is_rust_not_able_to_optimize_this/ (signed overflow)
  * Assignee: yugr
  * Statis: DONE (20m)
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
    + a lot of comments on [Reddit](https://www.reddit.com/r/rust/comments/z92vid/measuring_how_much_rusts_bounds_checking_actually/), [Reddit](https://www.reddit.com/r/programming/comments/z9hjpk/how_much_does_rusts_bounds_checking_actually_cost/) and [HackerNews](https://news.ycombinator.com/item?id=33805419)
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
  * Highly technical, low priority
- Move semantics in C and Rust: https://radekvit.medium.com/move-semantics-in-c-and-rust-the-case-for-destructive-moves-d816891c354b
- Are rust moves of structs, copies or moves Zero Cost Abstractions: https://www.reddit.com/r/rust/comments/1ibjnka/are_rust_moves_of_structs_copies_or_moves_zero/

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
- New range types: https://github.com/rust-lang/rust/issues/123741
  * Be sure to analyze links
- Rust’s iterators are inefficient, and here’s what we can do about it: https://medium.com/@veedrac/rust-is-slow-and-i-am-the-cure-32facc0fdcb
  * Assignee: yugr
  * Status: in progress
  * More materials:
    + [Reddit](https://www.reddit.com/r/rust/comments/5ez38g/rusts_iterators_are_inefficient_and_heres_what_we/)
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
  * Status: in progress
- Why does iteration over an inclusive range generate longer assembly in Rust than in C++? https://stackoverflow.com/questions/70672533/why-does-iteration-over-an-inclusive-range-generate-longer-assembly-in-rust-than/70680224
  * Assignee: yugr
  * Status: in progress
- Zero-cost iterator abstractions...not so zero-cost? https://www.reddit.com/r/rust/comments/yaft60/zerocost_iterator_abstractionsnot_so_zerocost/
  * Assignee: yugr
  * Status: in progress

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
- Enable mutable noalias for LLVM >= 12 by nikic merged: https://www.reddit.com/r/rust/comments/maix26/enable_mutable_noalias_for_llvm_12_by_nikic_merged/

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
- Inspecting rustc LLVM optimization remarks using cargo-remark: https://kobzol.github.io/rust/cargo/2023/08/12/rust-llvm-optimization-remarks.html
  * need to run `cargo remark` on some real projects
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
- Should small Rust structs be passed by-copy or by-borrow? https://www.reddit.com/r/rust/comments/zzxz2e/should_small_rust_structs_be_passed_bycopy_or/

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
- Expression templates: https://en.wikipedia.org/wiki/Expression_templates
  * This is a foundation block of C++ linear algebra packages like Eigen
  * Rust does not support such idioms (and it's considered a big flaw)

# Stack probing

- probestack.rs: https://github.com/rust-lang/compiler-builtins/blob/master/compiler-builtins/src/probestack.rs
  * Check comments
- Is rust guaranteed to detect stack overflows? https://users.rust-lang.org/t/is-rust-guaranteed-to-detect-stack-overflows/52593
- Bringing Stack Clash Protection to Clang / X86: https://blog.llvm.org/posts/2021-01-05-stack-clash-protection/

# Manual optimizations

- Nethercote's posts: https://blog.mozilla.org/nnethercote/category/rust/
  * Nethercote is top industry expert, need to pay close attention to his posts
- Moar Nethercote's posts: https://nnethercote.github.io/
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
  * Reddit: https://www.reddit.com/r/rust/comments/6ep1ao/blog_rust_performance_pitfalls/
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
- Huge performance gap in simple loop. Explanations? https://www.reddit.com/r/rust/comments/11f00kc/huge_performance_gap_in_simple_loop_explanations/
- Memory-safe PNG decoders now vastly outperform C PNG libraries: https://www.reddit.com/r/programming/comments/1hak25t/memorysafe_png_decoders_now_vastly_outperform_c/
- Speeding up RGB to grayscale conversion in Rust: https://www.reddit.com/r/rust/comments/7rxrka/speeding_up_rgb_to_grayscale_conversion_in_rust/
- Rust performance help (convolution): https://users.rust-lang.org/t/rust-performance-help-convolution/44075
- Rust: A better C++ than C++: Safety and performance: https://www.thecodedmessage.com/rust-c-book/safety.html

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
- Panics in rust consuming some extra resources. Can we disable it? https://www.reddit.com/r/rust/comments/12qhynj/panics_in_rust_consuming_some_extra_resources_can/
- RFC 1513: Less unwinding: https://github.com/rust-lang/rfcs/blob/master/text/1513-less-unwinding.md

# Unsafe

- Being Fair about Memory Safety and Performance: https://www.thecodedmessage.com/posts/unsafe/
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
- Some possibly interesting benchmark (low cgu and fat lto not always better) https://github.com/ggwpez/substrate-bench/tree/master/reports/01-first-findings
- Performance regressions of compiled code over the last year https://github.com/rust-lang/rust/issues/47561
- 2x benchmark loss in rayon-hash from multiple codegen-units https://github.com/rust-lang/rust/issues/47665
    * Assignee: zakhar
    * Status: DONE (10m)
    * Problem: Using multiple CGUs reduces benchmark performance by half
    * Reason: Inlining is not performed across multiple CGUs
    * Solution: Use LTO or compile with one CGU (adding inline tag into stdlib isn't feasible for a user)
- rustc: Default 32 codegen units at O0 https://github.com/rust-lang/rust/pull/44853
    - 32 codegen units may not always be better at -O0 https://github.com/rust-lang/rust/issues/44941
- Back-end parallelism in the Rust compiler: https://nnethercote.github.io/2023/07/11/back-end-parallelism-in-the-rust-compiler.html
    - https://news.ycombinator.com/item?id=36678457
    - https://www.reddit.com/r/rust/comments/14wcezs/backend_parallelism_in_the_rust_compiler/
    * Assignee: zakhar
    * Status: DONE (30m)
    * Problem: Nethercote's investigation on how to improve compilation times using CGUs. He also confirms that multiple CGUs with thin LTO is still worse than using one CGU.
- Let’s talk about parallel codegen https://internals.rust-lang.org/t/lets-talk-about-parallel-codegen/2759
    * Assignee: zakhar
    * Status: DONE (25m)
    * Problem: A prolonged discussion about default number of codegen units. Brings up a point about builds with multiple CGUs being non-deterministic. Contains some perf overhead measurements.
- codegen-units + ThinLTO is not as good as codegen-units = 1 https://github.com/rust-lang/rust/issues/47745
- Adding --emit=asm speeds up generated code because of codegen units https://github.com/rust-lang/rust/issues/57235
    * Assignee: zakhar
    * Status: DONE (10m)
    * Problem: `--emit=asm` flag drastically improves small benchmark performance
    * Root cause: `--emit-asm` disables CGUs; with multiple codegen units compiler is unable to detect that loop does not do anything
    * Solution: Use cgu=1 for building (especially for small projects)
- Speeding up rustc by being lazy https://www.reddit.com/r/rust/comments/1d9b36j/speeding_up_rustc_by_being_lazy/

# Other

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
- Reddit comments to 'Rust: Not So Great For Codec Implementing': https://www.reddit.com/r/rust/comments/6qv2s5/rust_not_so_great_for_codec_implementing/
- Why you should, actually, rewrite some of it in Rust: https://news.ycombinator.com/item?id=14753201
- Rust должен умереть, МГУ сделал замеры: https://habr.com/ru/articles/598219/

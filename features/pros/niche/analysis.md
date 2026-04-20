# Administrivia

Assignee: zak

Parent task: gh-57

Effort: 2h

TODO:
  - fix all TODOs that are mentioned in feature's README

# Background

TODO:
  - why is this feature needed ?
    * example cases which are optimized by niche and struct reorg
    * benefits (better D$ utilization)
    * situation in C/C++
      + struct reorg opt in GCC and Clang (by Golovanevsky Olga)
      + e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
      + e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
      + mention comparison w/ `std::optional` ([tiny-optional](https://github.com/Sedeniono/tiny-optional?tab=readme-ov-file#use-case-1-wasting-no-memory)
        and [this](https://news.ycombinator.com/item?id=34993661#:~:text=tialaramex%20on%20March%202%2C%202023,if%20the%20commitee%20wants%20to))
      + mention PointerIntPair in LLVM (and similar tricks in interpreters)
    * situation in other langs:
      + [Java](https://docs.oracle.com/javase/specs/jls/se24/html/),
      + [C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/introduction)
      + [Go](https://go.dev/ref/spec)
      + [Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/aboutthelanguagereference/)
      + [Fortran](https://j3-fortran.org/doc/year/24/24-007.pdf)
      + Ada ([RM](http://www.ada-auth.org/standards/22rm/html/RM-TOC.html) and [ARM](http://www.ada-auth.org/standards/22aarm/html/AA-TOC.html))
  - types of optimizations (niche via fields, niche via ranges, struct reorg)
  - consequences (lack of stable ABI)

# Examples

TODO:
  - clear example (Rust microbenchmark, asm code)

# Optimizations

# Workarounds

TODO:
  - info on how developer can disable this optimization

# Suggested reading

TODO:
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)

# Performance impact

## Prevalence

TODO:
  - is this check is a common case in practice ?
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences

## Disabling the opt

TODO:
  - determine how to disable opts in compiler
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      + patch for each feature needs to be implemented in separate branch (in private compiler repo)
      + compiler modifications need to be kept in private compiler repo `yugr/rust-private`
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`

## Measurements

TODO:
  - collect perf measurements for benchmarks:
    * runtime
      + large unexpected changes need to be investigated
    * code size (if applicable)
    * compiler stats (if applicable)
      + depend on feature
      + LLVM stats may be misleading because some opts (e.g. inline) are done in frontend
        (at MIR level). But recollecting with `-Zmir-opt-level=0`
        e.g. in panic feature didn't improve anything.
      + e.g. SLP/loop autovec for bounds checking feature
      + e.g. NoAlias returns from AA manager for alias feature
      + e.g. CSE/GVN/LICM for alias feature

### Analyzing rav1e results

Performance of rav1e has (rather unexpectedly) degraded overall.

To understand this, I studied
  - one heavy regression in `get_weighted_sse/32x8/10` (1.0878 -> 1.3253 us)
  - one speedup in `forward_transform/TX_16X16_H_ADST` (431.88 -> 393.7 ns)

#### get_weighted_sse regression (scalar)

I compiled with `.cargo/config.toml` to simplify analysis:
```
[build]
rustflags = [
  "-C", "llvm-args=-vectorize-loops=false",
  "-C", "llvm-args=-vectorize-slp=false",
  "-C", "llvm-args=-unroll-threshold=0",
  "-C", "llvm-args=-unroll-max-count=1",
]
```

Regressions reproduced (actually got worse).

Bench has a single hot loop which is totally identical in ref and new:
```
   # REF (31 bytes)
   1.44 │21fe0:   movzwl (%rdi,%r10,2),%edx                                                                                                                  ▒
  13.48 │21fe5:   movzwl (%r15,%r10,2),%ebx                                                                                                                  ▒
   1.44 │21fea:   lea    0x1(%r10),%rcx                                                                                                                      ▒
   8.18 │21fee:   sub    %ebx,%edx                                                                                                                           ▒
   8.36 │21ff0:   imul   %edx,%edx                                                                                                                           ▒
  14.46 │21ff3:   add    %edx,%r13d                                                                                                                          ▒
   0.99 │21ff6:   mov    %rcx,%r10                                                                                                                           ▒
   1.26 │21ff9:   cmp    $0x4,%rcx                                                                                                                           ▒
   6.02 │21ffd: ↑ jne    21fe0 <rav1e::dist::rust::get_weighted_sse+0x220>                                                                                   ▒

   # NEW (33 bytes)
   4.36 │1b700:   movzwl (%r15,%rcx,2),%r13d                                                                                                                 ▒
   7.79 │1b705:   movzwl (%r10,%rcx,2),%r8d                                                                                                                  ▒
   2.47 │1b70a:   lea    0x1(%rcx),%rbp                                                                                                                      ▒
   2.24 │1b70e:   sub    %r8d,%r13d                                                                                                                          ▒
  20.83 │1b711:   imul   %r13d,%r13d                                                                                                                         ▒
  12.22 │1b715:   add    %r13d,%r14d                                                                                                                         ▒
   3.18 │1b718:   mov    %rbp,%rcx                                                                                                                           ▒
        │1b71b:   cmp    $0x4,%rbp                                                                                                                           ▒
   0.81 │1b71f: ↑ jne    1b700 <rav1e::dist::rust::get_weighted_sse+0x340>                                                                                   ▒
```

Note that in new variant loop size exceeds fetchline size (32 bytes)
due to different regalloc so this explains performance drop.

We can prove this by checking perf counters:
execution time is dominated by frontend:
```
# REF
$ perf stat --topdown target/release/deps/demo-a0b0c58aa3cfa94b

 Performance counter stats for 'target/release/deps/demo-a0b0c58aa3cfa94b':

 %  tma_bad_speculation %  tma_backend_bound      %  tma_retiring %  tma_frontend_bound
                    3.0                  0.8                 77.7                   18.5

# NEW
$ perf stat --topdown target/release/deps/demo-a0b0c58aa3cfa94b

 Performance counter stats for 'target/release/deps/demo-a0b0c58aa3cfa94b':

 %  tma_bad_speculation %  tma_backend_bound      %  tma_retiring %  tma_frontend_bound
                    2.3                  0.6                    61.9                   35.2
```
which fails to supply uops at full speed:
```
# REF
$ perf stat -M tma_fetch_bandwidth target/release/deps/demo-a0b0c58aa3cfa94b

 Performance counter stats for 'target/release/deps/demo-a0b0c58aa3cfa94b':

       270,960,680      CPU_CLK_UNHALTED.REF_XCLK        #     16.9 %  tma_fetch_bandwidth

# NEW
$ perf stat -M tma_fetch_bandwidth target/release/deps/demo-a0b0c58aa3cfa94b

 Performance counter stats for 'target/release/deps/demo-a0b0c58aa3cfa94b':

       389,605,649      CPU_CLK_UNHALTED.REF_XCLK        #     24.4 %  tma_fetch_bandwidth
```

This does not look very relevant to original regression though
so need to investigate at least vectorized version.

#### get_weighted_sse regression (vector)

I compiled with `.cargo/config.toml` to simplify analysis:
```
[build]
rustflags = [
  "-C", "llvm-args=-vectorize-loops=false",
  "-C", "llvm-args=-vectorize-slp=false",
  "-C", "llvm-args=-unroll-threshold=0",
  "-C", "llvm-args=-unroll-max-count=1",
]
```

Regression reproduced (23%). Hot loops are again very similar
but new (slow) has extra branch in header:
```
   # REF
   0.96 │21f90:   test      %rdx,%rdx                                                                                                                        ▒
        │21f93: ↑ je        21f10 <rav1e::dist::rust::get_weighted_sse+0x150>                                                                                ▒
   3.17 │21f99:   test      %r15,%r15                                                                                                                        ▒
        │21f9c: ↑ je        21f10 <rav1e::dist::rust::get_weighted_sse+0x150>                                                                                ▒
   2.71 │21fa2:   movq      (%rdx),%xmm1                                                                                                                     ▒
   ...
   0.80 │21ff2:   inc       %rsi
   1.86 │21ff5: ↑ jne       21f90 <rav1e::dist::rust::get_weighted_sse+0x1d0>

   # NEW
   1.92 │22130:   test      %r15,%r15                                                                                                                        ▒
        │22133: ↑ je        22050 <rav1e::dist::rust::get_weighted_sse+0x1d0>                                                                                ▒
   1.91 │22139:   test      %rdi,%rdi                                                                                                                        ▒
        │2213c: ↑ je        22050 <rav1e::dist::rust::get_weighted_sse+0x1d0>                                                                                ▒
   1.91 │22142:   test      %r10,%r10                                                                                                                        ▒
        │22145: ↑ je        22050 <rav1e::dist::rust::get_weighted_sse+0x1d0>                                                                                ▒
   2.19 │2214b:   movq      (%r15),%xmm1                                                                                                                     ▒
   ...
   0.14 │2219b:   inc       %rdi
   1.65 │2219e: ↑ jne       22130 <rav1e::dist::rust::get_weighted_sse+0x2b0>
```

New version also has more branch misses but they seem too few to explain the regression:
```
# REF
$ perf stat target/release/deps/demo-cdc4b7bc884841f7

 Performance counter stats for 'target/release/deps/demo-cdc4b7bc884841f7':

     5,685,451,288      task-clock                       #    0.999 CPUs utilized
                23      context-switches                 #    4.045 /sec
                 0      cpu-migrations                   #    0.000 /sec
               846      page-faults                      #  148.801 /sec
    43,463,436,191      instructions                     #    3.83  insn per cycle
    11,344,184,138      cycles                           #    1.995 GHz
     5,329,352,506      branches                         #  937.367 M/sec
         5,116,308      branch-misses                    #    0.10% of all branches


# NEW
$ perf stat target/release/deps/demo-cdc4b7bc884841f7

 Performance counter stats for 'target/release/deps/demo-cdc4b7bc884841f7':

     6,970,952,168      task-clock                       #    0.999 CPUs utilized
                54      context-switches                 #    7.746 /sec
                 0      cpu-migrations                   #    0.000 /sec
               847      page-faults                      #  121.504 /sec
    53,936,105,451      instructions                     #    3.88  insn per cycle
    13,908,865,747      cycles                           #    1.995 GHz
     7,096,279,246      branches                         #    1.018 G/sec
        10,144,087      branch-misses                    #    0.14% of all branches
```

Extra compare-and-branch can only account for 2 / 16 = 7.5% cycles.

I wonder where extra instructions are coming from ?
The rest may come from differences in outer loop which is much shorter in ref
(231 vs 336 insns).

This is because in new version we have two duplicate indices:
```
"_ZN105_$LT$rav1e..tiling..plane_region..RowsIter$LT$T$GT$$u20$as$u20$core..iter..traits..iterator..Iterator$GT$4next17h5c9f5dd719ceefd5E.exit19.i.i.i.i.i.i.i.i.i.i.i": ; preds = %"_ZN105_$LT$rav1e..tiling..plane_region..RowsIter$LT$T$GT$$u20$as$u20$core..iter..traits..iterator..Iterator$GT$4next17h5c9f5dd719ceefd5E.exit19.i.i.i.i.i.i.i.i.i.i.i.preheader", %middle.block
  ...
  %36 = phi i64 [ %38, %middle.block ], [ 4, %"_ZN105_$LT$rav1e..tiling..plane_region..RowsIter$LT$T$GT$$u20$as$u20$core..iter..traits..iterator..Iterator$GT$4next17h5c9f5dd719ceefd5E.exit19.i.i.i.i.i.i.i.i.i.i.i.preheader" ]
  ...
  %37 = phi i64 [ %39, %middle.block ], [ 4, %"_ZN105_$LT$rav1e..tiling..plane_region..RowsIter$LT$T$GT$$u20$as$u20$core..iter..traits..iterator..Iterator$GT$4next17h5c9f5dd719ceefd5E.exit19.i.i.i.i.i.i.i.i.i.i.i.preheader" ]
  ...
  %_2.not.i.i.i.i.i.i.i.i.i.i.i.i = icmp eq i64 %37, 0
  %or.cond2.i.i.i.i.i.i.i.i = select i1 %.not.i.i.i.i.i.i.i.i.i.i.i, i1 true, i1 %_2.not.i.i.i.i.i.i.i.i.i.i.i.i, !dbg !1723
  %.not9.i.i.i.i.i.i.i.i.i.i.i = icmp eq ptr %_6.i.i1012.i.i.i.i.i.i.i.i.i.i, null
  %or.cond = select i1 %or.cond2.i.i.i.i.i.i.i.i, i1 true, i1 %.not9.i.i.i.i.i.i.i.i.i.i.i, !dbg !1723
  br i1 %or.cond, label %"_ZN4core4iter8adapters3map8map_fold28_$u7b$$u7b$closure$u7d$$u7d$17h09c06f5ea5b3b2c7E.exit.i.i.i.i.i.i", label %middle.block, !dbg !1723

middle.block:                                     ; preds = %"_ZN105_$LT$rav1e..tiling..plane_region..RowsIter$LT$T$GT$$u20$as$u20$core..iter..traits..iterator..Iterator$GT$4next17h5c9f5dd719ceefd5E.exit19.i.i.i.i.i.i.i.i.i.i.i"
  %38 = add i64 %36, -1, !dbg !1768
  ...
  %39 = add i64 %37, -1, !dbg !1770
```

The extra index is used for unnecessary extra check.

After tracing LLVM log (obtained via `-Cllvm-args=-print-after-all -Cllvm-args=-debug-only=inline`)
it seems that inefficient code is coming (via inlining) from
  - `rav1e::dist::rust::get_weighted_sse`
    * ref: `_ZN5rav1e4dist4rust16get_weighted_sse17hcfef2694476d3a0aE`
    * new: `_ZN5rav1e4dist4rust16get_weighted_sse17h4008daa6c4ccde8cE`
  - `<core::iter::adapters::zip::Zip<A,B> as core::iter::adapters::zip::ZipImpl<A,B>>::fold`
    * ref: `_ZN111_$LT$core..iter..adapters..zip..Zip$LT$A$C$B$GT$$u20$as$u20$core..iter..adapters..zip..ZipImpl$LT$A$C$B$GT$$GT$4fold17h80e5040784adedaaE`
    * new: `_ZN111_$LT$core..iter..adapters..zip..Zip$LT$A$C$B$GT$$u20$as$u20$core..iter..adapters..zip..ZipImpl$LT$A$C$B$GT$$GT$4fold17he26f2e2d1bc80adeE`
  - `<core::iter::adapters::zip::Zip<A,B> as core::iter::adapters::zip::SpecFold>::spec_fold`
    * ref: `_ZN99_$LT$core..iter..adapters..zip..Zip$LT$A$C$B$GT$$u20$as$u20$core..iter..adapters..zip..SpecFold$GT$9spec_fold17h1a4cbb411acf9760E`
    * new: `_ZN99_$LT$core..iter..adapters..zip..Zip$LT$A$C$B$GT$$u20$as$u20$core..iter..adapters..zip..SpecFold$GT$9spec_fold17h5a8adc594c0cf459E`
  - `core::iter::adapters::map::map_fold::{{closure}}`
    * ref: `_ZN4core4iter8adapters3map8map_fold28_$u7b$$u7b$closure$u7d$$u7d$17h0dea136089c7d852E`
    * new: `_ZN4core4iter8adapters3map8map_fold28_$u7b$$u7b$closure$u7d$$u7d$17ha229a2f49b24cee0E`
  - `rav1e::dist::rust::get_weighted_sse::{{closure}}::{{closure}}`
    * ref: `_ZN5rav1e4dist4rust16get_weighted_sse28_$u7b$$u7b$closure$u7d$$u7d$17ha22c77b1f0dd083eE`
    * new: `_ZN5rav1e4dist4rust16get_weighted_sse28_$u7b$$u7b$closure$u7d$$u7d$28_$u7b$$u7b$closure$u7d$$u7d$17hba09bac1c1a9b512E`
  - `<core::iter::adapters::zip::Zip<A,B> as core::iter::adapters::zip::ZipImpl<A,B>>::fold`
    * ref: `_ZN111_$LT$core..iter..adapters..zip..Zip$LT$A$C$B$GT$$u20$as$u20$core..iter..adapters..zip..ZipImpl$LT$A$C$B$GT$$GT$4fold17ha94cd43271bb9e5dE`
    * new: `_ZN111_$LT$core..iter..adapters..zip..Zip$LT$A$C$B$GT$$u20$as$u20$core..iter..adapters..zip..ZipImpl$LT$A$C$B$GT$$GT$4fold17ha4a1d564d7ba5f78E`
  - `<core::iter::adapters::zip::Zip<A,B> as core::iter::adapters::zip::SpecFold>::spec_fold`
    * ref: `_ZN99_$LT$core..iter..adapters..zip..Zip$LT$A$C$B$GT$$u20$as$u20$core..iter..adapters..zip..SpecFold$GT$9spec_fold17hbb8d059ec1d997c9E`
    * new: `_ZN99_$LT$core..iter..adapters..zip..Zip$LT$A$C$B$GT$$u20$as$u20$core..iter..adapters..zip..SpecFold$GT$9spec_fold17h33b61e2f28d0b68dE`

We then get discrepancy at
  - `<core::iter::adapters::zip::Zip<A,B> as core::iter::adapters::zip::ZipImpl<A,B>>::next`
    * ref: `_ZN111_$LT$core..iter..adapters..zip..Zip$LT$A$C$B$GT$$u20$as$u20$core..iter..adapters..zip..ZipImpl$LT$A$C$B$GT$$GT$4next17h4eb2a82c80d1190fE`
    * new: `_ZN111_$LT$core..iter..adapters..zip..Zip$LT$A$C$B$GT$$u20$as$u20$core..iter..adapters..zip..ZipImpl$LT$A$C$B$GT$$GT$4next17h87d7f54ec0e98452E`
  - `core::iter::adapters::map::map_fold::{{closure}}`
    * ref: `_ZN4core4iter8adapters3map8map_fold28_$u7b$$u7b$closure$u7d$$u7d$17hd4ad2369c6d1a1a9E`
    * new: `_ZN4core4iter8adapters3map8map_fold28_$u7b$$u7b$closure$u7d$$u7d$17h2dae2b7eb748ae77E`

Intuitively it seems that the reason is differences in InstCombine logic.

TODO

# forward_transform improvement

TODO

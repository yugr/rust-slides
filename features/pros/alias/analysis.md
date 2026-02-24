# Administrivia

Assignee: yugr

Parent task: gh-39

Effort: 24h

# Background

Memory aliasing is a common concept across programming langs
when different pointers/references address same memory location.

There are two extreme cases in language design:
  - allow this for any pair of pointers
  - completely disallow this
and a lot of intermediate options.

Landi proved that interprocedural AA is undecidable and
intraprocedural AA is NP-complete
(Undecidability of static analysis, Landi, 1992).

Originally C allowed arbitrary aliasing which was made more strict in C99
by disallowing aliasing of references of different types
(so called "strict aliasing"). This broke a lot of existing code and
to date a lot of projects are compiled with `-fno-strict-aliasing`.

Aliasing semantics is very important because it allows compiler
to optimize code much more aggressively via vectorization, CSE/GVN, LICM, DSE, etc.
(or prevents it from doing so !).

In practice aliasing is extremely rare. According to
"Dynamic Points-To Sets: A Comparison with Static Analyses and Potential Applications in Program Understanding and Optimization"
98% of pointers in SPEC benchmarks address only single object
and state-of-the-art static alias analyses overestimate this by 2-20x.
Similar results are reported in "Speculative Alias Analysis for Executable Code"
and are also a common knowledge among compiler writers.

Why would a language allow aliasing to begin with ?
Because it allows to write low-level code much more easily
which is particularly important for system programming langs.

Other languages e.g. Fortran have much stricter aliasing rules and
Rust also falls into this category w.r.t. references
(raw pointers can alias and unlike C/C++ there is
[not even type-based aliasing](https://users.rust-lang.org/t/question-about-rustc-aliasing-analysis/82398/3))
but in unique in that alias correctness is enforced by language rules.

Zig, it seems, is more C-like - everything aliases by default and
`noalias` need to be specified explicitly
(see [#1108](https://github.com/ziglang/zig/issues/1108)).

I was unable to find good description of situation in other languages
(Java, Swift, Go, Julia).

TODO:
  - situation in other langs
  - [Tree Borrows and Stack Borrows](https://internals.rust-lang.org/t/tree-borrows-explained/18587)
    (also [here](https://www.reddit.com/r/rust/comments/124jp5o/tree_borrows_a_new_aliasing_model_for_rust/))
  - add info from [Horizon paper](https://dl.acm.org/doi/10.1145/3771775.3786270)

# Examples

For this simple code
```
int foo(int * a, int * b) {
  *a = 1;
  *b = 2;
  return *a;
}
```
we could expect no loads but in fact we get it:
```
movl    $1, (%rdi)
movl    $2, (%rsi)
movl    (%rdi), %eax
retq
```
because compiler has to consider that `a` and `b` point to same location in memory
(i.e. alias).  It generates expected code if both pointers are marked with `restrict`.

An equivalent Rust code:
```
#[no_mangle]
pub fn foo(a: &mut i32, b: &mut i32) -> i32{
    *a = 1;
    *b = 2;
    *a
}
```
generates expected assembly
```
movl    $1, (%rdi)
movl    $2, (%rsi)
movl    $1, %eax
retq
```
because of language aliasing rules:
  - mutable reference can't alias anything
    (Rust's shared refs are true constants unlike in C/C++)

Interestingly enough for loops e.g.
```
void foo(int * RESTRICT a, const int * RESTRICT b, unsigned n) {
  for (unsigned i = 0; i < n; ++i)
    a[i] = b[i] + 100;
}
```
modern Clang will add a [runtime aliasing check](https://llvm.org/docs/Vectorizers.html#runtime-checks-of-pointers)
and generate two versions of loop (GCC does not do this)
(this is a case of "speculative alias analysis").

Other languages also have more strict aliasing guarantees
e.g. equivalent Fortran program
```
FUNCTION FOO(X, Y)
  INTEGER :: X, Y, FOO
  X = 1
  Y = 2
  FOO = X
END
```
generates same code as Rust (but Fortran does not enforce
language rules so it's much easier to make a mistake).

# Optimizations

Alias analysis is used by many opts:
```
$ grep -l 'getModRefInfo\|\<alias(\|isNoAlias' lib/Transforms/
lib/Transforms/Coroutines/CoroElide.cpp
lib/Transforms/InstCombine/InstCombineLoadStoreAlloca.cpp
lib/Transforms/InstCombine/InstructionCombining.cpp
lib/Transforms/InstCombine/InstCombineCalls.cpp
lib/Transforms/AggressiveInstCombine/AggressiveInstCombine.cpp
lib/Transforms/Utils/FlattenCFG.cpp
lib/Transforms/Utils/LoopUtils.cpp
lib/Transforms/Utils/MoveAutoInit.cpp
lib/Transforms/IPO/AttributorAttributes.cpp
lib/Transforms/IPO/ArgumentPromotion.cpp
lib/Transforms/IPO/FunctionAttrs.cpp
lib/Transforms/IPO/Attributor.cpp
lib/Transforms/Vectorize/SLPVectorizer.cpp
lib/Transforms/Vectorize/VectorCombine.cpp
lib/Transforms/Vectorize/SandboxVectorizer/DependencyGraph.cpp
lib/Transforms/Vectorize/LoadStoreVectorizer.cpp
lib/Transforms/Scalar/LoopIdiomRecognize.cpp
lib/Transforms/Scalar/TailRecursionElimination.cpp
lib/Transforms/Scalar/LowerMatrixIntrinsics.cpp
lib/Transforms/Scalar/GVN.cpp
lib/Transforms/Scalar/MergeICmps.cpp
lib/Transforms/Scalar/Sink.cpp
lib/Transforms/Scalar/DeadStoreElimination.cpp
lib/Transforms/Scalar/LICM.cpp
lib/Transforms/Scalar/LoopPredication.cpp
lib/Transforms/Scalar/MemCpyOptimizer.cpp
lib/Transforms/ObjCARC/ProvenanceAnalysis.cpp
lib/Transforms/ObjCARC/ObjCARCOpts.cpp
lib/Transforms/ObjCARC/ObjCARCContract.cpp
```

# Limitations

Currently Rust only provides alias info to LLVM for function parameters
(`noalias` attribute).
It could also use [alias.scope metadata](http://llvm.org/docs/LangRef.html#noalias-and-alias-scope-metadata)
or `llvm.experimental.noalias.scope.decl` intrinsic but currently [does not](https://github.com/rust-lang/rust/issues/16515).
In some (many?) cases this leads to redundant aliases in LLVM.
E.g. if we slightly change our starting code:
```
pub fn bar(a: *mut i32, b: *mut i32) -> i32 {
    let a = unsafe { &mut *a };
    let b = unsafe { &mut *b };
    *a = 1;
    *b = 2;
    return *a;
}
```
we will get a redundant load.

There is a plethora of linked issues showing that people hit
this issue in practice and also some projects work around this limitation by
[introducing dummy functions](https://github.com/rust-lang/rust/commit/71f5cfb21f3fd2f1740bced061c66ff112fec259)).

There are a lot of [mentions](https://www.reddit.com/r/rust/comments/acjcbp/comment/ed8nkmj/)
that `&mut Vec<T>` does not allow noalias for contained buffer and `&[T]` should be used instead.
I believe this came from the fact that `&Vec` is passed as a single pointer argument
and, even though this pointer is marked as `noalias`, pointer to data inside of it is not
which leads to redundant aliasing.

This can be seen from comparison of generated LLVM IR for
```
#[no_mangle]
pub fn foo(a: &mut [i32], b: &[i32]) {
    let n = a.len();
    let b = &b[..n];
    for i in 0..n {
        a[i] = b[i] + 100;
    }
}
```
and
```
#[no_mangle]
pub fn foo(a: &mut Vec<i32>, b: &Vec<i32>) {
    let n = a.len();
    let b = &b[..n];
    for i in 0..n {
        a[i] = b[i] + 100;
    }
}
```
(Vec-code has additional loop versioning due to potential aliasing).

TODO:
  - ORAQL — Optimistic Responses to Alias Queries in LLVM

# Suggested readings

TODO:
  - links to important articles (design, etc.)

# Performance impact

Parts of aliasing checks can be disabled via `-Z box-noalias=no` and `-Z mutable-noalias=no`.

## Prevalence

Efficiency of alias analysis is usually compared via AA precision
i.e. ratio of precise results (NoAlias + MustAlias) vs. all queries.

# Approach 1

This uses AliasAnalysisEvaluator:
```
diff --git a/llvm/lib/Passes/PassBuilderPipelines.cpp b/llvm/lib/Passes/PassBuilderPipelines.cpp
index 17ff3bd37..b63498a75 100644
--- a/llvm/lib/Passes/PassBuilderPipelines.cpp
+++ b/llvm/lib/Passes/PassBuilderPipelines.cpp
@@ -16,6 +16,7 @@

 #include "llvm/ADT/Statistic.h"
 #include "llvm/Analysis/AliasAnalysis.h"
+#include "llvm/Analysis/AliasAnalysisEvaluator.h"
 #include "llvm/Analysis/BasicAliasAnalysis.h"
 #include "llvm/Analysis/CGSCCPassManager.h"
 #include "llvm/Analysis/CtxProfAnalysis.h"
@@ -1559,6 +1560,8 @@ PassBuilder::buildModuleOptimizationPipeline(OptimizationLevel Level,
                           .speculateUnpredictables(true)
                           .hoistLoadsStoresWithCondFaulting(true)));

+  OptimizePM.addPass(AAEvaluator());
+
   // Add the core optimizing pipeline.
   MPM.addPass(createModuleToFunctionPassAdaptor(std::move(OptimizePM),
```
and then
```
$ ./x build --stage 1 compiler && ./x build -j1 --stage 2 compiler |& tee build.log
$ cat build.log | awk 'BEGIN{prec=0; tot=0} /Total Alias Queries/{tot+=$1} /no alias responses|must alias responses/{prec+=$1} END{print prec " " tot}'
```

Rust:
  - baseline: 267950087 / 304403228 = 88%
  - force-aliasing: 259796295 / 300809438 = 86%

TODO:
  - rebuild rustc w/ `debug-assertions=false` and recollect data

Results for other projects can be collected via
```
for d in *; do
  test -d $d || continue
  (cd $d; cargo clean && cargo +baseline b --release &> ref.log; cargo clean && cargo +force-aliasing b --release &> new.log)
  echo "=== $d"
  cat $d/ref.log | awk 'BEGIN{prec=0; tot=0} /Total Alias Queries/{tot+=$1} /no alias responses|must alias responses/{prec+=$1} END{print prec " " tot}'
  cat $d/new.log | awk 'BEGIN{prec=0; tot=0} /Total Alias Queries/{tot+=$1} /no alias responses|must alias responses/{prec+=$1} END{print prec " " tot}'
done
```

Results for other projects vary A LOT:
  - SpacetimeDB: 83% vs 81%
  - bevy: 72% vs 67%
  - meilisearch: 47% vs 41%
  - nalgebra: 66% vs 30%
  - oxipng: 99% both
  - rav1e: 89% vs 87%
  - rebar: 88% vs 82%
  - ruff: 80% vs 76%
  - rust_serialization_benchmark: 78% vs 75%
  - rustc-perf: 84% vs 83%
  - tokio: 87% vs 82%
  - uv: 87% both
  - veloren: 57% vs 55%
  - zed: 79% vs 78%

So we see that in some cases results are practically the same and
2-7% worse in other cases (except for nalgebra with over 2x).

Interestingly enough Clang has just 55% precision when building itself !

### Approach 2

This approach does not use AliasAnalysisEvaluator.

We patch LLVM:
```
diff --git a/llvm/lib/Analysis/AliasAnalysis.cpp b/llvm/lib/Analysis/AliasAnalysis.cpp
index 061a7e8e5..0093c62f6 100644
--- a/llvm/lib/Analysis/AliasAnalysis.cpp
+++ b/llvm/lib/Analysis/AliasAnalysis.cpp
@@ -143,9 +143,20 @@ AliasResult AAResults::alias(const MemoryLocation &LocA,
     else
       ++NumMayAlias;
   }
   return Result;
 }

+#include <sstream>
+
+struct AliasPrinter {
+  ~AliasPrinter() {
+    std::ostringstream S;
+    S << "Aliases: " << NumNoAlias << " " << NumMustAlias << " " << NumMayAlias << "\n";
+    dbgs() << S.str();
+  }
+} AliasPrinter;
+
 ModRefInfo AAResults::getModRefInfoMask(const MemoryLocation &Loc,
                                         bool IgnoreLocals) {
```
and then
```
$ ./x build --stage 1 compiler && ./x build -j1 --stage 2 compiler |& tee build.log
$ cat build.log | awk 'BEGIN{prec=0; tot=0} /Aliases/{prec+=$2+$3; tot+=$2+$3+$4} END{print prec " " tot}'
```

Rust:
  - baseline: 266298621 / 274619155 == 97%
  - force-aliasing: ???

TODO: recollect results for force-aliasing

## Disabling optimization

Compiler patch is in branch [yugr/force-aliasing/1](https://github.com/yugr/rust-private/tree/yugr/force-aliasing/1).
It
  - disables checks in compiler
  - removes relevant `panic!` / `assert!` / etc. in stdlib

## Measurements

### Static estimates

Following instructions for [bounds checks](../../cons/bounds-checks/analysis.md#static-estimates):
```
$ ./x setup
$ export RUSTFLAGS_NOT_BOOTSTRAP='-Cllvm-args=-debug-only=licm,early-cse,gvn,loop-vectorize,SLP'
$ ./x build --stage 1 compiler
$ ./x build -j1 --stage 2 compiler &> build.log

# Baseline
$ grep -c 'LV: Vectorizing' build.log
549
$ grep -c 'LICM \(hoist\|sink\)ing' build.log
2248947
$ grep -c 'GVN removed' build.log
798566
$ grep -c 'EarlyCSE CSE' build.log
2380605
$ grep -c 'SLP: vectorized' build.log
25065

# Forced aliasing
$ grep -c 'LV: Vectorizing' build.log
392 (-28%)
$ grep -c 'LICM \(hoist\|sink\)ing' build.log
2210414 (-1.5%)
$ grep -c 'GVN removed' build.log
737348 (-6%)
$ grep -c 'EarlyCSE CSE' build.log
2200458 (-7%)
$ grep -c 'SLP: vectorized' build.log
25504 (+1%)
```

According to [The Limits of Alias Analysis for Scalar Optimizations](https://www.cs.utexas.edu/~mckinley/papers/alias-cc-2004.pdf)
AA mainly affects LICM.

### Runtime improvements

Disabling the feature obviously decreases perf:
```
$ ../../benchmarks/compare.py baseline/ force-aliasing/
SpacetimeDB_0.json: -0.6%
bevy_0.json: +0.0%
meilisearch_0.json: -4.2%
nalgebra_0.json: -4.1%
oxipng_0.json: +2.0%
rav1e_0.json: -2.1%
regex_0.json: -1.2%
ruff_0.json: -0.9%
rust_serialization_benchmark_0.json: -2.3%
tokio_0.json: -0.5%
uv_0.json: -1.3%
veloren_0.json: -4.4%
zed_0.json: -0.3%
```

TODO: perf measurements for AArch64

Largest speedups in oxipng are in
  - reductions_16_to_8_bits (30%)
  - reductions_rgb_to_grayscale_16 (25%) - not reproduced (microarch effect ?)
  - filters_16_bits_filter_3 (23%) - not reproduced (microarch effect ?)
  - `filters_[1248]_bits_filter_3` (20%) - not reproduced (microarch effect ?)
  - filters_bigent (14%)

There are also slowdowns but not as many:
  - `deinterlacing_[124]_bits` (13%)
  - reductions_palette_8_to_grayscale_8 (16%)

To analyze regressions, update
```
#strip = "symbols"
debug = "line-tables-only"
```
in `Cargo.toml` and collect profile via
```
rm perf.data* && perf record -F99 target/release/deps/NAME_OF_SUITE --bench NAME_OF_BENCH
```

#### reductions_16_to_8_bits

Collect profile via
```
rm perf.data* && perf record -F99 target/release/deps/reductions-636692b0b03e7601 --bench --skip reductions_16_to_8_bits_scaled reductions_16_to_8_bits
```

The main reason for degradation is that without aliasing we suddenly get this loop
```
# png.data is &Vec<u8}
png.data.chunks_exact(2).map(|pair| pair[0]).collect()n
```
which originall codegen-ed to
```
220: movzbl    0x1(%rbp),%edx
mov       %dl,(%r12,%r13,1)
movzbl    0x2(%rbp),%edx
mov       %dl,0x1(%r12,%r13,1)
movzbl    0x4(%rbp),%edx
mov       %dl,0x2(%r12,%r13,1)
movzbl    0x6(%rbp),%edx
add       $0x8,%rbp
mov       %dl,0x3(%r12,%r13,1)
add       $0x4,%r13
cmp       %r13,%rcx
jne       220
```
to vectorize
```
1d0: movdqu    (%r14,%rsi,2),%xmm1
movdqu    0x10(%r14,%rsi,2),%xmm2
pand      %xmm0,%xmm2
pand      %xmm0,%xmm1
packuswb  %xmm2,%xmm1
movdqu    %xmm1,(%rcx,%rsi,1)
add       $0x10,%rsi
cmp       %rsi,%rax
jne       1d0
```

Interestingly enough, standalone example vectorizes fine in both.

Vectorization log can be collected by adding `#[no_mangle]` to `reduced_bit_depth_16_to_8` proto and
```
[target.x86_64-unknown-linux-gnu]
rustflags = ["-Cllvm-args=-debug-only=loop-vectorize -print-before=loop-vectorize --filter-print-funcs=reduced_bit_depth_16_to_8"]
```
to `.cargo/config`. Then run
```
$ cargo bench --no-run -j1 reductions_16_to_8_bits
```

Problematic loop looks like
```
167:                                              ; preds = %165, %167
  %168 = phi i64 [ %175, %167 ], [ 0, %165 ]
  %169 = phi i64 [ %172, %167 ], [ %15, %165 ]
  %170 = phi ptr [ %171, %167 ], [ %13, %165 ]
  %171 = getelementptr inbounds nuw i8, ptr %170, i64 2, !dbg !617
  %172 = add i64 %169, -2, !dbg !622
  tail call void @llvm.experimental.noalias.scope.decl(metadata !623), !dbg !626
  %173 = load i8, ptr %170, align 1, !dbg !627, !alias.scope !632, !noalias !635, !noundef !13
  %174 = getelementptr inbounds nuw i8, ptr %163, i64 %168, !dbg !652
  store i8 %173, ptr %174, align 1, !dbg !659, !noalias !662
  %175 = add nuw nsw i64 %168, 1, !dbg !667
  %176 = icmp eq i64 %172, 0, !dbg !596
  br i1 %176, label %177, label %167, !dbg !596
```
in baseline and
```
213:                                              ; preds = %210, %213
  %214 = phi i64 [ %221, %213 ], [ %208, %210 ], !dbg !24808
  %215 = phi ptr [ %218, %213 ], [ %18, %210 ], !dbg !24809
  %216 = phi i64 [ %217, %213 ], [ %22, %210 ]
  %217 = sub nuw i64 %216, 2, !dbg !24810
  %218 = getelementptr inbounds nuw i8, ptr %215, i64 2, !dbg !24814
  %219 = load i8, ptr %215, align 1, !dbg !24803, !noalias !24718, !noundef !424
  %220 = getelementptr inbounds nuw i8, ptr %207, i64 %214, !dbg !24816
  store i8 %219, ptr %220, align 1, !dbg !24823, !noalias !24718
  %221 = add i64 %214, 1, !dbg !24826
  %222 = icmp ult i64 %217, 2, !dbg !24791
  br i1 %222, label %235, label %213, !dbg !24791
```
in aliased version.

Debug message which marks start of loop handling is
```
LV: Checking a loop in 'reduced_bit_depth_16_to_8' from .* bit_depth.rs:26
```

Problem is cause by additional `sub` in aliased version which changes loop cost
and causes loop to not be vectorized in some cases
(particularly in `target/deps/reductions`)

#### filters_bigent

Regression is much smaller (6%) when I try to repro it and
reduces to 4% when I start to play with alignment by adding
```
[target.x86_64-unknown-linux-gnu]
rustflags = ["-Cllvm-args=-align-loops=1"]
```
in `.cargo/config`. Default align on LLVM X86 is
```
setPrefLoopAlignment(Align(16));
```

So I suspect this is another [code alignment issue](https://easyperf.net/blog/2018/01/18/Code_alignment_issues).

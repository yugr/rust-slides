# Administrivia

Assignee: yugr
Parent task: gh-39
Effort: 10h

# Background

Memory aliasing is a common concept across programming langs
when different pointers/references address same memory location.

There are two extreme cases in language design:
  - allow this for any pair of pointers
  - completely disallow this
and a lot of intermediate options.

Originally C allowed arbitrary aliasing which was made more strict in C99
by disallowing aliasing of references of different types
(so called "strict aliasing"). This broke a lot of existing code and
to date a lot of projects are compiled with `-fno-strict-aliasing`.

Aliasing semantics is very important because it allows compiler
to optimize code much more aggressively via vectorization, GVN, LICM, etc.
(or prevents it from doing so !).

Why would language allow aliasing to begin with ?
It allows to write low-level code much more easily
which is particularly important for system programming langs.

Other languages e.g. Fortran have much stricter aliasing rules and
Rust also falls into this category w.r.t. references
(raw pointers can alias and there is not even type-based aliasing as in C/C++ !)

TODO:
  - situation in other languages (Java, Swift, Julia) ?
  - most runtime aliases are fake
  - situation in C++
    * e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
    * e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
  - alias (pointer) analysis precision:
    * [AN EMPIRICAL STUDY OF ALIAS ANALYSIS TECHNIQUES](https://digitalcommons.calpoly.edu/cgi/viewcontent.cgi?article=3206&context=theses)
    * [Speculative Alias Analysis for Executable Code](https://arcb.csc.ncsu.edu/~mueller/pact02/papers/fernandez152.pdf):
      significant improvement of precision from using speculation

# Examples

For this simple code
```
void foo(int * a, const int * b) {
  *a = *b;
  *a += *b;
}
```
we could expect a single load and a single store
but in fact we get 2 loads and 2 stores:
```
movl (%rsi), %eax
movl %eax, (%rdi)
addl (%rsi), %eax
movl %eax, (%rdi)
```
because compiler has to consider that `a` and `b` point to same location in memory
(i.e. alias).  It generates expected code if both pointers are marked with `restrict`.

An equivalent Rust code:
```
#[no_mangle]
pub fn foo(a: &mut i32, b: &i32) {
    *a = *b + 1;
    *a += *b;
}
```
generates expected assembly
```
movl (%rsi), %eax
addl %eax, %eax
movl %eax, (%rdi)

```
because of language aliasing rules:
  - mutable reference can't alias anything

Interestingly enough for loops e.g.
```
void foo(int * RESTRICT a, const int * RESTRICT b, unsigned n) {
  for (unsigned i = 0; i < n; ++i)
    a[i] = b[i] + 100;
}
```
modern Clang will add a runtime aliasing check and
generate two versions of loop (GCC does not do this).

Other languages also have more strict aliasing guarantees
e.g. equivalent Fortran program
```
SUBROUTINE FOO(X, Y)
  INTEGER :: X, Y
  X = Y + 1
  X = X + Y
  RETURN
END
```
generates same code as Rust (but Fortran does not enforce
language rules so it's much easier to make a mistake).

# Optimizations

TODO:
  - how LLVM can use this info (and with what limitations e.g. only function params)
    * [relevant paper](https://www.cs.utexas.edu/~mckinley/papers/alias-cc-2004.pdf)
    * `llvm.experimental.noalias.scope.decl` may be relevant
  - A lot of [mentions](https://www.reddit.com/r/rust/comments/acjcbp/comment/ed8nkmj/) that
    `&mut Vec<T>` does not allow noalias for contained buffer and `&[T]` should be used instead.
    Need to investigate this.
  - Search for cases where alias info is not utilized
    (e.g. [here](https://blog.polybdenum.com/2017/02/19/how-copying-an-int-made-my-code-11-times-faster.html))

# Suggested readings

TODO:
  - links to important articles (design, etc.)

# Performance impact

TODO:
  - is this optimization is a common case in practice ?
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences
  - determine how to enable/disable feature in compiler/stdlib
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      - patch for each feature needs to be implemented in separate branch (in private compiler repo)
      - compiler modifications need to be kept in private compiler repo `yugr/rust-private`
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`

## Prevalence

TODO:
  - NoAlias returns from AA manager

## Measurements

### Static estimates

Following instructions for [bounds checks](../../cons/bounds-checks/analysis.md#static-estimates):

```
$ ./x setup
$ RUSTFLAGS_NOT_BOOTSTRAP='-Cllvm-args=-debug-only=licm,early-cse,gvn,loop-vectorize,SLP' ./x build -j1 --stage 2 compiler |& tee build.log

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
2213982 (-1.5%)
$ grep -c 'GVN removed' build.log
748188 (-6%)
$ grep -c 'EarlyCSE CSE' build.log
2202670 (-7%)
$ grep -c 'SLP: vectorized' build.log
25351 (+1%)
```

### Runtime improvements

Disabling the feature obviously decreases perf:
```
$ ../../benchmarks/compare.py baseline/ force-aliasing/
compare.py: warning: some results are present only in /home/Asus/src/rust-slides/tmp/results-20250826/baseline: meilisearch_0.json, veloren_0.json
SpacetimeDB_0.json: -0.7%
bevy_0.json: -0.1%
nalgebra_0.json: -4.5%
oxipng_0.json: +2.1%
rav1e_0.json: -1.0%
regex_0.json: -1.2%
ruff_0.json: -1.1%
rust_serialization_benchmark_0.json: -1.9%
tokio_0.json: -0.4%
uv_0.json: -1.0%
zed_0.json: -1.2%
```

TODO: perf measurements for AArch64

Largest speedups in oxipng are in
  - reductions_16_to_8_bits (28%)
  - filters_bigent (14%) - not reproduced
  - reductions_palette_8_to_grayscale_8 (9%)
  - reductions_rgba_to_grayscale_alpha_8 (8%)
  - reductions_rgb_to_grayscale_8 (7.5%)

There are also slowdowns but not as many:
  - filters_2_bits_filter_1 (5.6%)

#### reductions_16_to_8_bits

Update
```
#strip = "symbols"
debug = "line-tables-only"
```
in `Cargo.toml` and collect profile via
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
cargo bench --no-run -j1 reductions_16_to_8_bits
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

#### reductions_palette_8_to_grayscale_8 (also reductions_rgba_to_grayscale_alpha_8 and reductions_rgb_to_grayscale_8)

Profile data can be collected via
```
rm -f perf.data* && perf record -F99 target/release/deps/reductions-636692b0b03e7601 --bench reductions_palette_8_to_grayscale_8
```

Slowdown in `oxipng::reduction::color::indexed_to_channels` (or `oxipng::reduction::color::reduced_rgb_to_grayscale`).

Asm of hot loop is practically the same (modulo slightly different scheduling).
Perhaps alignment issue ?

The only noticeable difference in asm is presence of loop alignment in default (slow) case
so I suspect code alignment issues here. Default align on LLVM X86 is
```
setPrefLoopAlignment(Align(16));
```

If I disable it via
```
[target.x86_64-unknown-linux-gnu]
rustflags = ["-Cllvm-args=-align-loops=1"]
```
in `.cargo/config`, perf difference disappears (new binary becomes as slow as baseline).

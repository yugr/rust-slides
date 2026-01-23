# Administrivia

Assignee: zak

Parent task: gh-34

Effort: 0h

# Background

Rust has a very limited support of fast-math.
There is no `-ffast-math` flag to enable fast-math optimizations globally or at create/module/function level.
Rust has `std::intrinsics::XXX_algebraic` and `std::intrinsics::XXX_fast` intrinsics which allow fast-math optimization for a specific operations, however these intrinsics are currently unstable.
Lack of this feature has a significant impact on several domains such as gamedev:

> This particular feature is a real need within the game development community
> for obvious performance reasons. Usually we'd want this for hot-spot optimizations,
> however, it's also common to blanket enable -ffast-math for the entire (C++) game codebase.
>
> -- https://github.com/rust-lang/rust/issues/21690#issuecomment-1589427278

and computer vision:

> lack of even opt-in location-specific fast math (such as fadd_fast and fmul_fast)
> on stable hinders the use of Rust in some key algorithms for computer vision,
> robotics and augmented reality applications
>
> -- https://github.com/rust-lang/rust/issues/21690#issuecomment-1589427278

Rust developers have [clearly rejected](https://github.com/rust-lang/rust/issues/21690#issuecomment-1589427278) global fast math flag due to safety concerns (e.g. no clear way for a third-party crate to allow/disallow fast-math optimizations).

Other languages have different views on fast-math optimizations:

 - C/C++ standard prohibits fast-math optimizations, but compilers provide support for these optimizations
    - [C99](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1256.pdf) section 5.1.2.3 Example 5
 - C# permits performing computations with higher precision than the result type of the operation (most likely for performance on x87 architecture)
    - [C# specification](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/types#837-floating-point-types) section 8.3.7
 - At first Java required strict following of the IEEE 754 standard, but then some deviations were allowed to improve x87 performance
    - [Paper on the issue](https://arxiv.org/abs/cs/0701192) section 6
 - Go prohibits most fast-math optimizations, but allows fusion of floating-point operations if this fusion does not discard explicit rounding
    - [Go specification](https://go.dev/ref/spec#Floating_point_operators)
 - Swift compiler provides support for fast-math optimizations
    - [Godbolt example](https://godbolt.org/z/jqYfWoof5)
 - Fortran explicitly permits deviations from IEEE 754 in favor of performance
    - [Fortran specification](https://j3-fortran.org/doc/year/24/24-007.pdf) section 17.5

# Example

This simple loop is only vectorized when algebraic fast-math optimization is enabled. Without it, single scalar xmm instructions are used and only one value is processed per xmm calculation (4 double are processed per loop iteration due to unrolling). When compiler is allowed to change the order of computations, loop is vectorized in packs of 8 floats and one xmm calculation processes 2 double values (4 per loop iteration, but in 8 instructions vs 12 in baseline assembly).

## Source

```
use std::hint::black_box;
use std::cmp;

pub fn zipdot_checked_counted_loop() -> f64
{
    let xs = vec![0f64; 1024];
    let ys = vec![0f64; 768];
    let xs = black_box(xs);
    let ys = black_box(ys);

    let len = cmp::min(xs.len(), ys.len());
    let xs = &xs[..len];
    let ys = &ys[..len];

    let mut s = 0f64;

    for i in 0..len {
        let x = xs[i];
        let y = ys[i];
        s += x * y;
    }

    s
}
```

## x86 assembly, without fast-math optimizations

```
.LBB0_17:
	movsd	xmm2, qword ptr [rcx + 8*rsi]
	mulsd	xmm2, qword ptr [rdi + 8*rsi]
	movsd	xmm1, qword ptr [rcx + 8*rsi + 8]
	addsd	xmm2, xmm0
	mulsd	xmm1, qword ptr [rdi + 8*rsi + 8]
	addsd	xmm1, xmm2
	movsd	xmm2, qword ptr [rcx + 8*rsi + 16]
	mulsd	xmm2, qword ptr [rdi + 8*rsi + 16]
	addsd	xmm2, xmm1
	movsd	xmm0, qword ptr [rcx + 8*rsi + 24]
	mulsd	xmm0, qword ptr [rdi + 8*rsi + 24]
	lea	r8, [rsi + 4]
	addsd	xmm0, xmm2
	mov	rsi, r8
	cmp	rdx, r8
	jne	.LBB0_17
```

## x86 assembly, with algebraic fast-math optimizations

```
.LBB0_10:
	movupd	xmm2, xmmword ptr [rcx + r8]
	movupd	xmm3, xmmword ptr [rcx + r8 + 16]
	movupd	xmm4, xmmword ptr [rdi + r8]
	mulpd	xmm4, xmm2
	addpd	xmm0, xmm4
	movupd	xmm2, xmmword ptr [rdi + r8 + 16]
	mulpd	xmm2, xmm3
	addpd	xmm1, xmm2
	add	r8, 32
	cmp	rsi, r8
	jne	.LBB0_10
```

# Known performance hits

Most of the performance impact of a lack of fast-math optimizations comes from autovectorization problems. Efficient vectorization often requires reordering of operations, and it is not possible without at least algebraic level of fast-math optimizations.

# Enabling

There is no convenient way to globally enable fast math (see [this comment](https://github.com/rust-lang/rust/issues/21690#issuecomment-2167664644) for some reasons why).
`-C llvm-args=-ffast-math` has no impact on generated LLVM IR because `-ffast-math` is a clang frontend flag, so it has no impact when `rustc` is generating LLVM IR.
Furthermore, different options of fast-math optimizations are set in LLVM IR via flags, which apply to single floating-point operations (also phi-nodes, calls, returns).
Fast math attributes on functions are [in the process of being removed](https://github.com/llvm/llvm-project/issues/70533#issuecomment-1790250502) (or are already removed), so there LLVM IR also does not contain a way to "globally" enable fast-math optimizations.

Algebraic and fast-math optimizations can be enabled on per-operations basis by using `std::intrinsics::XXX_algebraic` and `std::intrinsics::XXX_fast`, however they are not yet stabilized.

Rust has `std::intrinsics::XXX_algebraic` and `std::intrinsics::XXX_fast` intrinsics which allow fast-math optimization for a specific operations, however these intrinsics are currently unstable.

# Recommended readings

- [rust-lang github issue](https://github.com/rust-lang/rust/issues/21690)
- [Fast-math dangers blogpost](https://simonbyrne.github.io/notes/fastmath/)
- [LLVM fast-math optimization flags](https://llvm.org/docs/LangRef.html#fast-math-flags)

# Performance with fast- and algebraic- math.

Compiler patches are in branches [zakhar/algebraic-math](https://github.com/yugr/rust-private/tree/zakhar/algebraic-math) and [zakhar/fast-math](https://github.com/yugr/rust-private/tree/zakhar/fast-math).

## x86_64

CPU:
```
$ lscpu
Architecture:                         x86_64
CPU op-mode(s):                       32-bit, 64-bit
Byte Order:                           Little Endian
Address sizes:                        46 bits physical, 48 bits virtual
CPU(s):                               24
On-line CPU(s) list:                  0-23
Thread(s) per core:                   2
Core(s) per socket:                   6
Socket(s):                            2
NUMA node(s):                         2
Vendor ID:                            GenuineIntel
CPU family:                           6
Model:                                63
Model name:                           Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz
Stepping:                             2
CPU MHz:                              2597.060
CPU max MHz:                          3200.0000
CPU min MHz:                          1200.0000
BogoMIPS:                             4794.66
Virtualization:                       VT-x
L1d cache:                            384 KiB
L1i cache:                            384 KiB
L2 cache:                             3 MiB
L3 cache:                             30 MiB
```

## Algebraic math

```
SpacetimeDB_0.json: -1.3%
bevy_0.json: -0.8%
meilisearch_0.json: -0.1%
nalgebra_0.json: -2.5%
oxipng_0.json: +0.4%
rav1e_0.json: -0.3%
regex_0.json: +0.2%
ruff_0.json: -0.0%
rust_serialization_benchmark_0.json: +0.1%
tokio_0.json: +0.5%
uv_0.json: -0.3%
veloren_0.json: +0.1%
zed_0.json: +0.4%
```

## Fast math

```
SpacetimeDB_0.json: -0.6%
bevy_0.json: +0.1%
meilisearch_0.json: -1.1%
nalgebra_0.json: -2.1%
oxipng_0.json: +0.6%
rav1e_0.json: -0.8%
regex_0.json: -0.4%
ruff_0.json: +0.3%
rust_serialization_benchmark_0.json: +0.2%
tokio_0.json: +0.2%
uv_0.json: -0.3%
veloren_0.json: +0.2%
zed_0.json: -0.3%
```

# Benchmark analysis

## Meilisearch

Meilisearch degradation did not reproduce on another machine, so is most likely caused by benchmarking noise.

## Nalgebra

`vec10000_dot_f32` is the most prominent regression, ~4 times, other benchmarks have not regressed more than 1.5 times.

### `vec10000_dot_f32`

Slows down significantly with fast-math. Vectorizer unrolls a tight loop, but is unable to optimize loads (does not use packed loads) and this results in an increase in I$ misses.
Initial loop seems hand-optimized to manually perform reassoc that the Rust compiler does not allow otherwise. This *might* have contributed to the autovectorization problems.

The benchmark's hot loop:

```
while self.nrows() - i >= 8 {
    acc0 += unsafe {
        conjugate(self.get_unchecked((i, j)).clone())
            * rhs.get_unchecked((i, j)).clone()
    };
    acc1 += unsafe {
        conjugate(self.get_unchecked((i + 1, j)).clone())
            * rhs.get_unchecked((i + 1, j)).clone()
    };
    acc2 += unsafe {
        conjugate(self.get_unchecked((i + 2, j)).clone())
            * rhs.get_unchecked((i + 2, j)).clone()
    };
    acc3 += unsafe {
        conjugate(self.get_unchecked((i + 3, j)).clone())
            * rhs.get_unchecked((i + 3, j)).clone()
    };
    acc4 += unsafe {
        conjugate(self.get_unchecked((i + 4, j)).clone())
            * rhs.get_unchecked((i + 4, j)).clone()
    };
    acc5 += unsafe {
        conjugate(self.get_unchecked((i + 5, j)).clone())
            * rhs.get_unchecked((i + 5, j)).clone()
    };
    acc6 += unsafe {
        conjugate(self.get_unchecked((i + 6, j)).clone())
            * rhs.get_unchecked((i + 6, j)).clone()
    };
    acc7 += unsafe {
        conjugate(self.get_unchecked((i + 7, j)).clone())
            * rhs.get_unchecked((i + 7, j)).clone()
    };
    i += 8;
}

res += acc0 + acc4;
res += acc1 + acc5;
res += acc2 + acc6;
res += acc3 + acc7;
```
> nalgebra/src/base/blas.rs


Baseline disassembly:
```
60:   movsd  -0x18(%r12,%rdi,4),%xmm5
      movsd  -0x10(%r12,%rdi,4),%xmm6
      movsd  -0x8(%r12,%rdi,4),%xmm7
      movsd  (%r12,%rdi,4),%xmm8
      movsd  -0x18(%r15,%rdi,4),%xmm9
      mulps  %xmm5,%xmm9
      addps  %xmm9,%xmm2
      movsd  -0x10(%r15,%rdi,4),%xmm5
      mulps  %xmm6,%xmm5
      addps  %xmm5,%xmm1
      movsd  -0x8(%r15,%rdi,4),%xmm5
      mulps  %xmm7,%xmm5
      addps  %xmm5,%xmm4
      movsd  (%r15,%rdi,4),%xmm5
      mulps  %xmm8,%xmm5
      addps  %xmm5,%xmm3
      add    $0x8,%rdi
      cmp    $0x2716,%rdi
      jne    60
```

Fast-math disassembly:
```
c0:   movss    -0x1c(%r12,%rdi,1),%xmm10
      movss    -0x3c(%r12,%rdi,1),%xmm11
      unpcklps %xmm10,%xmm11
      movss    -0x5c(%r12,%rdi,1),%xmm10
      movss    -0x7c(%r12,%rdi,1),%xmm13
      unpcklps %xmm10,%xmm13
      movlhps  %xmm11,%xmm13
      movss    -0x78(%r12,%rdi,1),%xmm14
      movss    -0x74(%r12,%rdi,1),%xmm12
      movss    -0x70(%r12,%rdi,1),%xmm10
      movss    -0x1c(%r15,%rdi,1),%xmm11
      movss    -0x3c(%r15,%rdi,1),%xmm15
      unpcklps %xmm11,%xmm15
      movss    -0x5c(%r15,%rdi,1),%xmm11
      movss    -0x7c(%r15,%rdi,1),%xmm0
      unpcklps %xmm11,%xmm0
      movlhps  %xmm15,%xmm0
      mulps    %xmm13,%xmm0
      addps    %xmm0,%xmm9
      movss    -0x78(%r15,%rdi,1),%xmm0
      movss    -0x74(%r15,%rdi,1),%xmm13
      movss    -0x70(%r15,%rdi,1),%xmm11
      movss    -0x18(%r12,%rdi,1),%xmm15
      movss    -0x38(%r12,%rdi,1),%xmm1
      unpcklps %xmm15,%xmm1
      movss    -0x58(%r12,%rdi,1),%xmm15
      unpcklps %xmm15,%xmm14
      movlhps  %xmm1,%xmm14
      movss    -0x18(%r15,%rdi,1),%xmm1
      movss    -0x38(%r15,%rdi,1),%xmm15
      unpcklps %xmm1,%xmm15
      movss    -0x58(%r15,%rdi,1),%xmm1
      unpcklps %xmm1,%xmm0
      movlhps  %xmm15,%xmm0
      mulps    %xmm14,%xmm0
      addps    %xmm0,%xmm8
      movss    -0x14(%r12,%rdi,1),%xmm0
      movss    -0x34(%r12,%rdi,1),%xmm1
      unpcklps %xmm0,%xmm1
      movss    -0x54(%r12,%rdi,1),%xmm0
      unpcklps %xmm0,%xmm12
      movlhps  %xmm1,%xmm12
      movss    -0x14(%r15,%rdi,1),%xmm0
      movss    -0x34(%r15,%rdi,1),%xmm1
      ...
```

### `lu_determinant_100x100`

Here the disassembly shows that in the baseline the hot loop was not vectorized, all operations are scalar. Allowing reassociation results in vectorization ("packed" instruction are used).

Baseline disassembly:
```
120:   mulsd  (%rsi,%rdx,1),%xmm2
       mulsd  (%rsi,%r14,1),%xmm2
       mulsd  (%rsi,%r13,1),%xmm2
       add    $0x4,%r15
       mulsd  (%rsi,%rbx,1),%xmm2
       add    %r12,%rbx
       add    %r12,%r13
       add    %r12,%rdx
       add    %r12,%r14
       cmp    %r15,%r10
       jne    120
```

Fast math disassembly:
```
150:   movsd    (%rsi,%r15,1),%xmm5
       movhpd   (%rsi,%r14,1),%xmm5
       mulpd    %xmm5,%xmm3
       movsd    (%rsi,%rbx,1),%xmm5
       movhpd   (%rsi,%r12,1),%xmm5
       mulpd    %xmm5,%xmm4
       add      %r13,%r15
       add      %r13,%r12
       add      %r13,%rbx
       add      %r13,%r14
       add      $0xfffffffffffffffc,%r11
       jne      150
```




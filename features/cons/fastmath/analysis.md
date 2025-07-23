# Nalgebra

## `vec10000_dot_f32`

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

## `lu_determinant_100x100`

Here the disassembly shows that the hot loop was not vectorized, all operations are scalar. Allowing reassociation results in vectorization ("packed" instruction are used).

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


# Enabling 

There is no convenient way to globally enable fast math (see [this comment](https://github.com/rust-lang/rust/issues/21690#issuecomment-2167664644) for some reasons why).
`-C llvm-args=-ffast-math` has no impact on generated LLVM IR because `-ffast-math` is a clang frontend flag, so it has no impact when `rustc` is generating LLVM IR.
Furthermore, different options of "fast math" optimizations are set in LLVM IR via flags, which apply to single floating-point operations (also phi-nodes, calls, returns).
Fast math attributes on functions are [in the process of being removed](https://github.com/llvm/llvm-project/issues/70533#issuecomment-1790250502) (or are already removed), so there LLVM IR also does not contain a way to "globally" enable "fast math" optimizations.


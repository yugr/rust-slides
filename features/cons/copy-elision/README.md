Rust does not always perform move/copy elision.

Rust copies/moves are side-effect-free (have "no user-visible
effects") so it does not need special copy-elision rules
like C++. So in theory compiler is capable of
removing all redundant `memcpy`'s.
E.g. Rust had (N)RVO since day one.

E.g. C++ code like
```c++
#include <utility>

class A {
public:
  A(A &&);
  A(const A &);
};

void sink(const A &);

void mov(A a) {
  A a1 = std::move(a);
  A a2 = std::move(a1);
  sink(a2);
}

void cpy(A a) {
  A a1(a);
  A a2(a1);
  sink(a2);
}
```
is not optimized by Clang/GCC whereas equivalent Rust code contains just 1 `memcpy` :
```rust
use std::hint::black_box;

#[derive(Clone)]
pub struct A {
  pub data: [i32; 1024],
}

pub fn mov(a: A) {
    let a = a;
    let a = a;
    black_box(&a);
}

pub fn cpy(a: A) {
    let a = a.clone();
    let a = a.clone();
    black_box(&a);
}
```
(compile via `rustc -O --emit asm --crate-type=lib repro.rs -o- | c++filt`).

Function returns and parameter passing also do not generate `memcpy` :
```
use std::hint::black_box;

#[derive(Clone)]
pub struct A {
  pub data: [i32; 1024],
}

extern "C" {
    fn foo() -> A;
}

pub fn param(a: A) {
    black_box(&a);
}

pub fn ret() -> A {
    unsafe { foo() }
}
```

On the other hand in many other cases Rust keeps spurious `memcpy`'s
e.g. in
```
use std::hint::black_box;

#[derive(Clone)]
pub struct A {
  pub data: [i32; 1024],
}

pub fn mov(a: A) {
    let a = a;
    black_box(&a);
}
```
The reason is that LLVM is not always good at optimizing `memcpy`
so Rust has [custom optimization passes](https://github.com/rust-lang/rust/blob/master/compiler/rustc_mir_transform/src/dest_prop.rs) to deal with them.
This work is [ongoing](https://github.com/rust-lang/rust/labels/A-mir-opt-nrvo)
e.g. [#91521](https://github.com/rust-lang/rust/issues/91521) has been fixed.

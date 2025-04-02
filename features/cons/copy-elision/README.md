Rust does not always perform move/copy elision.

This is actually similar to C++ : code like
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
is not optimized either.

Equivalent Rust code contains just 1 `memcpy` :
```
use std::hint::black_box;

#[derive(Clone)]
pub struct A {
  pub data: [i32; 1024],
}

pub fn mov(a: A) {
    let a1 = a;
    let a2 = a1;
    black_box(&a2);
}

pub fn cpy(a: A) {
    let a1 = a.clone();
    let a2 = a1.clone();
    black_box(&a2);
}
```
(compile via `rustc -O --emit asm --crate-type=lib repro.rs -o- | c++filt`).

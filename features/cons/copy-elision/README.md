Rust does not always perform move/copy elision.

Rust copies/moves are sife-effect free so it does not need
special copy-elision rules like C++. So in theory compiler
is capable of removing all redundant `memcpy`'s.

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

Unfortunately in some cases Rust still generates redundant `memcpy`'s
(e.g. why there is one in program above ?).

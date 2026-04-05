It's generally easier to elide moves in Rust
(than in C++) because a move (and copy, for copyable types)
is just a `memcpy` (a single instruction in LLVM IR)
so much easier to optimize in middle-end's LLVM memcpy optimizer.

Rust has _destructive_ moves i.e. destructor of moved object is not called afterwards.

Rust copies/moves are side-effect-free (have "no user-visible
effects") so it does not need special copy-elision rules
like C++. So in theory compiler is capable of
removing all redundant `memcpy`'s.
E.g. Rust had (non-guaranteed) (N)RVO since day one.

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

[copyless](https://github.com/kvark/copyless) trait has been removed
because situation w/ `memcpy`'s has been significantly improved.

Copies (`clone`'s) are present in high-level IR (MIR)
and also can be optimized but currently aren't.

# Problems

Rust does not always perform move/copy elision.

In many cases Rust keeps spurious `memcpy`'s esp. on function bondary:
```
use std::hint::black_box;

#[derive(Clone)]
pub struct A {
  pub data: [i32; 1024],
}

pub fn mov(a: A) {
    black_box(a);
}
```

Another common problem is [spurious moves in fold](https://github.com/rust-lang/rust/issues/76725).

The reason is that LLVM is not always good at optimizing `memcpy`
so Rust has [custom optimization passes](https://github.com/rust-lang/rust/blob/master/compiler/rustc_mir_transform/src/dest_prop.rs) to deal with them.
This work is [ongoing](https://github.com/rust-lang/rust/labels/A-mir-opt-nrvo)
e.g. [#91521](https://github.com/rust-lang/rust/issues/91521) has been fixed
and [#32966](https://github.com/rust-lang/rust/issues/32966)
and [#79914](https://github.com/rust-lang/rust/issues/79914) haven't.
Some info on why this may happen can be found in [#103172](https://github.com/rust-lang/rust/pull/103172).

There is a [proposal](https://rust-lang.github.io/rust-project-goals/2025h2/mir-move-elimination.html)
to optimize moves at MIR level.

# Solutions

Pass large structs (or [fold accumulators](https://github.com/rust-lang/rust-clippy/issues/6053)) by reference.

Enable additional MIR opts (does not help with case above though):
  - `-Zmir-enable-passes=+DestinationPropagation,+RenameReturnPlace`
  - `-Zmir-opt-level=4`
  - (may need to prepend `-Zunsound-mir-opts`)

(does not help in all cases).

# Examples

- [Example 1](https://www.reddit.com/r/rust/comments/px72r1/comment/hem26o0/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
- [Example 2](https://www.reddit.com/r/rust/comments/px72r1/comment/heqmrjh/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
- [Cost of copies in large C++ codebase](https://groups.google.com/a/chromium.org/g/chromium-dev/c/EUqoIz2iFU4/m/kPZ5ZK0K3gEJ)
- [#116541](https://github.com/rust-lang/rust/issues/116541)
  * optimization is done not by Rust (so `-Zmir-enable-passes=-DestinationPropagation,-RenameReturnPlace,-CopyProp`
    indeed do not help) but by LLVM InstCombine which eliminates dead copy
  * in latest release (1.92) code is optimized (by LLVM) if I remove one level
    of copying (Outer -> LargeStruct) and `d4` or just remove all `di` fields
    but keeps failing otherwise
  * just inlining all functions into main does not matter in 1.92
    (the issue remains until I remove `d2`-`d4` fields)
  * unable to debug further because test fails on nightly
  * looks like an issue with some threshold in InstCombineLoadStoreAlloca.cpp

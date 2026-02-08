# Administrivia

Assignee: yugr

Parent task: gh-37

Effort: 3.5h

# Background

In some situations (particularly when working with containers)
programmer needs to initialize objects at arbitrary address.
A straightforward way to do this is to construct a local object
on stack and then put it into the container.
The disadvantage of this approach is extra empty ctor
(to construct object to assign to) and copy ctor to assign it (a memcpy).
In some cases extra large objects may even crash app (due to stack overflow).

C++ has dedicated operator (_placement new_) to invoke ctor inplace at arbitrary address:
```
void *addr = some_alloc(sizeof(A));
A *ptr = new(addr) A(...);
```
(newer C++ versions also have `std::construct_at`).
This feature is crucial for emplace operators in std containers
(e.g. `std::vector::emplace_back`) but also to efficiently
construct smart pointers.

Rust does not have any language mechanism to force placement new
(there used to be `box` keyword for `Box` inits but no more).
Programmers have to rely on compiler to optimize away redundant memcpy's
in code like
```
let b = Box::new(LargeStruct { ... });
```
(so called "guaranteed copy elision") or
use dedicated APIs provided (or not) by each containers (see below)
Unfortunately compilers do not always manage to optimize even simplest cases
(or at least not reliably across versions and also not in debug) and
APIs may not always be provided.

This effectively means that one
> cannot create a struct that is bigger than the stack allows and
> it will always be created on the stack first and then copied to the heap
(from [here](https://users.rust-lang.org/t/how-to-create-large-objects-directly-in-heap/26405/2)).

There have been some RFCs about adding support for placement new
(e.g. [this](https://y86-dev.github.io/blog/return-value-optimization/placement-by-return.html)
or [this](https://github.com/rust-lang/rust/issues/27779))
but according to [this](https://www.reddit.com/r/rust/comments/1eeuqtc/c_vectoremplace_back_vs_rust_vecpushf_copying_v/)
there is nothing officially accepted.
Maintainers consider it [a low priority feature](https://www.reddit.com/r/rust/comments/1eeuqtc/comment/lfhqob6/).

Java and C# objects/arrays are always allocated in heap so
issue with stack overflow is irrelevant for them.
Similarly Golang controls all memory allocations
(and does them in heap or stack depending on liveness).
Ada supports [storage pools](https://www.adacore.com/blog/header-storage-pools).
Swift provides [UnsafeMutablePointer API](https://stackoverflow.com/a/27721441/2170527)
similar to Rust.

TODO: inplace initialization is [2026 project goal](https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html)

# Example

This C++ code
```
#include <vector>
#include <algorithm>

struct A {
  static constexpr size_t N = 1024;
  int vals[N] = {};

  A() = default;
  A(const A &) = default;

  A(int val) {
    std::fill(&vals[0], &vals[N], val);
  }
};

#define NITER 1024 * 1024

int main() {
  std::vector<A> aa;
  aa.reserve(NITER);

  for (size_t i = 0; i < NITER; ++i) {
#ifdef USE_PLACEMENT_NEW
    aa.emplace_back(i);
#else
    A a(i);
    aa.push_back(a);
#endif

    asm("" :: "r"(&aa) : "memory");
  }

  return 0;
}
```
is ~10% faster when using placement new:
```
$ g++ -O2 tmp33.cpp && for i in `seq 1 5`; do time ./a.out; done |& grep user
user    0m1.279s
user    0m1.056s
user    0m1.087s
user    0m1.193s
user    0m1.241s

$ g++ -O2 -DUSE_PLACEMENT_NEW tmp33.cpp && for i in `seq 1 5`; do time ./a.out; done |& grep user
user    0m1.118s
user    0m1.028s
user    0m1.060s
user    0m0.933s
user    0m0.932s
```

Similar example for Rust:
```
use std::hint::black_box;

const SIZE: usize = 1024 * 1024 * 1024;

fn main() {
    let b: Box<[usize]> = if cfg!(fast) {
        vec![15; SIZE].into_boxed_slice()
    } else {
        Box::new([15; SIZE])
    };
    black_box(&b);
}
```
fails when relying on compiler:
```
$ SIZE=$((8 * 1024))
$ rustc +baseline -O test.rs
$ (ulimit -s $SIZE; ./test)
thread 'main' has overflowed its stack
fatal runtime error: stack overflow
```
but works with dedicated API:
```
$ rustc +baseline --cfg fast -O test.rs
$ (ulimit -s $SIZE; ./test)
```

# Optimizations

Same as [copy elision feature](../copy-elision).

# Workarounds

Containers provide APIs to either construct uninitialized elements
(e.g. `Box/Rc::new_uninit` or `Vec::with_capacity/set_len`), convert objects to containers (e.g. `Vec::into_boxed_slice`)
or construct new elements w/ closures (e.g. `Vec::resize_with/fill_with`).

Note that the latter increases the chance for copy elision but still does no guarantee it.
For example this code
```
use std::hint::black_box;

const SIZE: usize = 1024 * 1024 * 1024;
const N: usize = 1;

struct MyStruct {
    data: [usize; SIZE],
}

fn main() {
    let mut v = Vec::<MyStruct>::with_capacity(N);
    if cfg!(uninit) {
        // This is UB but ok for test
        unsafe { v.set_len(N); }
    } else if cfg!(fast) {
        v.resize_with(N, || MyStruct { data: [15; SIZE] });
    } else {
        for _ in 0..N {
            let tmp = MyStruct { data: [15; SIZE], };
            v.push(tmp);
        }
    }
    black_box(&v);
}
```
works without initialization:
```
$ SIZE=$((8 * 1024))  # 8M
$ rustc +baseline --cfg uninit -O test.rs
$ (ulimit -s $SIZE; ./test)
```
but fails both w/ `resize_with` and default approach:
```
$ rustc +baseline --cfg fast -O test.rs
$ (ulimit -s $SIZE; ./test)
thread 'main' has overflowed its stack
fatal runtime error: stack overflow

$ rustc +baseline -O test.rs
$ (ulimit -s $SIZE; ./test)
thread 'main' has overflowed its stack
fatal runtime error: stack overflow
```

# Suggested readings

TODO:
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)

# Performance impact

## Prevalence

We could do a Valgrind checker that detect situations like
  - `memcpy` copies stack buffer to heap (need to compile w/ `-fno-builtin`)
  - resulting heap buffer used in `Vec::push`, `Box::new`, etc.
  - stack data overwritten later without ever being used again

This could serve as upper bound on number of missing copy elisions in placement new.

TODO: implement this checker (gh-53)

## Disabling the check

N/A

## Measurements

N/A

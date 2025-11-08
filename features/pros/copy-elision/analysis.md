# Administrivia

Assignee: yugr

Parent task: gh-32

Effort: 2h

TODO: fix all TODOs that are mentioned in feature's README

# Background

We call this feature "copy elision" in parallel to C++
but it's in fact a "move/copy elision" because
moves are much more prevalent in Rust and more
amenable to optimization.

It's one example where Rust's default choice (assignments move, not copy)
improves optimizations: move is just a `memcpy` underneath and
is much easier to reason about in LLVM and MIR passes (to remove it).
Also it allows compiler to not call destructor for moved object
(unlike in C++, where moving keeps source object in valid state and
requires destructor).

This feature enables compiler to optimize assignments, parameter passing
and returning values much more aggressively, both in MIR and LLVM transforms.
Optimization is of course best-effort (i.e. not guaranteed).

Elision is also applied to copies with some caveats:
  - there is a special `Copy` marker trait which says that object
    should be copied instead of moved but copy is shallow
    (i.e. just a `memcpy`); it behaves the same way for optimizations,
    only does not destruct the source of assignment
  - non-trivial copies (called "clones" in Rust) need to be done explicitly
    via `.clone()` method; such copies behave like C++ ones: they are
    _not_ optimized at MIR level but can be optimized by LLVM

C++ has a bunch of similar rules: RVO, NRVO and copy elision but
they are not mandatory and only performed with best effort.
E.g. copy elisions are not performed at all because
C++ compiles don't do high-level opts (there is Clang IR project
but it's future is unclear due to large compile-time overheads).

Most other languages (Java, Julia, Python) do not have copy elision
because there is no value semantics for non-primitive types.

TODO:
  - situation in Swift and C#

# Examples

Here is a simple example where Rust clearly wins.

This C++ code
```
#include <utility>

class A {
public:
  A(A &&);
};

A foo(A a0) {
  A a1(std::move(a0));
  A a2(std::move(a1));
  A a3(std::move(a2));
  A a4(std::move(a3));
  A a5(std::move(a4));
  return a5;
}
```
compiles] into 5 function calls to copy constructors
([tested](https://godbolt.org/z/bG1K6e3ns) on GCC 15.2 and Clang 21).

An equivalent Rust code
```
pub struct A {
    data: [u8; 1024],
}

pub fn foo(a0: A) -> A {
    let a1 = a0;
    let a2 = a1;
    let a3 = a2;
    let a4 = a3;
    let a5 = a4;
    a5
}
```
has just one `memcpy`.

It could be argued that code is not _quite_ identical because
definition of `A::A(A &&)` is not available but consider that 
it's simply not inlined by inliner due to some threshold.

# Optimizations

TODO:
  - info whether MIR opts can optimize it (moves, copies and clones)
  - info whether LLVM can potentially optimize it (and with what limitations)

# Workarounds

TODO:
  - info on how developer can work around it and with how much effort/ugliness (unsafe, wrapping operations, reslicing, etc.)
    * pay special attention to cases which can not be optimized at all

# Suggested reading

TODO:
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)

# Performance impact

## Prevalence

TODO:
  - is this check is a common case in practice ?
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences

## Disabling the check

TODO:
  - determine how to enable/disable feature in compiler/stdlib
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      + patch for each feature needs to be implemented in separate branch (in private compiler repo)
      + compiler modifications need to be kept in private compiler repo `yugr/rust-private`
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`

## Measurements

TODO:
  - collect perf measurements for benchmarks:
    * runtime
    * code size
    * standard compiler stats (inline, CSE/GVN/LICM, SLP/loop autovec)

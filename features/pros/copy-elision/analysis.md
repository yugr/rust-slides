# Administrivia

Assignee: yugr

Parent task: gh-32

Effort: 15h

# Background

We call this feature "copy elision" in parallel to C++
but it's in fact a "move/copy elision" because
moves are much more prevalent in Rust and more
amenable to optimization.

It's one example where Rust's default choice (assignments move, not copy)
improves optimizations: move is just a `memcpy` underneath
(even move of array of objects) and is much easier to reason about in LLVM
and MIR passes (to remove it).
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
it's simply not inlined by inliner due to some threshold
(or resides in another module).

# Optimizations

The general understanding is that LLVM alone is incapable of
optimizing all cases (see comments in dest\_prop.rs) so
MIR has several passes to deal with copy elision:
  - CopyProp (copy\_prop.rs)
  - DeadStoreElimination (dead\_store\_elimination.rs)
  - DestinationPropagation (dest\_prop.rs)
  - RenameReturnPlace (nrvo.rs)
    * not in latest, likely replaced with DestinationPropagation

It handles moves and copies (and `clone`'s).
Tracking issue for MIR copy elision is
[#32966](https://github.com/rust-lang/rust/issues/32966).

For cases where MIR fails (e.g. [#116541](https://github.com/rust-lang/rust/issues/116541)),
LLVM has a dedicated pass to optimize `memcpy`
(and other memory intrinsics): MemCpyOptPass. It performs, among other things,
copy propagation over `memcpy`'s. Also DSEPass can remove dead `memcpy`'s.

The main limitation for MIR opts seems to be lack of tracking across "projections":
```
//! There are a number of ways in which this pass could be improved in the future:
...
//! * Allow merging locals into places with projections, eg `_5` into `_6.foo`.
```
(from dest\_prop.rs). E.g. in this case
```
const SIZE: usize = 1024 * 1024 * 1024;

pub struct LargeStruct {
    huge: [u8; SIZE],
}

pub fn foo() -> Box<LargeStruct> {
    let a0 = LargeStruct { huge: [0; SIZE] };
    let a1 = a0;
    let a2 = a1;
    Box::new(a2)
}
```
all `ai`'s are eliminated but copies to `LargeStruct` and `Box` are not.

Also if address of variable is taken it's copy isn't elided by Rust:
```
pub fn foo() -> LargeStruct {
    let a0 = LargeStruct { huge: [0; SIZE] };
    let a1 = a0;
    std::hint::black_box(&a1);
    let a2 = a1;
    a2
}
```

TODO: better move elision in MIR is [2026 project goal](https://rust-lang.github.io/rust-project-goals/2025h2/mir-move-elimination.html)

# Workarounds

C++ has several workarounds for lack of copy elision e.g.
  - placement new
  - perfect forwarding (e.g. `emplace_back`)

but Rust does not have similar language features so
(currently) developers have to rely solely on compiler.
Simple cases like
```
vec.push(LargeStruct { ... });
Box::new(LargeStruct { ... });
```
are already optimized and some containers provide unsafe APIs
for `emplace_back`-like functionality (e.g. `Box::new_uninit` or
`Vec::split_at_spare_mut`).

Another problem is that optimizations happen only in optimized version
so debug version of program will segfault due to stack overflow.

More details on placement-new are available [here](../../cons/placement-new/README.md).

# Suggested reading

TODO:
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)

# Performance impact

Unfortunately it's not clear how to measure prevalence/benefit of this feature or
compare it against C++.

We can only suspect that redundant copies have high costs with some
[anecdotal evidence](https://groups.google.com/a/chromium.org/g/chromium-dev/c/EUqoIz2iFU4/m/kPZ5ZK0K3gEJ)
and the fact that full (i.e. non-mandatory) copy elision optimization does not exist in any production compiler
See e.g. how it's limited in [Visual Studio](https://devblogs.microsoft.com/cppblog/improving-copy-and-move-elision/).
Also in this simple example
```
#include <vector>
#include <optional>

struct Big {
  long data[1 << 20];
};

std::optional<Big> foo(std::vector<Big> &v) {
  auto ans = v.back();
  v.pop_back();
  return ans;
}
```
GCC generates two `memcpy`'s whereas equivalent Rust code
```
pub struct Big {
    pub data: [usize; 1 << 20],
}

pub fn foo(v: &mut Vec<Big>) -> Option<Big> {
    v.pop()
}
```
has just one (Clang has single `memcpy` but it's unrelated to LLVM optimizer -
Rust generates LLVM IR with single `memcpy`).

Aggressive use of `auto` (without `&`) also [adds](https://medium.com/@rogerbooth/c-gotcha-unnecessary-copies-due-to-the-misuse-of-auto-ed24e65b5efd)
to copy overheads in C++.

Situation may change if [ultimate_copy_elision](https://github.com/cpp-ru/ideas/issues/256)
is finished (see also [Настоящее и будущее copy elision](https://assets.ctfassets.net/oxjq45e8ilak/2eGPH36FWGYOPN2dgTom47/eb317b89aab933d9f28a367a7dcb1083/Roman_Rusyayev_Anton_Polukhin_Nastoyashcheye_i_budushcheye_copy_elision_2020_06_28_15_51_59.pdf)).

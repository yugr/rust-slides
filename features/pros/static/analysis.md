# Administrivia

Assignee: yugr

Parent task: gh-50

Effort: 10h

# Background

Functions which are local in translation unit (aka static or internal)
can be [more aggressively](https://web.archive.org/web/20240309202636/https://embeddedgurus.com/stack-overflow/2008/12/efficient-c-tips-5-make-local-functions-static/)
optimized by compiler:
  - ABI-violating optimizations (e.g. [IPRA](https://reviews.llvm.org/D23980))
  - change calling convention (to `coldcc` or `fastcc`, see `Transforms/IPO/GlobalOpt.cpp`)
  - more aggressive inlining (e.g. it's always beneficial to inline static function called once)
  - propagating constant arguments (IPSCCP)
  - promote by-ref arguments to by-val (ArgumentPromotion)
  - remove dead argument/return value (DeadArgumentElimination)
  - better alias analysis (GlobalsAA)
  - dead code elimitation
  - merge global constants (ConstantMerge)

For shared libraries global functions are also exported from library by default
which slows down startup and make calls to them go through GOT/PLT
(unless [special care is taken](https://github.com/yugr/CppRussia/blob/master/2024/EN.pdf) about visibility).

In C/C++ functions are public by default and need to be localized explicitly
(via `static` or anon. namespaces). This is called internal linkage.
Many high-profile coding styles require this e.g.
[Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html#Internal_Linkage),
[LLVM Coding Standard](https://llvm.org/docs/CodingStandards.html#id59) ("Restrict Visibility"),
[C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#rs-unnamed2),
[Chromium C++ Style Guilde](https://chromium.googlesource.com/chromium/src/+/main/styleguide/c++/c++.md#unnamed-namespaces).
One problem in C++ is that there internalization is done at class level so
there is no way to localize just some methods (esp. `private` methods,
see some preliminary work [here](https://github.com/yugr/llvm-project/commits/yugr/internal-private/2/))
except factoring them out to anon. namespaces.

In Rust functions are local by default and need to be published explicitly
via `pub` keyword. Note that `pub(crate/super/self)`
just control visibility within crate and do not publish a symbol
(unless it's explicitly re-exported via `pub use`):
```
$ cat test.rs
#[inline(never)]  // Simulate inliner fail
pub(crate) fn foo1(x: i32) {
    println!("Hello world {}", x);
}

mod mymod {
    #[inline(never)]  // Simulate inliner fail
    pub(super) fn foo2(x: i32) {
        println!("Goodbye world {}", x);
    }

    #[inline(never)]  // Simulate inliner fail
    pub fn foo3(x: i32) {
        println!("Nice world {}", x);
    }
}

pub use mymod::foo3;

pub fn bar() {
    foo1(1);
    mymod::foo2(2);
    mymod::foo3(3);
}

$ rustc +baseline test.rs -O --emit=asm --crate-type=rlib -o- | g globl
        .globl  _ZN5tmp415mymod4foo317he25c12b2983ea8d0E
        .globl  _ZN5tmp413bar17h1647cdb4897d4b54E
```

C# has `internal` specifier but there is no info if it can improve performance.
Swift functions need to be internalized explicitly via `private`.
In Go developer is forced to choose whether function is internal (starts w/ lowercase)
or public (starts w/ uppercase). Fortran functions are external by default.

# Examples

This Rust code
```
#[inline(never)]  // Simulate inliner fail
fn foo(b: bool, seed: i32, s: &[i32]) -> i32 {
    let mut ans = seed;
    for &x in s {
        ans += if b { 1 } else { ans ^ x }
    }
    ans
}

pub fn bar(n: i32, s: &[i32]) -> i32 {
    let mut ans = 0;
    for i in 0..n {
        ans += foo(true, i, s);
    }
    ans
}
```
compiles to
```
$ rustc +baseline test.rs -O --emit=asm --crate-type=rlib -o-
        .file   "tmp39.a753e57b1e183dcd-cgu.0"
        .section        .text._ZN5tmp393foo17h2c99de230f997c95E,"ax",@progbits
        .p2align        6
        .type   _ZN5tmp393foo17h2c99de230f997c95E,@function
_ZN5tmp393foo17h2c99de230f997c95E:
        .cfi_startproc
        leal    (%rsi,%rdi), %eax
        retq
...
```
Two things can be noticed here:
  - ABI of foo was optimized (third argument removed)
  - loop was completely eliminated from foo

Both optimizations would not have been possible if `foo` were not static
as can be seen for this seemingly equivalent C++ code:
```
#include <vector>

__attribute__((noinline))  // Simulate inliner fail
int foo(bool b, int seed, const std::vector<int> &s) {
  int ans = 0;
  for (auto x : s)
    ans += b ? 1 : (ans ^ x);
  return ans;
}

int bar(int n, const std::vector<int> &s) {
  int ans = 0;
  for (int i = 0; i < n; ++i)
    ans += foo(true, i, s);
   return ans;
}
```
compiler generates
```
$ clang++ -O2 -S -o- tmp39.cpp
        .text
        .file   "tmp39.cpp"
        .globl  _Z3foobiRKSt6vectorIiSaIiEE     # -- Begin function _Z3foobiRKSt6vectorIiSaIiEE
        .p2align        4, 0x90
        .type   _Z3foobiRKSt6vectorIiSaIiEE,@function
_Z3foobiRKSt6vectorIiSaIiEE:            # @_Z3foobiRKSt6vectorIiSaIiEE
        .cfi_startproc
# %bb.0:
        movq    (%rdx), %rcx
        movq    8(%rdx), %rdx
        cmpq    %rdx, %rcx
        je      .LBB0_1
# %bb.3:
        xorl    %esi, %esi
        movl    $1, %r8d
        .p2align        4, 0x90
.LBB0_4:                                # =>This Inner Loop Header: Depth=1
        movl    (%rcx), %eax
        xorl    %esi, %eax
        testb   %dil, %dil
        cmovnel %r8d, %eax
        addl    %esi, %eax
        addq    $4, %rcx
        movl    %eax, %esi
        cmpq    %rcx, %rdx
        jne     .LBB0_4
# %bb.2:
        retq
.LBB0_1:
        xorl    %eax, %eax
        retq
...
```
(code optimizes fine if we add `static` to `foo`).

# Optimizations

In theory compiler can perform similar optimizations through
  - function cloning
    (Attributor pass does this under `-mllvm -attributor-allow-deep-wrappers`)
  - determine internalizability at LTO link time
    (both fat and thin LTO do this, see calls to `internalizeModule`)
    but this can't be trivially done for shlibs (because all symbols
    are exported by default)

# Suggested reading

N/A

# Performance impact

## Disabling optimization

We disable static functions by converting them to globals with unique prefix
in [attached patch](0001-Remove-internal-functions.patch).  It also collects stats.

## Prevalence

Counts for Rust benchmarks were obtained with
Rust's llvm-project with aboev patch:
```
$ INTERNAL_STATS=1 ../benchmarks/runall.sh --runner-args "-b -j6 -v" no-static
$ csplit -z results/no-static/runner.log '/^Building /' '{*}'
$ for f in xx*; do
    name=$(head -n1 $f | awk '{print $2}')
    echo $name
    ./parse_stats.sh < $f
  done
SpacetimeDB...
839580 205050 80.371
bevy...
1266724 248484 83.6007
meilisearch...
1720897 55972 96.85
nalgebra...
110556 21742 83.5659
oxipng...
54242 13332 80.2705
rav1e...
96786 18072 84.2658
regex...
14954 3050 83.0593
ruff...
684568 152539 81.7778
rustc-runtime-benchmarks...
240663 52169 82.1847
rust_serialization_benchmark...
233682 69422 77.0963
tokio...
258060 54343 82.6048
uv...
981092 184816 84.1483
veloren...
1373325 353288 79.5387
zed...
1927025 103508 94.9024
```

Rustc stats:
```
$ ./x build -j12 library
$ INTERNAL_STATS=1 ./x build -j1 --stage 2 compiler |& tee build.log
$ ./parse_stats.sh < build.log
1270712 281931 81.8419
```

For some C/C++ projects the numbers are on par
(all measurements were done with llvmorg-20.1.7 Clang with the above patch).
For example x264 (0480cb05) stats are similar:
```
$ PREFIX=$HOME/src/llvm/remove-internals/build
$ CC=$PREFIX/bin/clang ../configure --prefix=$HOME/src/x264/install --enable-static --enable-shared
$ INTERNAL_STATS=1 make -j4 |& tee make.log
$ make install
$ ./parse_stats.sh < make.log
1823 501 78.4423
```
and ffmpeg 8.0.1 too:
```
$ PKG_CONFIG_PATH=$HOME/src/x264/install/lib/pkgconfig ~/src/ffmpeg-8.0.1/configure --cc=$PREFIX/bin/clang --cxx=$PREFIX/bin/clang++ --extra-cflags='-O2 -DNDEBUG' --extra-cxxflags='-O2 -DNDEBUG' --enable-libx264 --enable-gpl
$ INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
35817 4015 89.9202
```
and git 2.52.0:
```
$ CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ ./configure
$ INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
10868 3542 75.4198
```
and bitcoin v30.2:
```
$ cmake -B build -DCMAKE_C_COMPILER=$PREFIX/bin/clang -DCMAKE_CXX_COMPILER=$PREFIX/bin/clang++ -DENABLE_IPC=OFF
$ INTERNAL_STATS=1 make -C build -j4 |& tee make.log
$ ./parse_stats.sh < make.log
27532 4547 85.8256
```
and opencv 4.12.0:
```
$ cmake -B build -DCMAKE_C_COMPILER=$PREFIX/bin/clang -DCMAKE_CXX_COMPILER=$PREFIX/bin/clang++
$ INTERNAL_STATS=1 make -C build -j4 |& tee make.log
$ ./parse_stats.sh < make.log
146600 22938 86.4703
```
and clang llvmorg-20.1.7:
```
$ cmake -G Ninja -DCMAKE_C_COMPILER=$PREFIX/bin/clang -DCMAKE_CXX_COMPILER=$PREFIX/bin/clang++ -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG' -DCMAKE_EXE_LINKER_FLAGS= -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS=clang ../llvm
$ INTERNAL_STATS=1 ninja -j4 |& tee make.log
$ ./parse_stats.sh < make.log
425733 61557 87.3675
```

For other projects numbers are dramatically worse e.g.
openssl 3.6.0 has worse numbers (but this may be because of code style):
```
$ PATH=$PREFIX/bin:$PATH
$ ../config linux-x86_64-clang
$ INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
25014 21927 53.2882

# 308 symbols unused according to Localizer (678 if headers ignored)
$ ../config linux-x86_64
$ find-locals.py --ignore-header-symbols $PWD/.. 'make -j10 && make -j10 test'
```
and tmux 3.6a too:
```
$ ./autogen.sh
$ CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ ./configure
$ INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
1379 1149 54.5491

# 53 symbols unused according to Localizer (165 if headers ignored)
$ ./configure
$ find-locals.py --ignore-header-symbols $PWD 'make -j10 && make -j10 check'
```
and libuv 1.51.0:
```
$ ./autogen.sh
$ CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ ./configure
$ INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
316 457 40.8797

# 34 symbols unused according to Localizer (45 if headers ignored)
$ ./configure
$ find-locals.py --ignore-header-symbols $PWD 'make -j10 && make -j10 check'
```
and gcc 15.2.0:
```
$ contrib/download_prerequisites
$ mkdir build && cd build
$ CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ ../configure --enable-languages=jit,c,c++,fortran --enable-host-shared --disable-bootstrap --disable-multilib
$ INTERNAL_STATS=1 make -j4 all-gcc |& tee make.log
$ ./parse_stats.sh < make.log
32799 44471 42.4473

# 4.1K symbols unused according to Localizer (10.5 if headers ignored)
# (mainly due to missing anon. namespaces or statics but
# also because I compiled just one backend and not all frontends)
$ ../configure --enable-languages=jit,c,c++,fortran --enable-host-shared --disable-bootstrap --disable-multilib
$ find-locals.py --ignore-header-symbols $PWD/.. make -j10 all-gcc
```

## Measurements

### Static estimates

To speed up log collection
  - change `DEBUG_TYPE` to `"sccp-solver"`
    in `lib/Transforms/Utils/SCCPSolver.cpp`
  - remove
    ```
    LLVM_DEBUG(dbgs() << "  BasicBlock Dead:" << BB);
    ```
    in `Scalar/SCCP.cpp` and `IPO/SCCP.cpp`

Following instructions for [bounds checks](../../cons/bounds-checks/analysis.md#static-estimates):
```
# Ensure that LLVM is rebuild for both versions (see util/compiler.md for details) !

$ export RUSTFLAGS_NOT_BOOTSTRAP='-Cllvm-args=-debug-only=inline,sccp,argpromition,deadargelim'
$ ./x build --stage 1 compiler
$ ./x build -j1 --stage 2 compiler &> build.log

# Baseline
$ grep -c 'Size after inlining:' build.log
???
$ grep -c 'BasicBlock Dead:' build.log
???
$ grep -c 'Found that GV .* is constant' build.log
???
$ grep -c 'ARG PROMOTION:' build.log
???
$ grep -c 'DeadArgumentEliminationPass - Removing \(argument\|return value\)' build.log
???

# No-static
$ grep -c 'Size after inlining:' build.log
???
$ grep -c 'BasicBlock Dead:' build.log
???
$ grep -c 'Found that GV .* is constant' build.log
???
$ grep -c 'ARG PROMOTION:' build.log
???
$ grep -c 'DeadArgumentEliminationPass - Removing \(argument\|return value\)' build.log
???
```

TODO:
  - how does it influence code size ? E.g. 4 instances of `deserialize_from_impl`
    in meilisearch/search_songs

### Runtime improvements

Clang++ performance compared as in [llvm-bench](../../../benchmarks/cpp/llvm-bench)
degraded by ~1%:
```
$ cmake -G Ninja -DCMAKE_C_COMPILER=$PREFIX/bin/clang -DCMAKE_CXX_COMPILER=$PREFIX/bin/clang++ -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS= -DCMAKE_EXE_LINKER_FLAGS= -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS=clang ../llvm
$ ninja clang

# Repeat N times
$ /usr/bin/time setarch -R ~/src/llvm/llvm-project/build-stage1/bin/clang++ -O2 -w -S -o /dev/null CGBuiltin.ii
```
and ffmpeg as well by 1% (tested as in [ffmpeg-bench](../../../benchmarks/cpp/ffmpeg-bench)).

TODO:
  - collect Rust runtime perf measurements with disabled internals and (maybe) `-mllvm -enable-ipra`

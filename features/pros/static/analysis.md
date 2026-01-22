# Administrivia

Assignee: yugr

Parent task: gh-50

Effort: 5h

TODO: fix all TODOs that are mentioned in feature's README

# Background

Functions which are local in translation unit (aka static or internal)
can be optimized
[more aggressively](https://web.archive.org/web/20240309202636/https://embeddedgurus.com/stack-overflow/2008/12/efficient-c-tips-5-make-local-functions-static/)
by compiler:
  - ABI-violating optimizations (e.g. [IPRA](https://reviews.llvm.org/D23980))
  - change calling convention (to `coldcc` or `fastcc`, see `Transforms/IPO/GlobalOpt.cpp`)
  - more aggressive inlining (e.g. it's always beneficial to inline static function called once)

In C/C++ functions are public by default and need to be localized explicitly
(via `static` or anon. namespaces). This is called internal linkage.

TODO: no way to localize methods in C++ (esp. `private` methods) except factoring out to anon. namespaces

In Rust functions are local by default and need to be published explicitly
via `pub` keyword.

TODO: are `pub(crate/super/self)` symbols internalized ?

C# has `internal` specifier but there is no info if it can improve performance.
Swift functions need to be internalized explicitly via `private`.
In Go developer is forced to choose whether function is internal (starts w/ lowercase)
or public (starts w/ uppercase). Fortran functions are external by default.

# Examples

TODO:
  - clear example (Rust microbenchmark, asm code)

# Optimizations

TODO:
  - info whether LLVM and MIR opts can potentially optimize without it (and with what limitations)
    * inline/template, LTO, unity builds, etc.

# Suggested reading

TODO:
  - links to important articles (design, etc.)
  - (need to collect prooflinks with timecodes, reprocases for everything)

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

# 2269 symbols unused according to Localizer (2398 if headers ignored)
$ cmake -B build -DENABLE_IPC=OFF
$ find-locals.py --ignore-header-symbols $PWD 'make -j10 -C build && make -j10 -C build test'
```
and opencv 4.12.0:
```
$ cmake -B build -DCMAKE_C_COMPILER=$PREFIX/bin/clang -DCMAKE_CXX_COMPILER=$PREFIX/bin/clang++
$ INTERNAL_STATS=1 make -C build -j4 |& tee make.log
$ ./parse_stats.sh < make.log
146600 22938 86.4703

# 11.8 symbols unused according to Localizer (21.5K with tests, 22.3 if headers ignored)
$ cmake -B build -DBUILD_TESTS=ON -DBUILD_PERF_TESTS=ON -DBUILD_EXAMPLES=ON -DBUILD_opencv_apps=ON
$ find-locals.py --ignore-header-symbols $PWD make -j10 -C build
```
and clang llvmorg-20.1.7:
```
$ cmake -G Ninja -DCMAKE_C_COMPILER=$PREFIX/bin/clang -DCMAKE_CXX_COMPILER=$PREFIX/bin/clang++ -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG' -DCMAKE_EXE_LINKER_FLAGS= -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS=clang ../llvm
$ INTERNAL_STATS=1 ninja -j4 |& tee make.log
$ ./parse_stats.sh < make.log
425733 61557 87.3675
```

For other projects numbers are dramatically worse e.g.
openssl 3.6.0 has worse numbers (but this may be because of exported symbols):
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

# 9.1K symbols unused according to Localizer (11.2K if headers ignored)
$ ../configure --enable-languages=jit,c,c++,fortran --enable-host-shared --disable-bootstrap --disable-multilib
$ find-locals.py --ignore-header-symbols $PWD make -j10 all-gcc
```

## Measurements

### Static estimates

TODO:
  - collect compiler stats: SLP/loop autovec, CSE/GVN/LICM, NoAlias returns from AA manager

### Runtime improvements

Clang++ performance compared as in [llvm-bench](../../../util/llvm-bench)
degraded by ~1%:
```
$ cmake -G Ninja -DCMAKE_C_COMPILER=$PREFIX/bin/clang -DCMAKE_CXX_COMPILER=$PREFIX/bin/clang++ -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS= -DCMAKE_EXE_LINKER_FLAGS= -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS=clang ../llvm
$ ninja clang

# Repeat N times
$ /usr/bin/time setarch -R ~/src/llvm/llvm-project/build-stage1/bin/clang++ -O2 -w -S -o /dev/null CGBuiltin.ii
```
and ffmpeg as well by 1% (tested as in [ffmpeg-bench](../../../util/ffmpeg-bench)).

TODO:
  - collect Rust runtime perf measurements with disabled internals and (maybe) `-mllvm -enable-ipra`

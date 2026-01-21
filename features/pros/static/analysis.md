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

TODO: no way to localize methods in C++ (esp. `private` methods)

In Rust functions are local by default and need to be published explicitly
via `pub` keyword.

TODO: are `pub(crate/super/self)` symbols internalized ?

TODO:
  - why is this feature needed ?
    * situation in C/C++
      + e.g. [The New C Standard: An Economic and Cultural Commentary](https://www.coding-guidelines.com/cbook/cbook1_1.pdf)
      + e.g. [Rationale for International Standard Programming Languages - C](https://www.open-std.org/jtc1/sc22/wg14/www/C99RationaleV5.10.pdf)
    * situation in other langs:
      + [Java](https://docs.oracle.com/javase/specs/jls/se24/html/),
      + [C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/introduction)
      + [Go](https://go.dev/ref/spec)
      + [Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/aboutthelanguagereference/)
      + [Fortran](https://j3-fortran.org/doc/year/24/24-007.pdf)
      + Ada ([RM](http://www.ada-auth.org/standards/22rm/html/RM-TOC.html) and [ARM](http://www.ada-auth.org/standards/22aarm/html/AA-TOC.html))
  - types of check (e.g. compiler/stdlib parts)

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

## Prevalence

TODO:
  - is this optimization common in practice ?
    * may need to write analysis passes to scan real Rust code (libs, big projects) for occurences

## Disabling optimization

TODO:
  - determine how to enable/disable feature in compiler/stdlib
    * there may be flags (e.g. for interger overflows) but sometimes may need patch code (e.g. for bounds checks)
      + patch for each feature needs to be implemented in separate branch (in private compiler repo)
      + compiler modifications need to be kept in private compiler repo `yugr/rust-private`
    * make sure that found solution works on real examples
    * note that simply using `RUSTFLAGS` isn't great because they override project settings in `Cargo.toml`

## Measurements

TODO: collect compiler stats:
  - depend on feature
  - LLVM stats may be misleading because some opts (e.g. inline) are done in frontend
    (at MIR level). But recollecting with `-Zmir-opt-level=0`
    e.g. in panic feature didn't improve anything.
  - e.g. SLP/loop autovec for bounds checking feature
  - e.g. NoAlias returns from AA manager for alias feature
  - e.g. CSE/GVN/LICM for alias feature

### Static estimates

TODO: recollect static counts with updated patch

Counts for Rust benchmarks were obtained with
Rust's llvm-project with [attached patch](0001-Remove-internal-functions.patch)
that both disables internal symbols and collects stats:
```
$ INTERNAL_STATS=1 ../benchmarks/runall.sh --runner-args "-b -j6 -v" no-static
$ csplit -z -f section_ -b "%02d.txt" results/no-static/runner.log '/^Building /' '{*}'
$ for f in section_*.txt; do
    name=$(head -n1 $f | awk '{print $2}')
    echo $name
    ./parse_stats.sh < $f
  done
SpacetimeDB...
839580 205050 80.371
bevy...
1266716 248486 83.6005
meilisearch...
1720905 55974 96.8499
nalgebra...
110550 21742 83.5651
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
233690 69408 77.1005
tokio...
258030 54341 82.6037
uv...
981092 184816 84.1483
veloren...
1354875 349170 79.5093
zed...
1927025 103508 94.9024
```

TODO: rustc stage2 stats

For some C/C++ projects the numbers are on par
(all measurements were done with llvmorg-20.1.7 Clang with the above patch).
For example x264 (0480cb05) stats are similar:
```
$ PREFIX=$HOME/src/llvm/remove-internals/build
$ CC=$PREFIX/bin/clang ../configure --prefix=$PWD/../install --enable-static --enable-shared
$ INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
1823 503 78.3749
```
and ffmpeg 8.0.1 too:
```
$ PKG_CONFIG_PATH=$HOME/src/x264/install/lib/pkgconfig ~/src/ffmpeg-8.0.1/configure --prefix=$PWD/../install --cc=$PREFIX/bin/clang --cxx=$PREFIX/bin/clang++ --extra-cflags='-O2 -DNDEBUG' --extra-cxxflags='-O2 -DNDEBUG' --enable-libx264 --enable-gpl
$ INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
35817 4053 89.8345
```
and git 2.52.0:
```
$ CC=clang CXX=clang++ ./configure
$ PATH=$PREFIX/bin:$PATH INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
10868 3612 75.0552
```

For other projects numbers are dramatically worse e.g.
openssl 3.6.0 has worse numbers (but this may be because of exported symbols):
```
$ PATH=$PREFIX/bin:$PATH
$ ../config linux-x86_64-clang
$ INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
25014 21983 53.2247

# 308 symbols unused according to Localizer (678 if headers ignored)
$ ../config linux-x86_64
$ find-locals.py --ignore-header-symbols $PWD/.. 'make -j10 && make -j10 test'
```
and tmux 3.6a too:
```
$ ./autogen.sh
$ CC=clang CXX=clang++ ./configure
$ PATH=$PREFIX/bin:$PATH INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
1379 1154 54.4414

# 53 symbols unused according to Localizer (165 if headers ignored)
$ ./configure
$ find-locals.py --ignore-header-symbols $PWD 'make -j10 && make -j10 check'
```
and libuv 1.51.0:
```
$ ./autogen.sh
$ CC=clang CXX=clang++ ./configure
$ PATH=$PREFIX/bin:$PATH INTERNAL_STATS=1 make -j4 |& tee make.log
$ ./parse_stats.sh < make.log
316 464 40.5128

# 34 symbols unused according to Localizer (45 if headers ignored)
$ ./configure
$ find-locals.py --ignore-header-symbols $PWD 'make -j10 && make -j10 check'
```
and bitcoin v30.2:
```
$ cmake -B build -DCMAKE_C_COMPILER=$PREFIX/bin/clang  -DCMAKE_CXX_COMPILER=$PREFIX/bin/clang++  -DENABLE_IPC=OFF
$ INTERNAL_STATS=1 make -C build -j4 |& tee make.log
$ ./parse_stats.sh < make.log
27532 418346 6.17478

# 2269 symbols unused according to Localizer (2398 if headers ignored)
$ cmake -B build -DENABLE_IPC=OFF
$ find-locals.py --ignore-header-symbols $PWD 'make -j10 -C build && make -j10 -C build test'
```
and opencv 4.12.0:
```
$ cmake -B build -DCMAKE_C_COMPILER=$PREFIX/bin/clang -DCMAKE_CXX_COMPILER=$PREFIX/bin/clang++
$ INTERNAL_STATS=1 make -C build -j4 |& tee make.log
$ ./parse_stats.sh < make.log
146600 980637 13.0053

# 11.8 symbols unused according to Localizer (21.5K with tests, 22.3 if headers ignored)
$ cmake -B build -DBUILD_TESTS=ON -DBUILD_PERF_TESTS=ON -DBUILD_EXAMPLES=ON -DBUILD_opencv_apps=ON
$ find-locals.py --ignore-header-symbols $PWD make -j10 -C build
```
and gcc 15.2.0:
```
$ contrib/download_prerequisites
$ mkdir build && cd build
$ CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ ../configure --enable-languages=jit,c,c++,fortran --enable-host-shared --disable-bootstrap --disable-multilib
$ INTERNAL_STATS=1 make -j4 all-gcc |& tee make.log
$ ./parse_stats.sh < make.log
32594 233822 12.2343

# 9.1K symbols unused according to Localizer (11.2K if headers ignored)
$ ../configure --enable-languages=jit,c,c++,fortran --enable-host-shared --disable-bootstrap --disable-multilib
$ find-locals.py --ignore-header-symbols $PWD make -j10 all-gcc
```
and clang llvmorg-20.1.7:
```
$ cmake -G Ninja -DCMAKE_C_COMPILER=$PREFIX/bin/clang -DCMAKE_CXX_COMPILER=$PREFIX/bin/clang++ -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG' -DCMAKE_EXE_LINKER_FLAGS= -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS=clang ../llvm
$ INTERNAL_STATS=1 ninja -j4 |& tee make.log
$ ./parse_stats.sh < make.log
425733 3583463 10.6189

# ??? symbols unused according to Localizer (??? if headers ignored)
$ cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG' -DCMAKE_EXE_LINKER_FLAGS= -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS=clang ../llvm
$ find-locals.py --ignore-header-symbols $PWD ninja
```

### Runtime improvements

TODO:
  - collect runtime perf measurements with disabled internals and `-mllvm -enable-ipra`

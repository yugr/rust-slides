This patch prints stats about applications of `-fsanitize=bounds`.
It allows us to determine how often this check can be applied and
optimized out. This can serve as proxy metric of efficiency of
bounds checks in C/C++ i.e. how often compiler can check index accesses.

To test, first build and install stage1 compiler
(llvmorg-20.1.7 tag + [patch](bounds-test.patch)):
```
$ cmake -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS='clang' -DLLVM_ENABLE_RUNTIMES=compiler-rt -DCMAKE_INSTALL_PREFIX=$PWD/../stage1 ../llvm
$ ninja && ninja install
```
and collect stats:
```
$ cmake -G Ninja -DCMAKE_C_COMPILER=$PWD/../stage1/bin/clang -DCMAKE_CXX_COMPILER=$PWD/../stage1/bin/clang++ -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DCMAKE_CXX_FLAGS='-O2 -fsanitize=bounds' -DCMAKE_LINK_FLAGS='-O2 -fsanitize=bounds' -DLLVM_APPEND_VC_REV=OFF -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS='clang' ../llvm
$ ninja -j1 clang |& tee ninja.log
$ cat ninja.log | awk '/BoundsCheckingPass:/{succs+=$2; total+=$3; opt+=$4} END{print ((succs - opts) / (total - opts))}'
0.222293
```

TODO: also check `-fsanitize=object-size` by collecting stats in `llvm::lowerObjectSizeCall`

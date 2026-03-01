A simple benchmark for hardening options which runs Clang on huge slow files.

First clone LLVM, checkout llvmorg-20.1.7 tag and apply patches.

Then build stage0 compiler:
```
$ LLVM_DIR=...
$ BUILD_DIR=...
$ INSTALL_DIR=...
$ cmake -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF \
    -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS='clang;compiler-rt' -DLLVM_ENABLE_RUNTIMES='libcxx;libcxxabi;libunwind' \
    -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR -B $BUILD_DIR $LLVM_DIR/llvm
$ cmake -B $BUILD_DIR
$ ninja -C $BUILD_DIR install
```

Finally build and benchmark stage2 compilers:
```
$ PATH=$INSTALL_DIR/bin:$PATH ./run.sh --llvm $LLVM_DIR configs.txt tests.txt
```

Data can then be averged via
```
for file in results/*/CGBuiltin.ii.log; do echo $file; cat $file | sed -ne '/user/{s/user.*//; p}' | Median; done
```

TODO: prepare sources in `run.sh` ?

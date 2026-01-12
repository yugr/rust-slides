A simple benchmark for hardening options which runs Clang on huge slow files.

First clone LLVM, checkout llvmorg-20.1.7 tag and apply patches.

Then build stage0 compiler:
```
$ LLVM_DIR=...
$ BUILD_DIR=...
$ INSTALL_DIR=...
$ cmake -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG' -DCMAKE_EXE_LINKER_FLAGS= \
    -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF \
    -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS='clang;compiler-rt' -DLLVM_ENABLE_RUNTIMES='libcxx;libcxxabi;libunwind' \
    -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR -B $BUILD_DIR $LLVM_DIR/llvm
```

Finally build and benchmark stage1 compilers:
```
$ PATH=$INSTALL_DIR/bin:$PATH ./run.sh --llvm $LLVM_DIR configs.txt tests.txt
```

TODO: prepare sources in `run.sh` ?

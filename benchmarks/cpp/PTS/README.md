Helper scripts for running tests from Phoronix Test Suite.

Install config under `$HOME/.phoronix-test-suite` and
clone from https://github.com/phoronix-test-suite/phoronix-test-suite
and run `run.sh`.

Script assumes that environment was set up according to comments in
[gh-55](https://github.com/yugr/rust-slides/issues/55).

TODO:
  - log comparator
  - reduce stdev ?

# Configs

Note that `-O3` is forced in some tests.
`-fasm` is needed for some tests that use inline asm and `-std=c99`
(which disables inline asm for Clang but not GCC).

Baseline:
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS='-O2 -DNDEBUG -fpermissive' CXXFLAGS="$CFLAGS"
```

StackProtector:
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS='-O2 -DNDEBUG -fpermissive -fstack-protector-strong' CXXFLAGS="$CFLAGS"
```

Fortify2:
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS='-O2 -DNDEBUG -fpermissive -D_FORTIFY_SOURCE=2' CXXFLAGS="$CFLAGS"
```

Fortify3:
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS='-O2 -DNDEBUG -fpermissive -D_FORTIFY_SOURCE=3' CXXFLAGS="$CFLAGS"
```

Bounds:
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS='-O2 -DNDEBUG -fpermissive -fsanitize=bounds -fsanitize-minimal-runtime' CXXFLAGS="$CFLAGS"
```

Bounds:
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS='-O2 -DNDEBUG -fpermissive -fsanitize=object-size -fsanitize-minimal-runtime' CXXFLAGS="$CFLAGS"
```

Libcxx:
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS="-O2 -DNDEBUG -fpermissive -nostdinc++ -isystem $PREFIX/include/c++/v1 -isystem $PREFIX/include/x86_64-unknown-linux-gnu/c++/v1" CXXFLAGS="$CFLAGS" LDFLAGS="-L $PREFIX/lib/x86_64-unknown-linux-gnu -lc++abi -lunwind -Wl,-rpath,$PREFIX/lib/x86_64-unknown-linux-gnu"
```
(need STL in CFLAGS because nginx sets CXXFLAGS to them).

HardenedSTL:
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS="-O2 -DNDEBUG -fpermissive -nostdinc++ -isystem $PREFIX/include/c++/v1 -isystem $PREFIX/include/x86_64-unknown-linux-gnu/c++/v1 -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST" CXXFLAGS="$CFLAGS" LDFLAGS="-L $PREFIX/lib/x86_64-unknown-linux-gnu -lc++abi -lunwind -Wl,-rpath,$PREFIX/lib/x86_64-unknown-linux-gnu"
```
(need STL in CFLAGS because nginx sets CXXFLAGS to them,
note that HardenedSTL should be compared against Libcxx as other configs use GCC libstdc++).

IOF:
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS='-O2 -DNDEBUG -fpermissive -fsanitize=signed-integer-overflow,pointer-overflow -fno-sanitize-recover=signed-integer-overflow,pointer-overflow -fsanitize-minimal-runtime' CXXFLAGS="$CFLAGS"
```
(no unsigned-integer-overflow in IOF because some benchmarks use it intentionally).

AutoInit:
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS='-O2 -DNDEBUG -fpermissive -ftrivial-auto-var-init=zero' CXXFLAGS="$CFLAGS"
```

Stack Clash (probestack):
```
CC=$PREFIX/bin/clang CXX=$PREFIX/bin/clang++ CFLAGS='-O2 -DNDEBUG -fpermissive -fstack-clash-protection' CXXFLAGS="$CFLAGS"
```

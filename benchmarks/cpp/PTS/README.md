Helper scripts for running tests from Phoronix Test Suite.

To run Phoronix, install
```
$ sudo apt install php-cli php-xml
$ git clone https://github.com/yugr/cc-wrappers
```

Also install [config](user-config.xml) to `$HOME/.phoronix-test-suite` and
clone from https://github.com/phoronix-test-suite/phoronix-test-suite.

Then run
```
$ PATH=path/to/cc-wrappers:$PATH WRAPPER_CC=path/to/clang WRAPPER_CXX=path/to/clang++ ./run.sh
```

# Non-root environments

To run in environment w/o root access, set it up according to comments in
[gh-55](https://github.com/yugr/rust-slides/issues/55) and run under
[gcc14-env](gcc14-env) script:
```
PATH=... WRAPPER_CC=... WRAPPER_CXX=... ./gcc14-env ./benchmark.sh
```

# Issues with PTS

Based on commit a5364528:
  - not all tests respect environment variables (`CC`, `CFLAGS`, etc.)
    * e.g. luajit ignores `CC`
  - not all dependencies are handled by install.sh
    so need root access to use PTS
    * e.g. MPI in pts/gromacs or gflags/snappy in pts/rocksdb
  - some tests do not build with clang
    * e.g. pts/z3
  - some tests use prebuilt binaries
    * e.g. pts/blender
  - XML configs are inconvenient for tools
    * need command-line flags for all settings

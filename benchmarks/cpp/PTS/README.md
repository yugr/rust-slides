Helper scripts for running tests from Phoronix Test Suite.

To run Phoronix, install
```
# Phoronix deps
$ sudo apt install php-cli php-xml

# Package deps
$ sudo apt install gcc g++ make cmake ninja-build meson nasm libncurses-dev libpng-dev libtiff-dev libflags-dev libsnappy-dev libglut-dev 7zip

$ git clone https://github.com/yugr/cc-wrappers
```

Also install [config](user-config.xml) to `$HOME/.phoronix-test-suite` and
clone from https://github.com/phoronix-test-suite/phoronix-test-suite.

Then run
```
$ PATH=path/to/cc-wrappers:$PATH WRAPPER_CC=path/to/clang WRAPPER_CXX=path/to/clang++ ./run.sh
```

It's recommended to do
```
$ php pts-core/phoronix-test-suite.php make-download-cache
```
if you plan to run tests more than once (to save some bandwidth).

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
    * this is inconvenient because user needs root to install them
    * also these dependencies are not recompiled
    * e.g. MPI in pts/gromacs, gflags/snappy in pts/rocksdb, libpng/libtiff in pts/povray
  - some tests do not build with clang
    * e.g. pts/z3
  - some tests use prebuilt binaries
    * e.g. pts/blender
  - some tests take too long (~hours)
  - mix of XML configs and environment variables is inconvenient for tools
    * need command-line flags for all settings

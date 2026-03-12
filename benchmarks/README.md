Here we keep information about projects which we use for benchmarking.

See [methodology](method.md) for requirements on adding a new benchmark.

# Rust benchmarks

To clone, build and run benchmarks and compare results, run
```
# Install dependencies (requires root access)
$ ./install_deps.sh

$ ./runall.sh baseline bounds force-aliasing
```

Run
```
$ ./runall.sh --help
```
for more details.

# Automatic benchmarks

All compiler versions can be run via
```
$ mkdir workdir
$ cd workdir
$ ../build_test_all.sh -f
```

# C++ benchmarks

C++ benchmarks are in `cpp/` subdir (check READMEs there).

# System setup

It's recommended to setup system for benchmarking
according to instructions from [uInit](https://github.com/yugr/uInit)
and in particular run `./performance.sh` and `./stop_services.sh`.

See [this page](averaging.md) for discussion of averaging methods.

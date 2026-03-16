Here we keep information about projects which we use for benchmarking.

See [methodology](method.md) for requirements on adding a new benchmark.

# How to run

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

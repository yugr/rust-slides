Here we keep information about projects which we use for benchmarking.

See [methodology](method.md) for requirements on adding a new benchmark.

# How to run

To clone, build and run benchmarks and compare results,
[install rust tools](https://rust-lang.org/tools/install/)
and then run
```
# Install dependencies (requires root access)
$ ./install_deps.sh

# Rustc benchmarks need this
$ echo 'kernel.perf_event_paranoid = -1' | sudo tee -a /etc/sysctl.conf
$ sudo sysctl -p

$ ./runall.sh baseline bounds force-aliasing
```

Run
```
$ ./runall.sh --help
```
for more details.

# Plots

Once the data is collected, plots can be built via something like
```
$ benchmarks/plots.py --path work/results-20260220 force-overflow-checks
```

# Automatic benchmarks

All compiler versions can be run via
```
$ cd workdir
$ build_test_all.sh -f path/to/rust-private.git path/to/ci-llvm
```
(ci-llvm can be obtained from [here](https://github.com/yugr/rustc-builds)).

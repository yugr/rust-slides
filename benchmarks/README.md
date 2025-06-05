Here we keep information about projects which we use for benchmarking.

See [methodology](method.md) for requirements on adding a new benchmark.

To clone, build and run benchmarks, run
```
# Install dependencies (requires root access)
# Note that cargo deps need to be installed for each toolchain separately
$ ./install_deps.sh

$ ./runner -t $TOOLCHAIN_NAME
```

Run
```
$ ./runner --help
```
for more details.

Here we keep information about projects which we use for benchmarking.

See [methodology](method.md) for requirements on adding a new benchmark.

To clone, build and run benchmarks and compare results, run
```
# Install dependencies (requires root access)
$ ./install_deps.sh

$ ./runall.sh
```

Run
```
$ ./runall.sh --help
```
for more details.

It's recommended to setup system for benchmarking
according to instructions from [uInit](https://github.com/yugr/uInit)
and in particular run `./performance.sh` and `./stop_services.sh`.

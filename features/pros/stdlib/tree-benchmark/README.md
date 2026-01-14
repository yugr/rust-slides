Benchmark based on https://users.rust-lang.org/t/hashmap-performance/6476

Run C++ version via `run.sh` and Rust via
```
$ cargo +baseline b --release
$ time target/release/tree
```

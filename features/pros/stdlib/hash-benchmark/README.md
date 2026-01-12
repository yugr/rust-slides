Benchmark based on https://users.rust-lang.org/t/hashmap-performance/6476

Run C++ version via `run.sh` and Rust via
```
$ cargo +baseline b --features=sip --release
$ time target/release/hash
$ cargo +baseline b --features=ahash --release
$ time target/release/hash
$ cargo +baseline b --features=fxhash --release
$ time target/release/hash
```

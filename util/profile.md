Various hints about profiling Rust programs and analyzing hotspots.

# Run single benchmark

To run particular bench via Criterion use
```
$ cargo bench ... -- BENCH_NAME
```
syntax e.g.
```
$ cargo +baseline bench --features=bench -- get_weighted_sse/32x8/10
```

You can also run benchmark itself (without cargo) via
```
$ ./target/release/deps/bench-bdf12f16089d0683 get_weighted_sse/32x8/10 --bench
```

# Extract benchmark

Criterion benchmark could be extracted to separate program with fixed number
of iterations for simpler profiling:
  - put necessary code to e.g. `mytest/test.rs`
    (including `main` function which runs benchmarking code appropriate number
    of times)
  - add to root Cargo.toml:
    ```
    [[bin]]
    name = "mytest"
    path = "mytest/test.rs"
    ```
  - build:
    ```
    $ cargo +baseline b --profile bench --bin mytest
    ```
    (may need to update required features from `[[bench]]` section and
    benchmark-specific dependencies)
  - now you can run `target/release/mytest-XXX`

# Disable stripping

Some projects strip generated binaries by default.

Make sure that `strip` is not specified in Cargo.toml, .cargo/config.toml or build.rs
and maybe explicitly set it to
```
strip = false
```
for bench/release profiles (this will override settings in dependencies).

Finally add
```
[target.x86_64-unknown-linux-gnu]
rustflags = ["-Cforce-frame-pointers=yes", "-Cstrip=none"]
```
to .cargo/config.toml and rebuild.

# Disable complex optimizations

Try adding
```
[build]
rustflags = [
  "-C", "llvm-args=-vectorize-loops=false",
  "-C", "llvm-args=-vectorize-slp=false",
  "-C", "llvm-args=-unroll-threshold=0",
  "-C", "llvm-args=-unroll-max-count=1",
]
```
to `.cargo/config.toml` to simplify generated code.

# Stabilize memory layout effects

Try adding to `rustflags` in `.cargo/config.toml`:
```
# 32 is typical fetchline size (64 also makes sense)
"-C", "llvm-args=-align-loops=32",
```

Also try using GNU linker:
```
linker = "ld.bfd"
```

Finally run with different environment sizes
(to control stack alignment):
```
export X=
for i in $(seq 128); do
  ./mybench
  X="${X}."
done
```

# Profile

To collect perf profile run
```
$ rm -f perf.data* && perf record -F99 --call-graph fp cmd arg1 ...
```
(omit `--call-graph fp` for flat profile).
You can also try using `lbr`/`dwarf` for more precise (and slow) tracking.

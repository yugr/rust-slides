To profile Rust executable first check that
`strip` is not specified in Cargo.toml, .cargo/config.toml or build.rs.

Add
```
[target.x86_64-unknown-linux-gnu]
rustflags = ["-Cforce-frame-pointers=yes", "-Cstrip=none"]
```
to .cargo/config.toml and rebuild.

Then run
```
$ rm -f perf.data* && perf record -F99 --call-graph fp cmd arg1 ...
```
(omit `--call-graph fp` for flat profile).
You can also try using `lbr`/`dwarf` for more precise (and slow) tracking.

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

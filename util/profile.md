To profile Rust executable first check that
`strip` is not specified in Cargo.toml or `.cargo/config.toml.

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

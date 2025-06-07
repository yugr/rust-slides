Various useful info about Rust compiler building, testing, etc.

# Local install

Use [rustup](https://rustup.rs/) but set
```
export RUSTUP_HOME=path/to/rustup/cache
export CARGO_HOME=path/to/cargo/and/rustc
```

# Building compiler

See [Dev Guide](https://rustc-dev-guide.rust-lang.org/building/how-to-build-and-run.html)
but generally it's just
```
$ ./x setup  # Select 'compiler'
$ ./x build -jN library
```
(set `N` according to your quota).

Then add to `bootstrap.toml`
```
[llvm]
assertions = true
```
for debug prints in LLVM.

Default settings (in `src/bootstrap/src/core/config/config.rs`) are reasonable:
  - build optimized compiler and std
  - no incremental build
  - default codegen units for std (16 ?)
    * this is overridden in `src/ci/run.sh`
  - no overflow checks unless debug
  - build std with `panic_unwind`

Disk consumption:
  - sources: 750M
  - release build: 10G

# Using built compiler

Register toolchain with `rustup`:
```
$ rustup toolchain link MY_TOOLCHAIN_NAME build/host/stage1
```
and make it default:
```
$ rustup default stage1
```

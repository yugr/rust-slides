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

Disk consumption:
  - sources: 750M
  - release build: 10G

# Using built compiler

Register toolchain with `rustup`:
```
$ rustup toolchain link stage1 build/host/stage1
```
and make it default:
```
$ rustup default stage1
```

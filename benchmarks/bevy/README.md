Bevy game engine benchmarks are located in the `benches` subdirectory of the [repo](https://github.com/bevyengine/bevy).

Built and tested on `de79d3f363e292489f2dbfdd22b6a9b93e7672ea` commit.

# Build

Built and tested with `rustc` version `rustc 1.86.0 (05f9846f8 2025-03-31)` and `cargo` version `cargo 1.86.0 (adf9b6ad1 2025-02-28)`

- Install [necessary dependencies](https://github.com/bevyengine/bevy/blob/latest/docs/linux_dependencies.md) for the engine to build 

# Run

Change directory to `bevy/benches` and execute `cargo bench` to run the available benchmarks (approx 60m on x86 12-core machine to build and run the benchmarks)

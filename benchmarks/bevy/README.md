For Bevy game engine benchmarks are separated into [dedicated repo](https://github.com/TheBevyFlock/bevy-bencher).

# Build

Built and tested with `rustc` version `rustc 1.86.0 (05f9846f8 2025-03-31)` (stable) and `cargo` version `cargo 1.86.0 (adf9b6ad1 2025-02-28)`

- Install [necessary dependencies](https://github.com/bevyengine/bevy/blob/latest/docs/linux_dependencies.md) for the engine to build 
- Clone the [benchmarks repo](https://github.com/TheBevyFlock/bevy-bencher)
- The benchmarks seems to be not up to date with the newer versions of Bevy, so patch the `Cargo.toml` file to use older version:
```
diff --git a/Cargo.toml b/Cargo.toml
index f337e02..1962bb5 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -27,7 +27,7 @@ members = ["file-size"]

 [workspace.dependencies]
 # Bevy, on the latest commit.
-bevy = { git = "https://github.com/bevyengine/bevy.git" }
+bevy = { git = "https://github.com/bevyengine/bevy.git", rev = "b231ebbc195e12ae47616748e532c8dbc2421" }

 [profile.file-size]
 inherits = "release"
```

# Run

Use `cargo bench` to run the available benchmarks (approx 5m on x86 12-core machine to build and run the benchmarks)

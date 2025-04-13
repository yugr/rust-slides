# List of projects for benchmarking

- Bevy

# Bevy

For Bevy game engine benchmarks are separated into `https://github.com/TheBevyFlock/bevy-bencher` repository.

## Setup

- Install necessary dependencies for the engine to build `https://github.com/bevyengine/bevy/blob/latest/docs/linux_dependencies.md`
- Clone the benchmarks repo `https://github.com/TheBevyFlock/bevy-bencher`
- The benchmarks seem to be not up to date with the newer versions of Bevy, so patch the `Cargo.toml` file to use older version:
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
- Use `cargo bench` to run the available benchmarks (approx 5m to build and run the benchmarks)


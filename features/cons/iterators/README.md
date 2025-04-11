Iterators are great but in some cases do not optimize very well.

In particular _exterior iteration_ (`for_each` w/ lambda)
is [known](https://github.com/rust-lang/rust/issues/101814#issuecomment-1247184222)
to optimize much better than traditional for-loops.

Iterators are great but in some cases do not optimize very well.

In some cases iterators are faster than indexing but that's not always the case.

Iterators are _much_ slower in debug.

In particular _exterior iteration_ (`for_each` w/ lambda, aka "external iteration")
is [known](https://github.com/rust-lang/rust/issues/101814#issuecomment-1247184222)
to optimize better than traditional for-loops.

Rust functions (and types) are `static` by default
(need to use `pub` to make them public).

This allows compiler to optimize them much more aggressively,
like `static` functions in C/C++.

TODO:
  - how does it influence code size ? E.g. 4 instances of `deserialize_from_impl`
    in meilisearch/search_songs

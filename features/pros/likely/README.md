`Some()` and `Ok()` are [annotated as likely arms](https://www.reddit.com/r/rust/comments/k5wk7r/comment/ger93vz/)
by the compiler.

TODO:
  - verify that unlikely blocks are always placed at end
  - hot-cold splitting benefits

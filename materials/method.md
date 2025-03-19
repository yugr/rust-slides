This file contains info about how we searched for materials for the talk.

Queries:
  - Rust performance issues
  - Rust compiler optimization
  - Rust inefficient data structures
  - Rust gamedev problems
  - Rust zero-cost abstractions

Look for any mentions of `/performance|optimizations|compiler|inefficient|code ?gen/i` in
  - coding guidelines for big and/or performance-critical projects
  - weeklies
    * https://github.com/rust-lang/this-week-in-rust
    * blogs below have mainly been extracted from last 4 years of weeklies (starting Dec 2020)
  - forums (also follow suggested links, recursively)
    * https://users.rust-lang.org
    * https://internals.rust-lang.org/c/compiler/20/l/hot
  - Reddit
    * general:
      + https://www.reddit.com/r/rust/search/?q=optimize&type=posts and https://www.reddit.com/r/rust/search/?q=performance&type=posts
    * top-1:
      + burntsushi (regex):
        - https://www.reddit.com/user/burntsushi/search/?q=optimize&type=comments and https://www.reddit.com/user/burntsushi/search/?q=performance&type=comments
      + Shnatsel :
        - https://www.reddit.com/user/Shnatsel/search/?q=optimize&type=comments and https://www.reddit.com/user/Shnatsel/search/?q=performance&type=comments

Check Github for innate (unfixable, by design) performance issues :
  - rejected opts: https://github.com/rust-lang/rust/issues?q=is%3Aissue%20state%3Aclosed%20reason%3Anot-planned%20label%3AI-slow
  - compiler RFCs: https://github.com/rust-lang/rust/issues?q=is%3Aissue%20label%3AT-compiler%20rfc

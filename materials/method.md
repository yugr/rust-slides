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
    * https://users.rust-lang.org (URLO)
    * https://internals.rust-lang.org/c/compiler/20/l/hot (IRLO)
  - Reddit
    * general:
      + https://www.reddit.com/r/rust/search/?q=optimize&type=posts and https://www.reddit.com/r/rust/search/?q=performance&type=posts
    * top-1 (ideally all comments but at least the ones mentioning "performance"):
      + burntsushi (regex):
        - https://www.reddit.com/user/burntsushi/search/?q=optimize&type=comments and https://www.reddit.com/user/burntsushi/search/?q=performance&type=comments
      + Shnatsel :
        - https://www.reddit.com/user/Shnatsel/search/?q=optimize&type=comments and https://www.reddit.com/user/Shnatsel/search/?q=performance&type=comments
      + steveklabnik1:
        - https://www.reddit.com/user/steveklabnik1/search/?q=performance&type=comments
      + Zde-G (gh-9):
        - https://www.reddit.com/user/Zde-G/search/?q=performance&type=comments
      + matthiem (gh-11):
        - https://www.reddit.com/user/Zde-G/search/?q=performance&type=comments
      + SkiFire13 (gh-12):
        - https://www.reddit.com/user/SkiFire13/search/?q=performance&type=comments
      + simonask_ (gh-13):
        - https://www.reddit.com/user/simonask_/search/?q=performance&type=comments
      + Lucretiel (gh-14):
        - https://www.reddit.com/user/Lucretiel/search/?q=performance&type=comments
      + VorpalWay :
        - https://www.reddit.com/user/VorpalWay/search/?q=performance&type=comments
    * other known maintainers:
      + nikic:
        - https://www.reddit.com/user/nikic/search/?q=rust&type=comments (nothing found)

Check Github for innate (unfixable, by design) performance issues (gh-2) :
  - rejected opts: https://github.com/rust-lang/rust/issues?q=is%3Aissue%20state%3Aclosed%20reason%3Anot-planned%20label%3AI-slow
  - compiler RFCs: https://github.com/rust-lang/rust/issues?q=is%3Aissue%20label%3AT-compiler%20rfc

Check compiler team repo (gh-8) :
  - https://github.com/rust-lang/compiler-team

Check compiler RFCs (gh-10) :
  - https://github.com/rust-lang/rfcs/tree/master/text

Check compiler Zulip chats :
  - t-compiler/mir-opts: https://rust-lang.zulipchat.com/#narrow/channel/189540-t-compiler.2Fmir-opts
  - t-compiler/performance: https://rust-lang.zulipchat.com/#narrow/channel/247081-t-compiler.2Fperformance

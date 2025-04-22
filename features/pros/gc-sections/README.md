Rust compiles with `-ffunction-sections -Wl,--gc-sections` by default.

This allows it to remove unused functions more aggressively.

This behavior can be disabled via `-C link-dead-code`.

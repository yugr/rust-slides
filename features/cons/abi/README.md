Rust ABI is very inefficient in some important cases.

# Enums

As explained [here](https://www.reddit.com/r/rust/comments/1gl050z/comment/lvqzdcf/)
enums are usually passed on stack (unlike e.g. slices which are passed in regs).
This is particularly bad for traditional Rust error handling
(based on `Result`/`Option`).

For example this code
```
#[inline(never)]
pub fn x() -> Result<i32, &'static str> {
    Ok(0)
}

pub fn y() -> Result<i32, &'static str> {
    let res = x()?;
    Ok(res + 1)
}
```
when compiled by 1.86 passes results of `x` and `y` on stack
(so `x` stores to stack, `y` stores to and reads from stack).

This is one of the reasons exceptions (panics) can be beneficial
(see [panics](../panics/README.md) for details).

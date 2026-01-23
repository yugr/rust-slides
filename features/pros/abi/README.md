This is about various ABI-related improvements.

# Case of `unique_ptr`

Itanium ABI in C++ [requires](https://stackoverflow.com/questions/58339165/why-can-a-t-be-passed-in-register-but-a-unique-ptrt-cannot)
non-trivial parameters which are passed by value to be passed as pointers to temporary objects under the hood.
Rust does not have this requirement.
So Rust's `Box` does not require double indirection
```
type T = i32;

extern "C" {
    fn g(i:T);
}

pub fn f_box(ptr: Box<T>){
    unsafe{g(*ptr);}
}
-------------------------------------
        push    rbx
        mov     rbx, rdi
        mov     edi, dword ptr [rdi]
        call    qword ptr [rip + g@GOTPCREL]
        mov     esi, 4
        mov     edx, 4
        mov     rdi, rbx
        pop     rbx
        jmp     qword ptr [rip + __rust_dealloc@GOTPCREL]
```
like C++ `unique_ptr`:
```
#include <memory>

using T = int;

void g(T);

void f_unique(std::unique_ptr<T> ptr){
    g(*ptr);
    return;
}
-------------------------------------
mov     rax, qword ptr [rdi]
mov     edi, dword ptr [rax]
jmp     g(int)@PLT
```
See [Box vs std::unique_ptr, assembly differences](https://www.reddit.com/r/rust/comments/16hi9em/box_vs_stdunique_ptr_assembly_differences/)
and [this](https://www.rottedfrog.co.uk/?p=24) and [Carruth's talk](https://www.youtube.com/watch?v=rHIkrotSwcc&feature=youtu.be&t=1261)
and [this TG post](https://t.me/grokaemcpp/842)
for detailed discussion.

# Issue with enums

On other hand other Rust ABI is very inefficient in some important cases.

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

This is one of the reasons exceptions (panics) can be better
than error handling (see [panics](../../cons/panics/README.md)
for details).

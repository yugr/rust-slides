Various ABI-related improvements.

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
and [this](https://www.rottedfrog.co.uk/?p=24) for detailed discussion.

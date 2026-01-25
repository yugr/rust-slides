# Rust ABI cons

SIMD vectors are always passed to functions (non-intrinsics) on stack.
See [Issue #44367](https://github.com/rust-lang/rust/issues/44367) for SIMD vector ABI problems and [this reply](https://github.com/rust-lang/rust/issues/44367#issuecomment-360323733) for a final decision.
For x86 with SSE2 enabled and x84\_64 architectures, 128 bit SIMD vectors are passed directly in registers. Less than 128 bit vectors will be able to be passed directly when [cranelift issue](https://github.com/bytecodealliance/wasmtime/issues/10254) is fixed.

# C++ and Rust comparisons

- `Box` vs `std::unique_ptr`
- `enum` vs `std::variant`
- `string` vs `std::string`
- `slice` vs `std::span`
- `Vec` vs `std::vec`
- `Rc` vs `std::shared_ptr`
- `Result` vs `std::expected`
- `Option` vs `std::optional`

TODO:
  - explain how `Box` and slice are different from other containers (`String`, `Vec`)
  - add explanation of current calling convention for structs (vs C++ structs) and
    tuples (vs `std::tuple`)
  - also cover returns from functions

## `Box` vs `std::unique_ptr`

[Godbolt](https://godbolt.org/z/Y6hYccWKs)
C++ on stack (lang requirements), Rust in reg

### Rust

```Rust
#[inline(never)]
pub fn foo(ptr: Box<i32>) -> i32 {
    return *ptr;
}
```

```Assembly
example::foo::ha92655d17a583d1e:
        push    rbx
        mov     ebx, dword ptr [rdi]
        mov     esi, 4
        mov     edx, 4
        call    qword ptr [rip + __rustc[de0091b922c53d7e]::__rust_dealloc@GOTPCREL]
        mov     eax, ebx
        pop     rbx
        ret
```

Rust `Box` is passed in registers.

### C++

```C++
#include <iostream>
#include <memory>

int foo(std::unique_ptr<int> ptr) {
    if (ptr) {
        return *ptr;
    } else {
        return -1;
    }
}
```

```Assembly
foo(std::unique_ptr<int, std::default_delete<int>>):
        mov     rax, qword ptr [rdi]
        test    rax, rax
        je      .LBB0_1
        mov     eax, dword ptr [rax]
        ret
.LBB0_1:
        mov     eax, -1
        ret
```

`std::unique_ptr` is passed on stack due to language ABI requirements of passing objects with non-trivial copy constructor or non-trivial destructor.
Nice explanation [here](https://stackoverflow.com/questions/58339165/why-can-a-t-be-passed-in-register-but-a-unique-ptrt-cannot).


## `enum` vs `std::variant`

[Godbolt](https://godbolt.org/z/jTro69n3x)
C++ in regs, Rust on stack (fixable in compiler)

### Rust

```Rust
pub enum FooEnum {
    Double(f64),
    Int(i32),
}

#[inline(never)]
pub fn foo(val: FooEnum) -> f64 {
    match val {
        FooEnum::Double(f) => return f,
        FooEnum::Int(i) => return i.into(),
    }
}
```

```Assembly
example::foo::hcfc5d64e7cbc02fd:
        cmp     byte ptr [rdi], 0
        jne     .LBB0_1
        movsd   xmm0, qword ptr [rdi + 8]
        ret
.LBB0_1:
        cvtsi2sd        xmm0, dword ptr [rdi + 4]
        ret
```

Rust `Enum` is passed on stack in this case due to underoptimization in compiler.


### C++

```C++
#include <iostream>
#include <variant>

double foo(std::variant<double, int> val) {
    if (std::holds_alternative<double>(val)) {
        return std::get<double>(val);
    } else if (std::holds_alternative<int>(val)) {
        return std::get<int>(val);
    }
}
```


```Assembly
foo(std::variant<double, int>):
        test    sil, sil
        je      .LBB0_1
        cvtsi2sd        xmm0, edi
        ret
.LBB0_1:
        movq    xmm0, rdi
        ret
```

C++ `std::variant` is passed in registers in this case.

## `String` vs `std::string`

[Godbolt](https://godbolt.org/z/3W1r9vjb9)
Both on stack

Rust `String` is internally a `Vec` and it is passed on stack for the same reasons that `Vec` is.

### Rust

```Rust
#[inline(never)]
pub fn foo(val: String) -> i32 {
    if val.as_bytes()[0] == 110 {
        return 10;
    } else {
        return 1;
    }
}
```

```Assembly
example::foo::hc3a5c6933c8add58:
        push    r14
        push    rbx
        push    rax
        mov     rbx, rdi
        cmp     qword ptr [rdi + 16], 0
        je      .LBB0_7
        mov     rsi, qword ptr [rbx]
        mov     rdi, qword ptr [rbx + 8]
        movzx   ebx, byte ptr [rdi]
        test    rsi, rsi
        je      .LBB0_3
        mov     edx, 1
        call    qword ptr [rip + __rustc[de0091b922c53d7e]::__rust_dealloc@GOTPCREL]
.LBB0_3:
        xor     eax, eax
        cmp     bl, 110
        sete    al
        lea     eax, [rax + 8*rax]
        inc     eax
        add     rsp, 8
        pop     rbx
        pop     r14
        ret
.LBB0_7:
        lea     rdx, [rip + .Lanon.2a5be9ce72f759b528604ab2593337ff.1]
        xor     edi, edi
        xor     esi, esi
        call    qword ptr [rip + core::panicking::panic_bounds_check::h9bbcb0758914da05@GOTPCREL]
        ud2
        mov     r14, rax
        mov     rsi, qword ptr [rbx]
        test    rsi, rsi
        je      .LBB0_6
        mov     rdi, qword ptr [rbx + 8]
        mov     edx, 1
        call    qword ptr [rip + __rustc[de0091b922c53d7e]::__rust_dealloc@GOTPCREL]
.LBB0_6:
        mov     rdi, r14
        call    _Unwind_Resume@PLT

.Lanon.2a5be9ce72f759b528604ab2593337ff.0:
        .asciz  "/app/example.rs"

.Lanon.2a5be9ce72f759b528604ab2593337ff.1:
        .quad   .Lanon.2a5be9ce72f759b528604ab2593337ff.0
        .asciz  "\017\000\000\000\000\000\000\000\003\000\000\000\b\000\000"

DW.ref.rust_eh_personality:
        .quad   rust_eh_personality
```

Rust string is passed on stack.

### C++

```C++
#include <iostream>
#include <string>

int foo(std::string val) {
    if (val[0] == 'n') {
        return 10;
    } else {
        return 1;
    }
}
```

```Assembly
foo(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>):
        mov     rax, qword ptr [rdi]
        xor     ecx, ecx
        cmp     byte ptr [rax], 110
        sete    cl
        lea     eax, [rcx + 8*rcx]
        inc     eax
        ret
```

C++ string is passed on stack.

## `slice` vs `std::span`

[Godbolt](https://godbolt.org/z/Yn8sz9rG3)
Both in registers

### Rust

```Rust
#[inline(never)]
pub fn foo(val: &[i32]) -> i32 {
    if val[14] == 110 {
        return 10;
    } else {
        return 1;
    }
}
```

```Assembly
example::foo::hd503a88ce6ba3ca9:
        cmp     rsi, 15
        jb      .LBB0_2
        xor     eax, eax
        cmp     dword ptr [rdi + 56], 110
        sete    al
        lea     eax, [rax + 8*rax]
        inc     eax
        ret
.LBB0_2:
        push    rax
        lea     rdx, [rip + .Lanon.75b44ac2035c68ff3344cf2d50bd324c.1]
        mov     edi, 14
        call    qword ptr [rip + core::panicking::panic_bounds_check::h9bbcb0758914da05@GOTPCREL]

.Lanon.75b44ac2035c68ff3344cf2d50bd324c.0:
        .asciz  "/app/example.rs"

.Lanon.75b44ac2035c68ff3344cf2d50bd324c.1:
        .quad   .Lanon.75b44ac2035c68ff3344cf2d50bd324c.0
        .asciz  "\017\000\000\000\000\000\000\000\003\000\000\000\b\000\000"
```

Rust slice is passed in two registers.

### C++

```C++
#include <iostream>
#include <span>

int foo(std::span<int> val) {
    if (val[14] == 110) {
        return 10;
    } else {
        return 1;
    }
}
```

```
foo(std::span<int, 18446744073709551615ul>):
        xor     eax, eax
        cmp     dword ptr [rdi + 56], 110
        sete    al
        lea     eax, [rax + 8*rax]
        inc     eax
        ret
```

C++ slice is passed in two registers.

## `Vec` vs `std::vec`

[Godbolt](https://godbolt.org/z/3bMYhb37f)
Both on stack

Rust `Vec` is passed on stack (as opposed to slice), because internal structure of `Vec` is more complex and does not get (and probably cannot) get laid out in two registers. It probably can be represented by 3 or 4 registers, but compiler currently does not support this kind of optimization (and it might turn out to not be beneficial).

### Rust

```Rust
#[inline(never)]
pub fn foo(val: Vec<i32>) -> i32 {
    if val[14] == 110 {
        return 10;
    } else {
        return 1;
    }
}
```

```Assembly
example::foo::h1051256627136600:
        push    r14
        push    rbx
        push    rax
        mov     rbx, rdi
        mov     rsi, qword ptr [rdi + 16]
        cmp     rsi, 15
        jb      .LBB0_7
        mov     rsi, qword ptr [rbx]
        mov     rdi, qword ptr [rbx + 8]
        mov     ebx, dword ptr [rdi + 56]
        test    rsi, rsi
        je      .LBB0_3
        shl     rsi, 2
        mov     edx, 4
        call    qword ptr [rip + __rustc[de0091b922c53d7e]::__rust_dealloc@GOTPCREL]
.LBB0_3:
        xor     eax, eax
        cmp     ebx, 110
        sete    al
        lea     eax, [rax + 8*rax]
        inc     eax
        add     rsp, 8
        pop     rbx
        pop     r14
        ret
.LBB0_7:
        lea     rdx, [rip + .Lanon.c779728cc48f00e9b1e719a99873bd95.1]
        mov     edi, 14
        call    qword ptr [rip + core::panicking::panic_bounds_check::h9bbcb0758914da05@GOTPCREL]
        ud2
        mov     r14, rax
        mov     rsi, qword ptr [rbx]
        test    rsi, rsi
        je      .LBB0_6
        mov     rdi, qword ptr [rbx + 8]
        shl     rsi, 2
        mov     edx, 4
        call    qword ptr [rip + __rustc[de0091b922c53d7e]::__rust_dealloc@GOTPCREL]
.LBB0_6:
        mov     rdi, r14
        call    _Unwind_Resume@PLT

.Lanon.c779728cc48f00e9b1e719a99873bd95.0:
        .asciz  "/app/example.rs"

.Lanon.c779728cc48f00e9b1e719a99873bd95.1:
        .quad   .Lanon.c779728cc48f00e9b1e719a99873bd95.0
        .asciz  "\017\000\000\000\000\000\000\000\003\000\000\000\013\000\000"

DW.ref.rust_eh_personality:
        .quad   rust_eh_personality
```

Rust `Vec` is passed on stack.


### C++

```C++
#include <iostream>
#include <vector>

int foo(std::vector<int> val) {
    if (val[14] == 110) {
        return 10;
    } else {
        return 1;
    }
}
```

```Assembly
foo(std::vector<int, std::allocator<int>>):
        mov     rax, qword ptr [rdi]
        xor     ecx, ecx
        cmp     dword ptr [rax + 56], 110
        sete    cl
        lea     eax, [rcx + 8*rcx]
        inc     eax
        ret
```

C++ vector is passed on stack.


## `Rc` vs `std::shared_ptr`

[Godbolt](https://godbolt.org/z/Waqnn5aaa)
C++ on stack, Rust in registers

### Rust

```Rust
#[inline(never)]
pub fn foo(val: std::rc::Rc<i32>) -> i32 {
    *val
}
```

```Assembly
alloc::rc::Rc<T,A>::drop_slow::h0d5f34dd4c5aa101:
        mov     rdi, qword ptr [rdi]
        cmp     rdi, -1
        je      .LBB0_2
        dec     qword ptr [rdi + 8]
        je      .LBB0_3
.LBB0_2:
        ret
.LBB0_3:
        mov     esi, 24
        mov     edx, 8
        jmp     qword ptr [rip + __rustc[de0091b922c53d7e]::__rust_dealloc@GOTPCREL]

example::foo::h436144ea3aa21137:
        push    rbx
        sub     rsp, 16
        mov     qword ptr [rsp + 8], rdi
        mov     ebx, dword ptr [rdi + 16]
        dec     qword ptr [rdi]
        je      .LBB1_1
        mov     eax, ebx
        add     rsp, 16
        pop     rbx
        ret
.LBB1_1:
        lea     rdi, [rsp + 8]
        call    qword ptr [rip + alloc::rc::Rc<T,A>::drop_slow::h0d5f34dd4c5aa101@GOTPCREL]
        mov     eax, ebx
        add     rsp, 16
        pop     rbx
        ret
```

Rust `Rc` is passed on stack.
Unlike C++, this does not seem to be a language requirement and more likely is a compiler underoptimization, as Rust `Box` is passed in registers.

### C++

```C++
#include <memory>

int foo(std::shared_ptr<int> val) {
    return *val;
}
```

```Assembly
foo(std::shared_ptr<int>):
        mov     rax, qword ptr [rdi]
        mov     eax, dword ptr [rax]
        ret
```

C++ `shared_ptr` is passed on stack.


## `Result` vs `std::expected`

[Godbolt](https://godbolt.org/z/aT8vWoaW8)
C++ in registers, Rust on stack


### Rust

```Rust
#[inline(never)]
pub fn foo(val: Result<i32, &str>) -> i32 {
    match val {
        Ok(i) => i,
        Err(_) => 0,
    }
}
```

```Assembly
example::foo::h3e18ceab42494c9b:
        xor     eax, eax
        cmp     qword ptr [rdi], 0
        jne     .LBB0_2
        mov     eax, dword ptr [rdi + 8]
.LBB0_2:
        ret
```

Rust `Result` is passed on stack due to compiler underoptimization of enum ABI.

### C++

```C++
#include <memory>
#include <expected>

int foo(std::expected<int, char*> val) {
    if (val.has_value()) {
        return *val;
    } else {
        return 0;
    }
}
```

```Assembly
foo(std::expected<int, char*>):
        xor     eax, eax
        test    sil, 1
        cmovne  eax, edi
        ret
```

C++ `expected` is passed in registers.

## `Option` vs `std::optional`

[Godbolt](https://godbolt.org/z/5Gh3hKET9)
Both in registers


### Rust

```Rust
#[inline(never)]
pub fn foo(val: Option<i32>) -> i32 {
    match val {
        Some(i) => i,
        None => 0,
    }
}
```

```Assembly
example::foo::h84433e59a9eeb653:
        xor     eax, eax
        test    dil, 1
        cmovne  eax, esi
        ret
```

Rust `Option` is passed in registers (due to niche optimization).

### C++

```C++
#include <memory>
#include <optional>

int foo(std::optional<int> val) {
    return val.value_or(0);
}
```

```Assembly
foo(std::optional<int>):
        xor     eax, eax
        bt      rdi, 32
        cmovb   eax, edi
        ret
```

C++ `optional` is passed in registers.

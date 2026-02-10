# Rust ABI cons

SIMD vectors are always passed to functions (non-intrinsics) on stack.
See [Issue #44367](https://github.com/rust-lang/rust/issues/44367) for SIMD vector ABI problems and [this reply](https://github.com/rust-lang/rust/issues/44367#issuecomment-360323733) for a final decision.
For x86 with SSE2 enabled and x84\_64 architectures, 128 bit SIMD vectors are passed directly in registers. Less than 128 bit vectors will be able to be passed directly when [cranelift issue](https://github.com/bytecodealliance/wasmtime/issues/10254) is fixed.

# Aggregate type passing ABI

Both [AMD64 abi](https://refspecs.linuxbase.org/elf/x86_64-abi-0.99.pdf) and AArch64 [AAPCS64](https://student.cs.uwaterloo.ca/~cs452/docs/rpi4b/aapcs64.pdf) allow aggregate types which size does not exceed 16 bytes to be passed in two general-purpose registers (also called struct scalarization).

In Rust, structs, tuples (which are just structs with unnamed fields) and enums are treated as aggregate types and are all subject to struct scalarization.
The possibility of scalarization is special-cased by a separate `BackendRepr` assigned to suitable aggregates - `ScalarPair`.
Aggregates with such `BackendRepr` will be lowered to an anonymous LLVM IR struct, which will be scalarized according to the ABI.
The assignment of `ScalarPair` representation is assigned based on both struct element sizes and their offsets, and it's logic does not seem perfectly optimal currently.
This covers some important cases: slices, `Rc`, ranges.
It does not take into account all the possibilities of different types coexisting, so some aggregate types (most prominently some cases of the Result enum, e.g `Result<i32, &str>`) are not converted to a `ScalarPair` and are instead passed in memory.

Structs that cannot be represented as a pair of scalars are passed in memory (on stack).
These structures are not lowered to LLVM IR structs and instead Rust frontend directly generates memory accesses.
Most likely this is due to Rust abi being unstable and allowing for optimizations that cannot be represented on LLVM IR level or performed by the LLVM backend.
Such optimizations are:
    - reordering of struct fields
    - niche optimizations

A significant difference from Itanium ABI is that the Itanium ABI requires any type with a non-trivial copy/move constructor or destructor to be passed on stack, and Rust ABI does not have this kind of limitation.

> If a parameter type is a class type that is non-trivial for the purposes of calls, the caller must allocate space for a temporary and pass that temporary by reference
>
> -- [Itanium ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#non-trivial-parameters)

# C++ and Rust comparisons

- `Box` vs `std::unique_ptr`
- `enum` vs `std::variant`
- `slice` vs `std::span`
- `Vec` vs `std::vec`
- `string` vs `std::string`
- `Arc` vs `std::shared_ptr`
- `Result` vs `std::expected`
- `Option` vs `std::optional`

TODO:
  - add explanation of current calling convention for structs (vs POD structs in amd64/arm64 platform ABIs
    and C++ structs in Itanium ABI) and tuples (vs `std::tuple`)
    * structs are sometimes passed in RegPair, otherwise as explicit pointers to temp. objects
      (mention why Rust chooses to explicitly lower them to pointers rather than rely on LLVM lowering)
    * for tuples can mention that they use same ABI as structs
    * most likely RegPair optimization is tightly related to underlying platform ABI
  - also cover returns from functions

## `Box` vs `std::unique_ptr`

[Godbolt](https://godbolt.org/z/Y6hYccWKs)

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

## `slice` vs `std::span`

[Godbolt](https://godbolt.org/z/Yn8sz9rG3)

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

Rust `Vec` is passed on stack (as opposed to slice), because internal structure of `Vec` is more complex and does not get (and probably cannot) get laid out in two registers due to it's size.
It probably can be represented by 3 or 4 registers, but the ABI does not allow it (see [Aggregate type passing ABI](#aggregate-type-passing-abi) section).

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

## `String` vs `std::string`

[Godbolt](https://godbolt.org/z/3W1r9vjb9)

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

Rust `String` is internally a `Vec` and it is passed on stack for the same reasons that `Vec` is.

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

## `Arc` vs `std::shared_ptr`

[Godbolt](https://godbolt.org/z/oP6r7Gh9G)

### Rust

```Rust
#[inline(never)]
pub fn foo(val: std::sync::Arc<i32>) -> i32 {
    *val
}
```

```Assembly
alloc::sync::Arc<T,A>::drop_slow::hd489889effa8d4fa:
        mov     rdi, qword ptr [rdi]
        cmp     rdi, -1
        je      .LBB0_2
        lock            dec     qword ptr [rdi + 8]
        jne     .LBB0_2
        mov     esi, 24
        mov     edx, 8
        jmp     qword ptr [rip + __rustc[de0091b922c53d7e]::__rust_dealloc@GOTPCREL]
.LBB0_2:
        ret

example::foo::he8d9e0d3f481b444:
        push    rbx
        sub     rsp, 16
        mov     qword ptr [rsp + 8], rdi
        mov     ebx, dword ptr [rdi + 16]
        lock            dec     qword ptr [rdi]
        jne     .LBB1_2
        lea     rdi, [rsp + 8]
        call    qword ptr [rip + alloc::sync::Arc<T,A>::drop_slow::hd489889effa8d4fa@GOTPCREL]
.LBB1_2:
        mov     eax, ebx
        add     rsp, 16
        pop     rbx
        ret
```

Rust `Arc` is passed in register.

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

Rust `Result` is passed on stack due to compiler underoptimization of enum ABI (as explained in the [Aggregate type passing ABI](#aggregate-type-passing-abi) section).
When considering if `Result` is eligible to be a `ScalarPair`, compiler check sizes and offsets of types in both enum variants.
Offset is calculated from the start of the representation, and the first byte of it is taken by the tag of the enum (unless some niche or non-null optimization is performed, which is not the case here).
In case of `Result` with 4-byte first variant and 8-byte second variant, their offsets are, respectively, 4 and 8 bytes (as 8-byte value has to be aligned on 8 bytes) and do not match.
This is blocking the conversion of enum to `ScalarPair`.

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


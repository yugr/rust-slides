Rust requires that all variables are initialized at definition.

This may be unnecessary if e.g. buffer will be overwritten later
but compiler will still require dummy initialization.
In some cases it can be optimized later,
in some this will be unnecessary overhead.

Unfortunately APIs to avoid redundant inits are complex.

# Solutions

Note that it's UB to access data before it's initialized (e.g. call `Vec::set_len` on it).
Also it is not valid to construct (mutable) reference to uninitialized memory:
> Creating a reference with &/&mut is only allowed if the pointer
> is properly aligned and points to initialized data. 
(from [here](https://doc.rust-lang.org/std/ptr/macro.addr_of_mut.html)).
Only pointers should be used to avoid UB.

The suggested solution for simple types is `MaybeUninit`.
E.g. for arrays:
```
let buf = unsafe {
    let mut buf = MaybeUninit::<[u8; 4]>::uninit();
    let ptr = buf.as_mut_ptr();
    for i in ... {
        ptr.offset(i).write(...);
    }
    buf.assume_init()
};
```
and for structs:
```
let role = unsafe {
    let mut uninit = MaybeUninit::<Role>::uninit();
    let ptr = uninit.as_mut_ptr();
    // Need write (instead of explicit assign) to avoid dropping uninitialized String
    addr_of_mut!((*ptr).name).write("basic".to_string());
    (*ptr).flag = 1;
    (*ptr).disabled = false;
    uninit.assume_init()
};
```

For vectors can also construct slice from raw parts:
```
let mut buf: Vec<u8> = ...;

let old_len = buf.len();
buf.reserve(data.len());

unsafe {
    let ptr = buf.spare_capacity_mut();
    for i in ... {
        ptr[idx].write(...);
    }
    buf.set_len(len + data.len());
}

# TODO

It's not clear how to benchmark Rust without initialization but we can benchmark GCC (via `-ftrivial-auto-var-init=zero`)

Is it UB to construct `&mut [T]` on uninitialized part of `Vec` for the purpose of initializing it ?

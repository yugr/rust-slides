Rust requires that all variables are initialized at definition.

This may be unnecessary if e.g. buffer will be overwritten later
but compiler will still require dummy initialization.
In some cases it can be optimized later,
in some this will be unnecessary overhead.

# Solutions

The most common solution for simple arrays is to use `MaybeUninit`:
```
let mut buf: MaybeUninit<[u8; 4]> = MaybeUninit::uninit();
let mut_ref = unsafe { &mut *buf.as_mut_ptr() };
// Initialize mut_ref
let buf = unsafe { buf.assume_init() };
```

For vectors can also construct slice from raw parts:
```
let mut buf: Vec<u8> = ...;

let old_len = buf.len();
buf.reserve(data.len());

unsafe {
    let s = std::slice::from_raw_parts_mut(
        buf.as_mut_ptr().add(old_len),  // Or buf.spare_capacity_mut()
        data.len()
    );
}

// Initialize s

unsafe {
    buf.set_len(len + data.len());
}
```
or can use (safe)
```
buf.spare_capacity_mut()[idx].write(...)
```
to avoid constucting `&mut` to uninitialized memory which may be UB ?

Note that it's UB to access data before it's initialized (e.g. call `Vec::set_len` on it).

# TODO

It's not clear how to benchmark Rust without initialization but we can benchmark GCC (via `-ftrivial-auto-var-init=zero`)

Is it UB to construct `&mut [T]` on uninitialized part of `Vec` for the purpose of initializing it ?

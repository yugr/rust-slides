This is a collection of performance improvements in Rust stdlib.

Associative containers (`BTreeSet`, `HashSet`) are much faster than C++.

Rust encapsulation rules allow library authors to hide details of their types.
This allows returning values of internal types on stack, rather than
allocating them on heap. One example of this is IO in stdlib -
unlike C (which returns heap-allocated `FILE *`) Rust just returns `File` by value.
Of course this prohibits dynamic update of shared stdlib (if it's ever used in future)
(without recompiling the whole world).

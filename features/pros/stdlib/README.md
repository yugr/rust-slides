This is a collection of performance improvements in Rust stdlib.

Associative containers (`BTreeSet`, `HashSet`) are much faster than C++.
Same goes for regexes (`std::regex` is known to be very slow).

Sort implementations are [significantly faster](https://github.com/Voultapher/sort-research-rs/blob/main/writeup/sort_safety/text.md)
despite doing more work due to safety guarantees.

Rust encapsulation rules allow library authors to hide details of their types.
This allows returning values of internal types on stack, rather than
allocating them on heap. One example of this is IO in stdlib -
unlike C (which returns heap-allocated `FILE *`) Rust just returns `File` by value.
Of course this prohibits dynamic update of shared stdlib (if it's ever used in future)
(without recompiling the whole world).

Rust associative containers allow find-or-insert-like method
(entry methods) which are faster than C++
```
it = map.find(...);
if (it == map.end())
  map.insert(...);
```

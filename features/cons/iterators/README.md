Iterators are great but in some cases do not optimize very well.

Main benefit of iterators is that they are implemented via `unsafe`
and do not have bounds checks.
So in _some_ cases iterators are faster than indexing but that's not always the case:
> Others have touched on how the “miracle” of zero cost abstraction has a limit.
> In my limited experience, flat_map is usually that limit,
> not to mention flat_map sandwiched by chunk and flatten.
> The nested computation would obscure useful properties
> of your data structures from the optimizer.
> This is not a Rust only problem. Even Haskell,
> the language making most use of flat_map (they call it bind),
> has a hard time optimizing them all away. 
(from [here](https://www.reddit.com/r/rust/comments/yaft60/zerocost_iterator_abstractionsnot_so_zerocost/)).
One example of this is `collect` which may preallocate result if size is known
(via optional `Iterator::size_hint` method).

Iterators are _much_ slower in debug.

In particular _interior iteration_ (`for_each` w/ lambda, aka "internal iteration"
or "push iteration) is [known](https://github.com/rust-lang/rust/issues/101814#issuecomment-1247184222)
to optimize better than traditional for-loops ("external iteration", "pull iteration").

Slice iterators do not require `Copy`able types so work on references.
As shown in [upstream #106539](https://github.com/rust-lang/rust/issues/106539)
this may cause overhead because LLVM fails to optimize code with derefs well (e.g. does not autovec).
So a [suggested guideline](https://github.com/nnethercote/perf-book/issues/83)
is to forcedly copy elements via `copied()`.

# Solutions

## Using for_each for chained iterators

Internal iteration is [definitely](https://users.rust-lang.org/t/noob-chaining-efficiency/65355/8)
[recommended](https://users.rust-lang.org/t/are-iterators-even-efficient/36050/2)
for "chained" iterators i.e. combinators that change the control flow
(`flat_map`, `flatten`, `chain`, [RangeInclusive](https://stackoverflow.com/a/70680224/2170527),
[iproduct!](https://users.rust-lang.org/t/why-are-cartesian-iterators-slower-than-nested-fors/42847),
[skip, skip_while](https://internals.rust-lang.org/t/about-optimizations-of-for-loops/18896)
and some others). The logic is
> For loop: When using a chain iterator in a for loop,
> you're repeatedly calling next. This means that
> the code will have to check if you're in the first or second half for every iteration.
>
> for_each: When using for_each, the custom implementation of
> for_each for the chain iterator will simply generate two loops,
> one after the other, so there is no need to check which half you're in for every iteration.
(i.e. `for_each` has unswitched loops internally).

Unfortunately `for_each` does not allow for complex control flow (`continue`, `break`).

## Replace containers with slices

As explained [here](https://internals.rust-lang.org/t/what-additional-performance-overhead-does-the-use-of-iterators-and-closures-cause/20296/16)
using slice instead of Vec iteration may simplify work for LLVM.

## Do not use inclusive ranges

See [overflow page](../arithmetic-checks/overflow-checks/README.md) for details.
Similar to "Using for_each for chained iterators" above.

This may be fixed as part of [RFC 3550](https://github.com/rust-lang/rfcs/pull/3550)
which changes `RangeInclusive` to be `IntoIterator` and
internally changing `x..=y` to `x..(y + 1)` in `RangeInclusive::into_iter`
but that's only for 2027 edition and also not clear there may be code bloat.

# TODO

- Scan stdlib for iterator specializations (e.g. `with_capacity` for `collect<Vec>`)

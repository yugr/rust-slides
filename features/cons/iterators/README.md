Iterators are great but in some cases do not optimize very well.

In some cases iterators are faster than indexing but that's not always the case.

Iterators are _much_ slower in debug.

In particular _exterior iteration_ (`for_each` w/ lambda, aka "external iteration")
is [known](https://github.com/rust-lang/rust/issues/101814#issuecomment-1247184222)
to optimize better than traditional for-loops.

# Solutions

## Using for_each for chained iterators

External iteration is [definitely](https://users.rust-lang.org/t/noob-chaining-efficiency/65355/8)
[recommended](https://users.rust-lang.org/t/are-iterators-even-efficient/36050/2)
for "chained" iterators i.e. combinators that change the control flow
(`flat_map`, `flatten`, `chain` and some others). The logic is
> For loop: When using a chain iterator in a for loop,
> you're repeatedly calling next. This means that
> the code will have to check if you're in the first or second half for every iteration.
>
> for_each: When using for_each, the custom implementation of
> for_each for the chain iterator will simply generate two loops,
> one after the other, so there is no need to check which half you're in for every iteration.
(i.e. `for_each` has unswitched loops internally).

## Replace containers with slices

As explained [here](https://internals.rust-lang.org/t/what-additional-performance-overhead-does-the-use-of-iterators-and-closures-cause/20296/16)
using slice instead of Vec iteration may simplify work for LLVM.

## Do not use inclusive ranges

See [overflow page](../arithmetic-checks/overflow-checks/README.md) for details.

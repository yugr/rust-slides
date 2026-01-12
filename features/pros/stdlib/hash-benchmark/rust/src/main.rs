use std::collections::HashMap;
use ahash::RandomState;
use fxhash::FxBuildHasher;

fn main() {
    #[cfg(feature = "sip")]
    let mut m = HashMap::new();
    #[cfg(feature = "ahash")]
    let mut m = HashMap::with_hasher(RandomState::new());
    #[cfg(feature = "fxhash")]
    let mut m = HashMap::with_hasher(FxBuildHasher::new());

    for i in 0..200_000_000 {
        *m.entry(i % 100_000).or_insert(0) += 1;
    }

    println!("{}", m[&40000]);
}

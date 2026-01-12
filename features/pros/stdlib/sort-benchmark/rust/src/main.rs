use rand_mt::Mt;

use std::cmp::Ordering;
use std::hint::black_box;
use std::time::SystemTime;
use std::mem::size_of;

static mut CALLS: usize = 0;

#[derive(Clone)]
struct T {
    a: u32,
    b: u32,
}

impl T {
    fn new() -> T {
        T { a: 0, b: 0 }
    }
}

impl PartialEq for T {
    #[inline]
    fn eq(&self, other: &T) -> bool {
        return self.a == other.a && self.b == other.b
    }
}

impl Eq for T {
}

impl PartialOrd for T {
    #[inline]
    fn partial_cmp(&self, other: &T) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for T {
    #[inline]
    fn cmp(&self, other: &T) -> Ordering {
        unsafe { CALLS += 1 }
        if self.a < other.a {
            Ordering::Less
        } else if self.a == other.a && self.b < other.b {
            Ordering::Less
        } else if self == other {
            Ordering::Equal
        } else {
            Ordering::Greater
        }
    }
}

const N: usize = 1024usize * 1024usize * 1024usize / size_of::<T>();

fn main() {
    let mut vals = vec![T::new(); N];

    {
        // Matches C++
        let seed = 0;
        let mut rng = Mt::new(seed);
        for val in vals.iter_mut() {
            *val = T { a: rng.next_u32() % 100, b: rng.next_u32() % 100 };
        }
    }

    let start = SystemTime::now().duration_since(SystemTime::UNIX_EPOCH).unwrap();
    vals.sort_unstable();
    let end = SystemTime::now().duration_since(SystemTime::UNIX_EPOCH).unwrap();

    println!("Elapsed: {:?} ({} calls)", end - start, unsafe { CALLS });

    black_box(vals);
}

#include <algorithm>
#include <chrono>
#include <random>
#include <vector>

#include <stdio.h>

using namespace std::literals;

size_t calls = 0;

struct T {
  unsigned a, b;
  T(): a(0), b(0) {}
  bool operator <(const T &rhs) const {
    ++calls;
    if (a < rhs.a)
      return true;
    else if (a == rhs.a && b < rhs.b)
      return true;
    else
      return false;
  }
};

static constexpr size_t N = 1024ull * 1024 * 1024 / sizeof(T);

int main() {
  std::vector<T> vals(N);

  {
    // Matches Rust
    const unsigned seed = 0;
    std::mt19937 gen(seed);
    for (auto &val : vals) {
      val.a = gen() % 100;
      val.b = gen() % 100;
    }
  }

  auto start = std::chrono::high_resolution_clock::now();
  std::sort(vals.begin(), vals.end());
  asm volatile("" :: "m"(vals));
  auto end = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double, std::milli> elapsed = end - start;

  printf("Elapsed: %g s (%zu calls)\n", elapsed / 1s, calls);
  return 0;
}


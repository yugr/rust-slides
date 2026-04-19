#include <assert.h>
#include <math.h>
#include <limits.h>

#include <vector>
#include <string>
#include <iostream>
#include <algorithm>
#include <unordered_map>
#include <unordered_set>
#include <set>
#include <map>
#include <algorithm>
#include <queue>

using namespace std;

template <typename A, typename B>
std::ostream &operator<<(std::ostream &os, const std::pair<A, B> &p) {
  os << "(" << p.first << ", " << p.second << ")";
  return os;
}

template <typename T,
          typename = decltype(std::declval<T &>().begin()),
          int = 1 / !is_same_v<T, std::string>>
std::ostream &operator<<(std::ostream &os, const T &c) {
  os << "[";
  for (auto i = c.begin(); i != c.end(); ++i)
    os << (i == c.begin() ? "" : ", ") << *i;
  os << "]";
  return os;
}

// reserve + push_back
class Solution_v0 {
public:
  string pushDominoes(string dominoes) {
    const int n = dominoes.size();

    string ans;
    ans.reserve(n);

    char prev = '.';
    int j = 0;

    // [0, j) are dominoes with decided positions
    // and len(ans) == j
    // and previously set value is prev

    for (int i = 0; i < n; ++i) {
      assert(j <= i);

      const char c = dominoes[i];

      if (c == '.')
        continue;

      if (c == 'L') {
        if (prev != 'R') {
          // [j, i] fall left
          for (; j <= i; ++j)
            ans.push_back('L');
        } else {
          int w = i - j;  // Do not include i (it's fixed)
          int w2 = w / 2;
          // Left half falls right
          for (int k = 0; k < w2; ++k)
            ans.push_back('R');
          if (w & 1)
            ans.push_back('.');
          // Right half falls left
          for (int k = 0; k < w2; ++k)
            ans.push_back('L');
          ans.push_back(c);
          j = i + 1;
        }
      } else {  // 'R'
        switch (prev) {
          case '.':
          case 'L':
            for (; j < i; ++j)
              ans.push_back('.');
            break;
          case 'R':
            for (; j < i; ++j)
              ans.push_back('R');
            break;
        }
        ++j;
        ans.push_back(c);
      }

      assert(ans.size() == j);

      prev = c;
    }

    switch (prev) {
      case '.':
      case 'L':
        prev = '.';
        break;
      case 'R':
        prev = 'R';
        break;
    }

    for (; j < n; ++j)
      ans.push_back(prev);

    return ans;
  }
};

// reserve + resize
class Solution_v1 {
public:
  string pushDominoes(string dominoes) {
    const int n = dominoes.size();

    string ans;
    ans.reserve(n);

    char prev = '.';
    int j = 0;

    // [0, j) are dominoes with decided positions
    // and len(ans) == j
    // and previously set value is prev

    for (int i = 0; i < n; ++i) {
      assert(j <= i);

      const char c = dominoes[i];

      if (c == '.')
        continue;

      if (c == 'L') {
        if (prev != 'R') {
          // [j, i] fall left
          ans.resize(i + 1, 'L');
          j = i + 1;
        } else {
          int w = i - j;  // Do not include i (it's fixed)
          int w2 = w / 2;
          // Left half falls right
          ans.resize(j + w2, 'R');
          if (w & 1)
            ans.push_back('.');
          // Right half falls left
          ans.resize(j + w, 'L');
          ans.push_back(c);
          j = i + 1;
        }
      } else {  // 'R'
        switch (prev) {
          case '.':
          case 'L':
            ans.resize(i, '.');
            j = i;
            break;
          case 'R':
            ans.resize(i, 'R');
            j = i;
            break;
        }
        ++j;
        ans.push_back(c);
      }

      assert(ans.size() == j);

      prev = c;
    }

    switch (prev) {
      case '.':
      case 'L':
        prev = '.';
        break;
      case 'R':
        prev = 'R';
        break;
    }

    ans.resize(n, prev);

    return ans;
  }
};

// resize + []
class Solution_v2 {
public:
  string pushDominoes(string dominoes) {
    const int n = dominoes.size();

    string ans(n, '?');

    char prev = '.';
    int j = 0;

    // [0, j) are dominoes with decided positions
    // and len(ans) == j
    // and previously set value is prev

    for (int i = 0; i < n; ++i) {
      assert(j <= i);

      const char c = dominoes[i];

      if (c == '.')
        continue;

      if (c == 'L') {
        if (prev != 'R') {
          // [j, i] fall left
          for (; j <= i; ++j)
            ans[j] = 'L';
        } else {
          int w = i - j;  // Do not include i (it's fixed)
          int w2 = w / 2;
          // Left half falls right
          for (int k = 0; k < w2; ++k, ++j)
            ans[j] = 'R';
          if (w & 1)
            ans[j++] = '.';
          // Right half falls left
          for (int k = 0; k < w2; ++k, ++j)
            ans[j] = 'L';
          ans[j++] = c;
        }
      } else {  // 'R'
        switch (prev) {
          case '.':
          case 'L':
            for (; j < i; ++j)
              ans[j] = '.';
            break;
          case 'R':
            for (; j < i; ++j)
              ans[j] = 'R';
            break;
        }
        ans[j++] = c;
      }

      prev = c;
    }

    switch (prev) {
      case '.':
      case 'L':
        prev = '.';
        break;
      case 'R':
        prev = 'R';
        break;
    }

    for (; j < n; ++j)
      ans[j] = prev;

    return ans;
  }
};

int main(int argc, char *argv[]) {
  if (argc != 2) {
    cerr << "Usage: prog.exe ALG_TYPE\n";
    exit(1);
  }

  int type = atoi(argv[1]);

  srand(0);

  const int max_size = 1024 * 1024 * 100;
  static char dirs[] = "LR.";

  std::string test(max_size, '?');
  for (int i = 0; i < max_size; ++i)
    test[i] = dirs[rand() % 3];

  switch (type) {
    case 0: {
      Solution_v0 sol;
      auto ans = sol.pushDominoes(test);
      break;
    }
    case 1: {
      Solution_v1 sol;
      auto ans = sol.pushDominoes(test);
      break;
    }
    case 2: {
      Solution_v2 sol;
      auto ans = sol.pushDominoes(test);
      break;
    }
  }

  cout << "SUCCESS\n";

  return 0;
}

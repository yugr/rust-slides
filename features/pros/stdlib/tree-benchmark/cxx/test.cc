#include <iostream>
#include <ctime>
#include <map>

static constexpr size_t MAX = 10000000;

int main() {
    clock_t start = clock(); 

    std::map<size_t, size_t> m;
    for (int i = 0; i < MAX; ++i) {
        m[2*i] = i;
    }

    size_t result = 0;
    for (int i = 0; i < MAX; ++i) {
        auto it = m.find(i);
        if (it != m.end())
            result += it->second;
    }

    std::cout << result << " " << float(clock() - start)
        / CLOCKS_PER_SEC << " s\n";

    return 0;
}

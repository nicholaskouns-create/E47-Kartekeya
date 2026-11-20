#include <algorithm>
#include <vector>

extern "C" void contract_batch(int n, int count, int steps, const int* rows,
                               const int* cols, const float* values,
                               const float* input, float* output) {
  std::vector<float> x(n), next(n);
  for (int sample = 0; sample < count; ++sample) {
    std::copy_n(input + sample * n, n, x.begin());
    for (int step = 0; step < steps; ++step) {
      for (int row = 0; row < n; ++row) {
        float total = 0;
        for (int i = rows[row]; i < rows[row + 1]; ++i) {
          total += values[i] * x[cols[i]];
        }
        next[row] = total;
      }
      x.swap(next);
    }
    std::copy(x.begin(), x.end(), output + sample * n);
  }
}

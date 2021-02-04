#pragma once

#include <cmath>
#include <functional>
#include <iostream>
#include <thread>
#include <vector>

namespace pst::parallelize {
void parallelize(size_t size, const std::function<void(size_t, size_t)> &fun) {
  const auto processor_count = std::thread::hardware_concurrency();
  std::vector<std::thread> threads{};
  float values_per_thread = float(size) / processor_count;

  for (size_t i = 0; i < processor_count; i++) {
    size_t start_index = std::floor(values_per_thread * i);
    size_t stop_index = std::ceil(values_per_thread * (i + 1.0));
    if (i == (processor_count - 1)) {
      stop_index = size;
    }
    threads.emplace_back(fun, start_index, stop_index);
  }

  for (auto &thread : threads) {
    if (thread.joinable()) {
      thread.join();
    }
  }
}

} // namespace pst::parallelize
#pragma once

#include <array>
#include <functional>
#include <numeric>
#include <queue>
#include <stack>
#include <tuple>
#include <vector>

#include <seqan3/alphabet/all.hpp>
#include <seqan3/alphabet/composite/alphabet_variant.hpp>
#include <seqan3/core/debug_stream.hpp>
#include <seqan3/range/container/bitcompressed_vector.hpp>
#include <seqan3/range/view/convert.hpp>

#include "lazy_suffix_tree/construction.hpp"
#include "lazy_suffix_tree/iteration.hpp"
#include "lazy_suffix_tree/suffix_links.hpp"

namespace lst {

template <seqan3::Alphabet alphabet_t = seqan3::dna5> class LazySuffixTree {

public:
  friend class LazySuffixTreeTest;

  LazySuffixTree() {}

  LazySuffixTree(seqan3::bitcompressed_vector<alphabet_t> &sequence_) {
    sequence = sequence_ | seqan3::view::convert<seqan3::gapped<alphabet_t>>;
    sequence.push_back(seqan3::gap{});

    suffixes = std::vector<int>(sequence.size());
    std::iota(suffixes.begin(), suffixes.end(), 0);

    lst::details::expand_root(sequence, suffixes, table, flags);
  }

  void expand_all() {
    for (int i = 0; i < table.size(); i++) {
      if (is_unevaluated(i)) {
        lst::details::expand_node(i, sequence, suffixes, table, flags);
      }
    }
  }

  std::vector<std::tuple<lst::details::sequence_t<alphabet_t>, int>>
  get_all_labels() {
    std::vector<std::tuple<lst::details::sequence_t<alphabet_t>, int>> labels{};

    lst::details::breadth_first_iteration(
        sequence, suffixes, table, flags,
        [&](int node_index, int lcp, int edge_lcp) -> bool {
          auto label = node_label(node_index, lcp, edge_lcp);
          int occurrences =
              lst::details::node_occurrences(node_index, table, flags);

          if (is_leaf(node_index)) {
            label = leaf_label(node_index, lcp);
          }

          if (label.size() != 0) {
            labels.emplace_back(label, occurrences);
          }
          return true;
        });

    return labels;
  }

  std::vector<int> search(std::vector<alphabet_t> pattern) {
    if (pattern.size() == 0) {
      std::vector<int> all_suffixes{};
      lst::details::iterate_children(0, table, flags, [&](int index) {
        auto suffixes = suffix_indicies(index, 0);
        all_suffixes.insert(all_suffixes.end(), suffixes.begin(),
                            suffixes.end());
      });
      return all_suffixes;
    }

    auto [node_index, lcp] = find(pattern);

    if (node_index == -1) {
      return std::vector<int>{};
    } else {
      return suffix_indicies(node_index, lcp);
    }
  }

  void
  breadth_first_traversal(const std::function<bool(int, int, int, int)> &f) {
    lst::details::breadth_first_iteration(
        sequence, suffixes, table, flags,
        [&](int node_index, int lcp, int edge_lcp) -> bool {
          int sequence_index = get_sequence_index(node_index);

          int node_start = sequence_index - lcp;
          int node_end = sequence_index + edge_lcp;

          if (is_leaf(node_index)) {
            node_end = suffixes.size() - 1;
          }
          int occurrences =
              lst::details::node_occurrences(node_index, table, flags);

          return f(node_start, node_end, edge_lcp, occurrences);
        });
  }

  void expand_implicit_nodes() {
    std::queue<int> queue{};
    queue.push(0);

    while (!queue.empty()) {
      int node_index = queue.front();
      queue.pop();

      if (is_unevaluated(node_index)) {
        continue;
      }

      if (!is_leaf(node_index)) {
        lst::details::iterate_children(node_index, table, flags,
                                       [&](int index) { queue.push(index); });
      }

      int edge_lcp = lst::details::get_edge_lcp(node_index, sequence, suffixes,
                                                table, flags);
      if (edge_lcp > 1) {
        lst::details::add_implicit_nodes(node_index, edge_lcp, table, flags);
      }
    }
  }

  void add_suffix_links() {
    suffix_links.resize(table.size() / 2, -1);
    std::fill(suffix_links.begin(), suffix_links.end(), -1);

    lst::details::add_explicit_suffix_links(sequence, suffixes, table, flags,
                                            suffix_links);
    lst::details::add_implicit_suffix_links(table, flags, suffix_links);
    suffix_links[0] = -1;
  }

  void add_reverse_suffix_links() {
    if (suffix_links.size() != table.size() / 2) {
      add_suffix_links();
    }

    reverse_suffix_links.resize(table.size() / 2);

    for (auto &reverses : reverse_suffix_links) {
      reverses.fill(-1);
    }

    lst::details::breadth_first_iteration(
        sequence, suffixes, table, flags, false,
        [&](int node_index, int lcp, int edge_lcp) -> bool {
          int sequence_index = get_sequence_index(node_index);
          int node_start = sequence_index - lcp;

          int suffix_parent = suffix_links[node_index / 2];

          int character_rank = seqan3::to_rank(this->sequence[node_start]);

          if (reverse_suffix_links[suffix_parent / 2][character_rank] == -1) {
            reverse_suffix_links[suffix_parent / 2][character_rank] =
                node_index;
          }
          return true;
        });
  }

  void print() {
    lst::details::breadth_first_iteration(
        sequence, suffixes, table, flags, false,
        [&](int node_index, int lcp, int edge_lcp) -> bool {
          auto label = node_label(node_index, lcp, edge_lcp);

          if (is_leaf(node_index)) {
            label = leaf_label(node_index, lcp);
          }

          seqan3::debug_stream << label << "\t" << node_index << "\t"
                               << table[node_index] << "\t"
                               << table[node_index + 1];

          if (suffix_links.size() > node_index / 2) {
            seqan3::debug_stream << "\t" << suffix_links[node_index / 2];
          }

          if (reverse_suffix_links.size() > node_index / 2) {
            seqan3::debug_stream << "\t"
                                 << reverse_suffix_links[node_index / 2];
          }

          seqan3::debug_stream << std::endl;
          return true;
        });
  }

protected:
  lst::details::sequence_t<alphabet_t> sequence;
  std::vector<int> suffixes{};
  std::vector<int> table{0, 2};
  std::vector<lst::details::Flag> flags{lst::details::Flag::RightMostChild,
                                        lst::details::Flag::None};
  std::vector<int> suffix_links{};
  std::vector<lst::details::alphabet_array<alphabet_t>> reverse_suffix_links{};

  std::vector<int> suffix_indicies(int node_index, int og_lcp) {
    if (node_index >= table.size()) {
      throw std::invalid_argument(
          "[SUFFIX INDICIES] Given node index is too large.");
    }

    std::vector<int> start_indicies{};
    std::queue<std::tuple<int, int>> queue{};

    queue.emplace(node_index, og_lcp);

    while (!queue.empty()) {
      auto [index, lcp] = queue.front();
      queue.pop();

      if (is_leaf(index)) {
        start_indicies.push_back(table[index] - lcp);
      } else if (is_unevaluated(index)) {
        for (int i = table[index]; i < table[index + 1]; i++) {
          start_indicies.push_back(suffixes[i] - lcp);
        }
      } else {
        int edge_lcp =
            lst::details::get_edge_lcp(index, sequence, suffixes, table, flags);
        int new_lcp = lcp + edge_lcp;
        lst::details::iterate_children(
            index, table, flags, [&](int i) { queue.emplace(i, new_lcp); });
      }
    }

    return start_indicies;
  }

  std::tuple<int, int> find(std::vector<alphabet_t> pattern) {
    std::queue<std::tuple<int, int>> queue{};

    queue.emplace(0, 0);

    int pattern_lcp = 0;

    while (!queue.empty()) {
      auto [node_index, lcp] = queue.front();
      queue.pop();

      int edge_lcp;
      if (is_unevaluated(node_index)) {
        edge_lcp = lst::details::expand_node(node_index, sequence, suffixes,
                                             table, flags);
      } else {
        edge_lcp = lst::details::get_edge_lcp(node_index, sequence, suffixes,
                                              table, flags);
      }

      lst::details::sequence_t<alphabet_t> edge =
          edge_label(node_index, edge_lcp);

      bool edge_match = edge_matches(node_index, pattern_lcp, pattern, edge);

      if (!edge_match) {
        continue;
      }

      pattern_lcp += edge.size();
      if (pattern_lcp >= pattern.size()) {
        return std::make_tuple(node_index, lcp);
      }

      empty_queue(queue);

      if (!is_leaf(node_index)) {
        int new_lcp = lcp + edge_lcp;
        lst::details::iterate_children(
            node_index, table, flags,
            [&](int index) { queue.emplace(index, new_lcp); });
      }
    }

    return std::make_tuple(-1, -1);
  }

  template <typename T> void empty_queue(std::queue<T> &queue) {
    while (!queue.empty()) {
      queue.pop();
    }
  }

  bool edge_matches(int node_index, int pattern_lcp,
                    std::vector<alphabet_t> &pattern,
                    lst::details::sequence_t<alphabet_t> &edge) {
    for (int i = 0; pattern_lcp + i < pattern.size() && i < edge.size(); i++) {
      int sequence_index = table[node_index] + i;

      if (sequence[sequence_index] != pattern[pattern_lcp + i]) {
        return false;
      }
    }

    return true;
  }

  lst::details::sequence_t<alphabet_t> edge_label(int node_index,
                                                  int edge_lcp) {
    int edge_start = get_sequence_index(node_index);
    lst::details::sequence_t<alphabet_t> edge(sequence.begin() + edge_start,
                                              sequence.begin() + edge_start +
                                                  edge_lcp);

    return edge;
  }

  lst::details::sequence_t<alphabet_t> node_label(int node_index, int lcp,
                                                  int edge_lcp) {
    int sequence_index = get_sequence_index(node_index);

    int node_start = sequence_index - lcp;
    int node_end = sequence_index + edge_lcp;
    lst::details::sequence_t<alphabet_t> label(sequence.begin() + node_start,
                                               sequence.begin() + node_end);

    return label;
  }

  lst::details::sequence_t<alphabet_t> leaf_label(int node_index, int lcp) {
    int node_start = table[node_index] - lcp;
    lst::details::sequence_t<alphabet_t> label(sequence.begin() + node_start,
                                               sequence.end());

    return label;
  }

  int get_sequence_index(int node_index) {
    if (is_unevaluated(node_index)) {
      return suffixes[table[node_index]];
    } else {
      return table[node_index];
    }
  }

  bool is_leaf(int node_index) {
    return lst::details::is_leaf(node_index, flags);
  }

  bool is_unevaluated(int node_index) {
    return lst::details::is_unevaluated(node_index, flags);
  }

  bool is_rightmostchild(int node_index) {
    return lst::details::is_rightmostchild(node_index, flags);
  }
};
} // namespace lst

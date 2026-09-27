/// Merges overlapping intervals.
List<List<int>> mergeIntervals(List<List<int>> intervals) {
  if (intervals.isEmpty) return [];

  intervals.sort((a, b) => a[0].compareTo(b[0]));
  List<List<int>> merged = [intervals[0]];

  for (int i = 1; i < intervals.length; i++) {
    List<int> last = merged.last;
    if (intervals[i][0] <= last[1]) {
      last[1] = last[1] > intervals[i][1] ? last[1] : intervals[i][1];
    } else {
      merged.add(intervals[i]);
    }
  }

  return merged;
}
 // updated 1790507389

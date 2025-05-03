List<int> fibonacci(int n) {
  List<int> seq = [0, 1];
  for (int i = 2; i < n; i++) {
    seq.add(seq[i - 1] + seq[i - 2]);
  }
  return seq;
}

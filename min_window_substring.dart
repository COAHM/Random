/// Finds the minimum window substring that contains all characters of [t] in [s].
String minWindow(String s, String t) {
  if (t.isEmpty || s.length < t.length) return "";

  Map<String, int> need = {};
  for (int i = 0; i < t.length; i++) {
    need[t[i]] = (need[t[i]] ?? 0) + 1;
  }

  Map<String, int> window = {};
  int have = 0, needSize = need.length;
  int left = 0, minLen = s.length + 1, minStart = 0;

  for (int right = 0; right < s.length; right++) {
    String char = s[right];
    window[char] = (window[char] ?? 0) + 1;

    if (need.containsKey(char) && window[char] == need[char]) {
      have++;
    }

    while (have == needSize) {
      if (right - left + 1 < minLen) {
        minStart = left;
        minLen = right - left + 1;
      }

      String leftChar = s[left];
      window[leftChar] = window[leftChar]! - 1;
      if (need.containsKey(leftChar) && window[leftChar]! < need[leftChar]!) {
        have--;
      }
      left++;
    }
  }

  return minLen > s.length ? "" : s.substring(minStart, minStart + minLen);
}
 // updated 1781782685

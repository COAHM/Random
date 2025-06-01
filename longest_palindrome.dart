/// Finds the longest palindromic substring in a given string.
String longestPalindrome(String s) {
  if (s.length < 2) return s;
  int start = 0, maxLen = 1;

  for (int i = 1; i < s.length; i++) {
    int low = i - 1, high = i;

    while (low >= 0 && high < s.length && s[low] == s[high]) {
      if (high - low + 1 > maxLen) {
        start = low;
        maxLen = high - low + 1;
      }
      low--;
      high++;
    }

    low = i - 1;
    high = i + 1;

    while (low >= 0 && high < s.length && s[low] == s[high]) {
      if (high - low + 1 > maxLen) {
        start = low;
        maxLen = high - low + 1;
      }
      low--;
      high++;
    }
  }

  return s.substring(start, start + maxLen);
}
 // updated 1748792371

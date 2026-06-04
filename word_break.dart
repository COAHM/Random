/// Returns true if the string can be segmented using the word dictionary.
bool wordBreak(String s, List<String> wordDict) {
  Set<String> dict = wordDict.toSet();
  List<bool> dp = List.filled(s.length + 1, false);
  dp[0] = true;

  for (int i = 1; i <= s.length; i++) {
    for (int j = 0; j < i; j++) {
      if (dp[j] && dict.contains(s.substring(j, i))) {
        dp[i] = true;
        break;
      }
    }
  }

  return dp[s.length];
}
 // updated 1780571238

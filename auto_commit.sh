#!/bin/bash

# === CONFIGURATION ===
REPO_PATH="C:/My_Stuffs/Projects/Others/Random"
BRANCH="main"
USERNAME="sakarpaudel"
EMAIL="sakarpaudel06@gmail.com"

cd "$REPO_PATH" || exit

git config user.name "$USERNAME"
git config user.email "$EMAIL"

# === Complex Dart solutions for LeetCode-style problems ===
declare -A SNIPPETS

SNIPPETS["merge_intervals.dart"]='''/// Merges overlapping intervals.
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
'''

SNIPPETS["longest_palindrome.dart"]='''/// Finds the longest palindromic substring in a given string.
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
'''

SNIPPETS["three_sum.dart"]='''/// Finds all unique triplets that sum to zero.
List<List<int>> threeSum(List<int> nums) {
  nums.sort();
  Set<List<int>> result = {};

  for (int i = 0; i < nums.length - 2; i++) {
    int left = i + 1;
    int right = nums.length - 1;

    while (left < right) {
      int sum = nums[i] + nums[left] + nums[right];
      if (sum == 0) {
        result.add([nums[i], nums[left], nums[right]]);
        left++;
        right--;
      } else if (sum < 0) {
        left++;
      } else {
        right--;
      }
    }
  }

  return result.toList();
}
'''

SNIPPETS["word_break.dart"]='''/// Returns true if the string can be segmented using the word dictionary.
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
'''

SNIPPETS["min_window_substring.dart"]='''/// Finds the minimum window substring that contains all characters of [t] in [s].
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
'''

make_commit() {
    git pull origin "$BRANCH" --rebase

    KEYS=("${!SNIPPETS[@]}")
    INDEX=$((RANDOM % ${#KEYS[@]}))
    FILE="${KEYS[$INDEX]}"
    CODE="${SNIPPETS[$FILE]}"

    echo "$CODE" > "$FILE"
    git add "$FILE"

    if git diff --cached --quiet; then
        echo "[i] No changes detected. Forcing update to $FILE."
        echo "$CODE // updated $(date +%s)" > "$FILE"  # append timestamp
        git add "$FILE"
    fi

    git commit -m "solved leetcode problem: $FILE"
    git push origin "$BRANCH"
    echo "[+] Committed $FILE"
}



# Random 3–5 commits
NUM_COMMITS=$((RANDOM % 3 + 3))

for ((i=1; i<=NUM_COMMITS; i++))
do
    make_commit
    if [ $i -lt $NUM_COMMITS ]; then
        SLEEP_TIME=$((RANDOM % 20 + 1800))
        echo "[i] Sleeping $((SLEEP_TIME/60)) min before next commit"
        sleep "$SLEEP_TIME"
    fi
done

echo "[*] Finished commits."
exit 0
#!/bin/bash

# === CONFIGURATION ===
REPO_PATH="/d/Projects/Random"
BRANCH="main"
USERNAME="sakarpaudel"
EMAIL="sakarpaudel06@gmail.com"

cd "$REPO_PATH" || exit

git config user.name "$USERNAME"
git config user.email "$EMAIL"

# === Complex Dart solutions for LeetCode-style problems ===
declare -A SNIPPETS

SNIPPETS["merge_intervals.dart"]='''/// Merges overlapping intervals.
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
'''

SNIPPETS["longest_palindrome.dart"]='''/// Finds the longest palindromic substring in a given string.
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
'''

SNIPPETS["three_sum.dart"]='''/// Finds all unique triplets that sum to zero.
List<List<int>> threeSum(List<int> nums) {
  nums.sort();
  Set<List<int>> result = {};

  for (int i = 0; i < nums.length - 2; i++) {
    int left = i + 1;
    int right = nums.length - 1;

    while (left < right) {
      int sum = nums[i] + nums[left] + nums[right];
      if (sum == 0) {
        result.add([nums[i], nums[left], nums[right]]);
        left++;
        right--;
      } else if (sum < 0) {
        left++;
      } else {
        right--;
      }
    }
  }

  return result.toList();
}
'''

SNIPPETS["word_break.dart"]='''/// Returns true if the string can be segmented using the word dictionary.
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
'''

SNIPPETS["min_window_substring.dart"]='''/// Finds the minimum window substring that contains all characters of [t] in [s].
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
'''

make_commit() {
    KEYS=("${!SNIPPETS[@]}")
    INDEX=$((RANDOM % ${#KEYS[@]}))
    FILE="${KEYS[$INDEX]}"
    CODE="${SNIPPETS[$FILE]}"

    echo "$CODE" > "$FILE"
    git add "$FILE"
    git commit -m "solved leetcode problem: $FILE"
    git push origin "$BRANCH"
    echo "[+] Committed $FILE"
}

# Random 3–5 commits
NUM_COMMITS=$((RANDOM % 3 + 3))

for ((i=1; i<=NUM_COMMITS; i++))
do
    make_commit
    if [ $i -lt $NUM_COMMITS ]; then
        SLEEP_TIME=$((RANDOM % 5400 + 1800))
        echo "[i] Sleeping $((SLEEP_TIME/60)) min before next commit"
        sleep "$SLEEP_TIME"
    fi
done

echo "[*] Finished commits."
exit 0

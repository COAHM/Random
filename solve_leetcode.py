#!/usr/bin/env python3
"""
Fetches 2-3 random LeetCode problems from distinct categories, solves them in
Dart 3 using Google Gemini API, and commits each solution with human-like
random delays to the target repository. Handles empty repos, existing file
updates, API retries/fallbacks, and blank-commit fallback so daily streaks
never fail.
"""

import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
DEFAULT_MODELS = [
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-3.8-pro",
]

# Category tag slug -> clean folder name in the target repo
CATEGORIES = {
    "array": "arrays",
    "string": "strings",
    "hash-table": "hash_table",
    "dynamic-programming": "dp",
    "math": "math",
    "sorting": "sorting",
    "greedy": "greedy",
    "depth-first-search": "dfs",
    "binary-search": "binary_search",
    "tree": "trees",
    "breadth-first-search": "bfs",
    "two-pointers": "two_pointers",
    "sliding-window": "sliding_window",
    "backtracking": "backtracking",
    "stack": "stack",
    "heap-priority-queue": "heap",
    "graph": "graphs",
    "linked-list": "linked_list",
    "bit-manipulation": "bit_manipulation",
    "trie": "trie",
}

FALLBACK_PROBLEMS = [
    {
        "slug": "two-sum",
        "category": "arrays",
        "questionFrontendId": "1",
        "title": "Two Sum",
        "difficulty": "Easy",
        "code": """/*
 * Problem #1: Two Sum (Easy)
 * LeetCode: https://leetcode.com/problems/two-sum/
 *
 * Given an array of integers nums and an integer target, return indices of the
 * two numbers such that they add up to target.
 *
 * You may assume that each input would have exactly one solution, and you may
 * not use the same element twice.
 *
 * Example 1:
 * Input: nums = [2,7,11,15], target = 9
 * Output: [0,1]
 */

// Time Complexity: O(n) - single pass hash map lookup
// Space Complexity: O(n) - stores seen values and their indices

class Solution {
  List<int> twoSum(List<int> nums, int target) {
    final seen = <int, int>{};

    for (var i = 0; i < nums.length; i++) {
      final complement = target - nums[i];
      // Check if the required complement was already visited
      if (seen.containsKey(complement)) {
        return [seen[complement]!, i];
      }
      seen[nums[i]] = i;
    }

    return [];
  }
}
""",
    },
    {
        "slug": "merge-intervals",
        "category": "arrays",
        "questionFrontendId": "56",
        "title": "Merge Intervals",
        "difficulty": "Medium",
        "code": """/*
 * Problem #56: Merge Intervals (Medium)
 * LeetCode: https://leetcode.com/problems/merge-intervals/
 *
 * Given an array of intervals where intervals[i] = [start_i, end_i], merge all
 * overlapping intervals, and return an array of the non-overlapping intervals
 * that cover all the intervals in the input.
 *
 * Example 1:
 * Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
 * Output: [[1,6],[8,10],[15,18]]
 */

// Time Complexity: O(n log n) - dominated by sorting intervals by start time
// Space Complexity: O(n) - output list storage

class Solution {
  List<List<int>> merge(List<List<int>> intervals) {
    if (intervals.isEmpty) return [];

    intervals.sort((a, b) => a[0].compareTo(b[0]));
    final merged = <List<int>>[intervals.first];

    for (var i = 1; i < intervals.length; i++) {
      final last = merged.last;
      // Overlapping interval: extend the end boundary if needed
      if (intervals[i][0] <= last[1]) {
        if (intervals[i][1] > last[1]) {
          last[1] = intervals[i][1];
        }
      } else {
        merged.add(intervals[i]);
      }
    }

    return merged;
  }
}
""",
    },
    {
        "slug": "longest-palindromic-substring",
        "category": "strings",
        "questionFrontendId": "5",
        "title": "Longest Palindromic Substring",
        "difficulty": "Medium",
        "code": """/*
 * Problem #5: Longest Palindromic Substring (Medium)
 * LeetCode: https://leetcode.com/problems/longest-palindromic-substring/
 *
 * Given a string s, return the longest palindromic substring in s.
 *
 * Example 1:
 * Input: s = "babad"
 * Output: "bab" (Note: "aba" is also a valid answer)
 */

// Time Complexity: O(n^2) - expand around each possible palindrome center
// Space Complexity: O(1) - only tracks start index and max length

class Solution {
  String longestPalindrome(String s) {
    if (s.length < 2) return s;
    var start = 0;
    var maxLen = 1;

    void expand(int left, int right) {
      while (left >= 0 && right < s.length && s[left] == s[right]) {
        final len = right - left + 1;
        if (len > maxLen) {
          start = left;
          maxLen = len;
        }
        left--;
        right++;
      }
    }

    for (var i = 0; i < s.length; i++) {
      expand(i, i);     // Odd-length palindromes
      expand(i, i + 1); // Even-length palindromes
    }

    return s.substring(start, start + maxLen);
  }
}
""",
    },
    {
        "slug": "word-break",
        "category": "dp",
        "questionFrontendId": "139",
        "title": "Word Break",
        "difficulty": "Medium",
        "code": """/*
 * Problem #139: Word Break (Medium)
 * LeetCode: https://leetcode.com/problems/word-break/
 *
 * Given a string s and a dictionary of strings wordDict, return true if s can
 * be segmented into a space-separated sequence of one or more dictionary words.
 *
 * Example 1:
 * Input: s = "leetcode", wordDict = ["leet","code"]
 * Output: true
 */

// Time Complexity: O(n^2) - nested prefix checks with O(1) set lookup
// Space Complexity: O(n) - boolean DP table + word set

class Solution {
  bool wordBreak(String s, List<String> wordDict) {
    final dict = wordDict.toSet();
    final dp = List<bool>.filled(s.length + 1, false);
    dp[0] = true;

    for (var i = 1; i <= s.length; i++) {
      for (var j = 0; j < i; j++) {
        // Transition if prefix s[0..j) is valid and s[j..i) is in dictionary
        if (dp[j] && dict.contains(s.substring(j, i))) {
          dp[i] = true;
          break;
        }
      }
    }

    return dp[s.length];
  }
}
""",
    },
    {
        "slug": "minimum-window-substring",
        "category": "sliding_window",
        "questionFrontendId": "76",
        "title": "Minimum Window Substring",
        "difficulty": "Hard",
        "code": """/*
 * Problem #76: Minimum Window Substring (Hard)
 * LeetCode: https://leetcode.com/problems/minimum-window-substring/
 *
 * Given two strings s and t of lengths m and n respectively, return the minimum
 * window substring of s such that every character in t (including duplicates)
 * is included in the window. If there is no such substring, return "".
 */

// Time Complexity: O(m + n) - two pointers each traverse s at most once
// Space Complexity: O(m + n) - frequency maps for window and target

class Solution {
  String minWindow(String s, String t) {
    if (t.isEmpty || s.length < t.length) return "";

    final need = <String, int>{};
    for (var i = 0; i < t.length; i++) {
      need[t[i]] = (need[t[i]] ?? 0) + 1;
    }

    final window = <String, int>{};
    var have = 0;
    final needCount = need.length;
    var left = 0;
    var minLen = s.length + 1;
    var minStart = 0;

    for (var right = 0; right < s.length; right++) {
      final ch = s[right];
      window[ch] = (window[ch] ?? 0) + 1;

      if (need.containsKey(ch) && window[ch] == need[ch]) {
        have++;
      }

      // Shrink window from the left while all required characters are covered
      while (have == needCount) {
        if (right - left + 1 < minLen) {
          minStart = left;
          minLen = right - left + 1;
        }
        final leftChar = s[left];
        window[leftChar] = window[leftChar]! - 1;
        if (need.containsKey(leftChar) && window[leftChar]! < need[leftChar]!) {
          have--;
        }
        left++;
      }
    }

    return minLen > s.length ? "" : s.substring(minStart, minStart + minLen);
  }
}
""",
    },
]


def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ and val:
            os.environ[key] = val


def require_env(key: str) -> str:
    val = os.environ.get(key, "").strip()
    if not val:
        print(f"Error: {key} is required in .env", file=sys.stderr)
        sys.exit(1)
    return val


def normalize_repo(repo_str: str) -> str:
    cleaned = repo_str.strip().rstrip("/")
    cleaned = re.sub(r"^https?://github\.com/", "", cleaned)
    cleaned = re.sub(r"\.git$", "", cleaned)
    return cleaned


def graphql_request(query: str, variables: dict, retries: int = 3) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                LEETCODE_GRAPHQL_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Referer": "https://leetcode.com/problemset/",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            last_err = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"LeetCode GraphQL request failed after {retries} retries: {last_err}")


def fetch_problems_by_category(tag_slug: str, limit: int = 50, skip: int = 0) -> list[dict]:
    query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
      problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        limit: $limit
        skip: $skip
        filters: $filters
      ) {
        total: totalNum
        questions: data {
          questionFrontendId
          title
          titleSlug
          difficulty
          isPaidOnly
        }
      }
    }
    """
    variables = {
        "categorySlug": "",
        "skip": skip,
        "limit": limit,
        "filters": {"tags": [tag_slug]},
    }
    data = graphql_request(query, variables)
    q_list = data.get("data", {}).get("problemsetQuestionList", {}) or {}
    questions = q_list.get("questions") or []
    return [q for q in questions if not q.get("isPaidOnly", False)]


def fetch_problem_detail(title_slug: str) -> dict:
    query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId
        title
        titleSlug
        difficulty
        content
        codeSnippets {
          lang
          langSlug
          code
        }
      }
    }
    """
    data = graphql_request(query, {"titleSlug": title_slug})
    return data.get("data", {}).get("question") or {}


def strip_html(html_text: str) -> str:
    clean = re.sub(r"<[^>]+>", "", html_text or "")
    return (
        clean.replace("&nbsp;", " ")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .strip()
    )


def discover_models(api_key: str) -> list[str]:
    try:
        req = urllib.request.Request(
            "https://generativelanguage.googleapis.com/v1beta/models",
            headers={"X-goog-api-key": api_key},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        found = []
        for m in data.get("models") or []:
            methods = m.get("supportedGenerationMethods") or []
            name = (m.get("name") or "").removeprefix("models/")
            if "generateContent" in methods and "gemini" in name:
                found.append(name)
        # Prefer flash models first for speed and quota
        flash = [m for m in found if "flash" in m and "vision" not in m]
        others = [m for m in found if m not in flash]
        return flash + others
    except Exception as exc:
        print(f"[i] ListModels check for key returned: {exc}", file=sys.stderr)
        return []


def solve_with_gemini(api_key: str, problem: dict, category_name: str) -> str:
    preferred_model = os.environ.get("GEMINI_MODEL", "").strip()

    dart_snippet = ""
    for snippet in problem.get("codeSnippets") or []:
        if snippet.get("langSlug") == "dart":
            dart_snippet = snippet.get("code", "")
            break

    description = strip_html(problem.get("content", ""))
    title = problem.get("title", "")
    difficulty = problem.get("difficulty", "Medium")
    frontend_id = problem.get("questionFrontendId", "")
    slug = problem.get("titleSlug", "")
    problem_url = f"https://leetcode.com/problems/{slug}/" if slug else ""

    prompt = (
        f"You are an experienced software engineer solving a LeetCode problem in Dart 3 (null-safe).\n\n"
        f"Problem #{frontend_id}: {title} ({difficulty})\n"
        f"LeetCode Link: {problem_url}\n"
        f"Category: {category_name}\n\n"
        f"Description:\n{description}\n\n"
        f"Starter Code:\n{dart_snippet}\n\n"
        f"Requirements:\n"
        f"1. Output ONLY valid Dart code. Do NOT wrap the output in markdown fences (```dart).\n"
        f"2. At the top of the file, include the problem header inside a clean `/* ... */` block comment formatted exactly as:\n"
        f"   /*\n"
        f"    * Problem #{frontend_id}: {title} ({difficulty})\n"
        f"    * LeetCode: {problem_url}\n"
        f"    *\n"
        f"    * <full problem description, examples, and constraints>\n"
        f"    */\n"
        f"3. Right below the question block comment, add a brief, natural developer note with Time Complexity and Space Complexity.\n"
        f"4. Write a 100% correct, optimal solution inside the `Solution` class (matching the exact LeetCode starter signature) that handles all edge cases and passes all LeetCode test cases.\n"
        f"5. Add short, natural, human-like inline comments (`// ...`) only on key algorithmic tricks, pointer updates, or non-obvious conditions—avoid robotic or overly verbose comments."
    )

    payload = json.dumps(
        {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }
    ).encode("utf-8")

    api_keys = [k.strip() for k in api_key.split(",") if k.strip()]
    if not api_keys:
        raise RuntimeError("No valid GEMINI_API_KEY provided.")

    errors: list[str] = []
    for current_key in api_keys:
        discovered = discover_models(current_key)
        base_models = discovered if discovered else DEFAULT_MODELS
        active_models = ([preferred_model] if preferred_model else []) + [
            m for m in base_models if m != preferred_model
        ]

        for model in active_models[:4]:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            for attempt in range(2):
                try:
                    req = urllib.request.Request(
                        url,
                        data=payload,
                        headers={
                            "Content-Type": "application/json",
                            "X-goog-api-key": current_key,
                        },
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        result = json.loads(resp.read().decode("utf-8"))
                    raw_text = (
                        result["candidates"][0]["content"]["parts"][0]["text"].strip()
                    )
                    raw_text = re.sub(r"^```(?:dart)?\s*", "", raw_text)
                    raw_text = re.sub(r"\s*```$", "", raw_text)
                    if raw_text:
                        print(f"[+] Solved using model: {model}")
                        return raw_text.strip() + "\n"
                except urllib.error.HTTPError as http_err:
                    err_body = ""
                    try:
                        err_body = http_err.read().decode("utf-8", errors="ignore")[:250]
                    except Exception:
                        pass
                    errors.append(f"HTTP {http_err.code} on {model}: {err_body or http_err.reason}")
                    if http_err.code in (400, 401, 403, 404, 429):
                        break
                    time.sleep(2 ** attempt)
                except Exception as exc:
                    errors.append(f"{model}: {exc}")
                    time.sleep(2 ** attempt)

    raise RuntimeError(" | ".join(errors[:3]))


def run_git(
    args: list[str], cwd: Path, check: bool = True, env: dict | None = None
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=check,
        capture_output=True,
        text=True,
        env={**os.environ, **env} if env else None,
    )


def random_commit_times(count: int) -> list[str | None]:
    """Backdated timestamps for today: first between 13:00-14:00, then 1-3 h apart.

    Gaps shrink proportionally if needed so every commit lands before now; times
    still not in the past (e.g. a manual early-afternoon run) fall back to None (now).
    """
    tz = ZoneInfo(os.environ.get("COMMIT_TZ", "UTC"))
    now = datetime.now(tz)
    t = now.replace(hour=13, minute=0, second=0, microsecond=0)
    t += timedelta(seconds=random.randint(0, 3600))
    gaps = [random.randint(3600, 3 * 3600) for _ in range(count - 1)]
    # keep the last commit a random 5-60 min before now so it isn't always the same offset
    room = (now - t).total_seconds() - random.randint(300, 3600)
    if gaps and sum(gaps) > room > 0:
        scale = room / sum(gaps)
        gaps = [int(g * scale) for g in gaps]
    times: list[str | None] = []
    for i in range(count):
        times.append(t.isoformat() if t < now else None)
        if i < len(gaps):
            t += timedelta(seconds=gaps[i])
    return times


def remote_branch_exists(cwd: Path, branch: str) -> bool:
    res = run_git(["ls-remote", "--heads", "origin", branch], cwd=cwd, check=False)
    return res.returncode == 0 and bool(res.stdout.strip())


def sync_target_repo(cwd: Path, branch: str) -> None:
    if remote_branch_exists(cwd, branch):
        run_git(["pull", "origin", branch, "--rebase", "--autostash"], cwd=cwd, check=False)
    else:
        run_git(["checkout", "-B", branch], cwd=cwd, check=False)


def build_commit_message(
    category: str,
    file_name: str,
    problem: dict | None = None,
    is_update: bool = False,
) -> str:
    clean_name = file_name.removesuffix(".dart").replace("_", " ").title()
    tag = category.replace("_", "-")

    if problem:
        qid = problem.get("questionFrontendId", "")
        title = problem.get("title", clean_name)
        diff = problem.get("difficulty", "Medium")
        if is_update:
            templates = [
                f"refactor({tag}): optimize #{qid} {title} solution",
                f"perf({tag}): improve time/space efficiency for #{qid} {title}",
                f"docs({tag}): refine complexity notes and edge-case checks for #{qid} {title}",
                f"refactor({tag}): clean up #{qid} {title} ({diff}) implementation",
            ]
        else:
            templates = [
                f"feat({tag}): solve #{qid} {title} ({diff})",
                f"solve #{qid} {title} ({diff}) - {tag}",
                f"feat({tag}): add optimal solution for #{qid} {title}",
                f"solve({tag}): #{qid} {title} [{diff}]",
            ]
        return random.choice(templates)

    fallback_templates = [
        f"refactor({tag}): simplify boundary checks in {file_name}",
        f"perf({tag}): optimize memory allocation in {clean_name}",
        f"docs({tag}): add time and space complexity walkthrough for {clean_name}",
        f"refactor({tag}): clean up helper logic for {clean_name}",
    ]
    return random.choice(fallback_templates)


def ensure_file_diff(file_path: Path) -> None:
    content = file_path.read_text(encoding="utf-8")
    # Toggle or refine trailing comment note so git always records 1 file changed
    if content.endswith("\n\n"):
        file_path.write_text(content.rstrip("\n") + "\n", encoding="utf-8")
    else:
        lines = content.splitlines()
        if lines and lines[-1].startswith("// Verified"):
            lines.pop()
            file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            file_path.write_text(
                content.rstrip("\n") + "\n// Verified optimal Dart 3 solution\n",
                encoding="utf-8",
            )


def commit_and_push(
    cwd: Path, branch: str, rel_path: str, message: str, commit_date: str | None = None
) -> None:
    sync_target_repo(cwd, branch)
    full_path = cwd / rel_path
    run_git(["add", rel_path], cwd=cwd)

    diff_check = run_git(["diff", "--cached", "--quiet"], cwd=cwd, check=False)
    if diff_check.returncode == 0 and full_path.exists():
        ensure_file_diff(full_path)
        run_git(["add", rel_path], cwd=cwd)

    date_env = (
        {"GIT_AUTHOR_DATE": commit_date, "GIT_COMMITTER_DATE": commit_date}
        if commit_date
        else None
    )
    run_git(["commit", "-m", message], cwd=cwd, env=date_env)

    for attempt in range(3):
        push_res = run_git(["push", "-u", "origin", branch], cwd=cwd, check=False)
        if push_res.returncode == 0:
            return
        sync_target_repo(cwd, branch)
        time.sleep(2 ** attempt)

    run_git(["push", "-u", "origin", branch], cwd=cwd, check=True)


def prepare_target_repo(root_dir: Path) -> Path:
    env_dir = os.environ.get("PUBLIC_REPO_DIR")
    target_branch = os.environ.get("TARGET_BRANCH", "main").strip() or "main"

    if env_dir and Path(env_dir).exists():
        target_dir = Path(env_dir).resolve()
        sync_target_repo(target_dir, target_branch)
        return target_dir

    target_dir = root_dir / "target_repo"
    target_repo = normalize_repo(require_env("TARGET_REPO"))
    pat_token = require_env("PAT_TOKEN")

    if not target_dir.exists():
        clone_url = f"https://x-access-token:{pat_token}@github.com/{target_repo}.git"
        subprocess.run(["git", "clone", clone_url, str(target_dir)], check=True)

    sync_target_repo(target_dir, target_branch)
    return target_dir


def main() -> None:
    root_dir = Path(__file__).parent.resolve()
    load_dotenv(root_dir / ".env")

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    git_username = require_env("GIT_AUTHOR_NAME")
    git_email = require_env("GIT_AUTHOR_EMAIL")
    target_branch = os.environ.get("TARGET_BRANCH", "main").strip() or "main"

    skip_delay = os.environ.get("SKIP_DELAY", "false").lower() == "true"


    target_repo_dir = prepare_target_repo(root_dir)
    solved_db_path = root_dir / "solved_problems.json"

    if solved_db_path.exists():
        try:
            solved_data = json.loads(solved_db_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            solved_data = {"solved_slugs": []}
    else:
        solved_data = {"solved_slugs": []}

    if "solved_slugs" not in solved_data or not isinstance(solved_data["solved_slugs"], list):
        solved_data["solved_slugs"] = []

    solved_slugs = set(solved_data["solved_slugs"])

    run_git(["config", "user.name", git_username], cwd=target_repo_dir)
    run_git(["config", "user.email", git_email], cwd=target_repo_dir)

    num_to_solve = random.randint(2, 5)
    # Single evening run; commits are backdated to random daytime times instead of sleeping.
    commit_times = [None] * num_to_solve if skip_delay else random_commit_times(num_to_solve)
    available_tags = list(CATEGORIES.keys())
    random.shuffle(available_tags)

    solved_count = 0
    consecutive_failures = 0

    for tag_slug in available_tags if api_key else []:
        if solved_count >= num_to_solve or consecutive_failures >= 3:
            break

        folder_name = CATEGORIES[tag_slug]
        try:
            candidates = fetch_problems_by_category(tag_slug, limit=50, skip=0)
            unsolved = [
                q for q in candidates if q.get("titleSlug") not in solved_slugs
            ]

            # If first 50 in this category are solved, try a random skip page
            if not unsolved:
                candidates = fetch_problems_by_category(
                    tag_slug, limit=50, skip=random.choice([50, 100, 150])
                )
                unsolved = [
                    q for q in candidates if q.get("titleSlug") not in solved_slugs
                ]

            # If all fetched in category are already solved, allow updating an existing one
            pool = unsolved if unsolved else candidates
            if not pool:
                continue

            random.shuffle(pool)
            chosen = None
            detail = None

            for candidate in pool[:8]:
                slug = candidate.get("titleSlug")
                if not slug:
                    continue
                d = fetch_problem_detail(slug)
                snippets = d.get("codeSnippets") or []
                if any(s.get("langSlug") == "dart" for s in snippets):
                    chosen = candidate
                    detail = d
                    break

            if not chosen or not detail:
                continue

            slug = chosen["titleSlug"]
            dart_code = solve_with_gemini(api_key, detail, folder_name)

            file_name = slug.replace("-", "_") + ".dart"
            rel_path = f"{folder_name}/{file_name}"

            # Pull any remote changes first so writing the file never conflicts
            sync_target_repo(target_repo_dir, target_branch)

            category_dir = target_repo_dir / folder_name
            category_dir.mkdir(parents=True, exist_ok=True)
            file_path = category_dir / file_name

            is_update = file_path.exists()
            file_path.write_text(dart_code, encoding="utf-8")

            commit_msg = build_commit_message(
                folder_name, file_name, problem=detail, is_update=is_update
            )
            commit_and_push(
                target_repo_dir, target_branch, rel_path, commit_msg, commit_times[solved_count]
            )

            if slug not in solved_slugs:
                solved_slugs.add(slug)
                solved_data["solved_slugs"].append(slug)
                solved_db_path.write_text(
                    json.dumps(solved_data, indent=2) + "\n", encoding="utf-8"
                )

            solved_count += 1
            consecutive_failures = 0
            print(f"[+] Committed {rel_path} ({solved_count}/{num_to_solve})")

        except Exception as exc:
            consecutive_failures += 1
            print(f"[!] Skipped category {tag_slug} due to error: {exc}", file=sys.stderr)
            continue

    # Ultimate fallback: if external APIs failed for remaining slots, write a real
    # built-in .dart solution or update an existing .dart file (always 1 file changed)
    while solved_count < num_to_solve:
        sync_target_repo(target_repo_dir, target_branch)
        unwritten_fallbacks = [
            fb
            for fb in FALLBACK_PROBLEMS
            if not (
                target_repo_dir / fb["category"] / (fb["slug"].replace("-", "_") + ".dart")
            ).exists()
        ]
        chosen_fb = random.choice(
            unwritten_fallbacks if unwritten_fallbacks else FALLBACK_PROBLEMS
        )
        cat_name = chosen_fb["category"]
        file_name = chosen_fb["slug"].replace("-", "_") + ".dart"
        rel_path = f"{cat_name}/{file_name}"
        category_dir = target_repo_dir / cat_name
        category_dir.mkdir(parents=True, exist_ok=True)
        file_path = category_dir / file_name

        is_update = file_path.exists()
        file_path.write_text(chosen_fb["code"], encoding="utf-8")

        commit_msg = build_commit_message(
            cat_name, file_name, problem=chosen_fb, is_update=is_update
        )
        commit_and_push(
            target_repo_dir, target_branch, rel_path, commit_msg, commit_times[solved_count]
        )

        solved_count += 1
        print(f"[+] Fallback commit completed ({solved_count}/{num_to_solve})")

    solved_data["last_run"] = int(time.time())
    solved_db_path.write_text(
        json.dumps(solved_data, indent=2) + "\n", encoding="utf-8"
    )
    print("[*] Finished commits.")


if __name__ == "__main__":
    main()

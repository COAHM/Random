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
from pathlib import Path

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
DEFAULT_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]

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


def solve_with_gemini(api_key: str, problem: dict, category_name: str) -> str:
    preferred_model = os.environ.get("GEMINI_MODEL", "").strip()
    models = ([preferred_model] if preferred_model else []) + [
        m for m in DEFAULT_MODELS if m != preferred_model
    ]

    dart_snippet = ""
    for snippet in problem.get("codeSnippets") or []:
        if snippet.get("langSlug") == "dart":
            dart_snippet = snippet.get("code", "")
            break

    description = strip_html(problem.get("content", ""))
    title = problem.get("title", "")
    difficulty = problem.get("difficulty", "Medium")
    frontend_id = problem.get("questionFrontendId", "")

    prompt = (
        f"You are an experienced software engineer solving a LeetCode problem in Dart 3 (null-safe).\n\n"
        f"Problem #{frontend_id}: {title} ({difficulty})\n"
        f"Category: {category_name}\n\n"
        f"Description:\n{description}\n\n"
        f"Starter Code:\n{dart_snippet}\n\n"
        f"Requirements:\n"
        f"1. Output ONLY valid Dart code. Do NOT wrap the output in markdown fences (```dart).\n"
        f"2. At the top of the file, include the full problem title, difficulty, and problem description (including examples and constraints) inside a clean `/* ... */` block comment.\n"
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

    last_err = None
    # Support both Google AI Studio keys (AIza...) and Vertex AI Express keys (AQ....)
    endpoints = (
        [
            "https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent?key={key}",
            "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        ]
        if api_key.startswith("AQ.")
        else [
            "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
            "https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent?key={key}",
        ]
    )

    for endpoint_tpl in endpoints:
        for model in models:
            url = endpoint_tpl.format(model=model, key=api_key)
            for attempt in range(2):
                try:
                    req = urllib.request.Request(
                        url,
                        data=payload,
                        headers={"Content-Type": "application/json"},
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
                        return raw_text.strip() + "\n"
                except urllib.error.HTTPError as http_err:
                    err_body = ""
                    try:
                        err_body = http_err.read().decode("utf-8", errors="ignore")[:200]
                    except Exception:
                        pass
                    last_err = f"HTTP {http_err.code} on {model}: {err_body or http_err.reason}"
                    if http_err.code in (400, 401, 403, 404):
                        break
                    time.sleep(2 ** attempt)
                except Exception as exc:
                    last_err = exc
                    time.sleep(2 ** attempt)

    raise RuntimeError(f"Gemini generation failed across all models: {last_err}")


def run_git(
    args: list[str], cwd: Path, check: bool = True
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=check,
        capture_output=True,
        text=True,
    )


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


def commit_and_push(
    cwd: Path, branch: str, rel_path: str | None, message: str
) -> None:
    sync_target_repo(cwd, branch)

    if rel_path:
        run_git(["add", rel_path], cwd=cwd)

    diff_check = run_git(["diff", "--cached", "--quiet"], cwd=cwd, check=False)
    if diff_check.returncode == 0:
        # Either an existing file had identical content or no file was staged:
        # create an empty/blank commit so updating existing files or unchanged state still commits cleanly
        print(f"[i] No file diff detected; creating commit with --allow-empty: {message}")
        run_git(["commit", "--allow-empty", "-m", message], cwd=cwd)
    else:
        run_git(["commit", "-m", message], cwd=cwd)

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

    if not skip_delay:
        initial_sleep = random.randint(60, 2700)
        print(
            f"[i] Waiting {initial_sleep // 60} min ({initial_sleep}s) before starting daily solve..."
        )
        time.sleep(initial_sleep)

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

    num_to_solve = random.randint(2, 3)
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
            commit_and_push(target_repo_dir, target_branch, rel_path, commit_msg)

            if slug not in solved_slugs:
                solved_slugs.add(slug)
                solved_data["solved_slugs"].append(slug)
                solved_db_path.write_text(
                    json.dumps(solved_data, indent=2) + "\n", encoding="utf-8"
                )

            solved_count += 1
            consecutive_failures = 0
            print(f"[+] Committed {rel_path} ({solved_count}/{num_to_solve})")

            if solved_count < num_to_solve and not skip_delay:
                sleep_time = random.randint(1800, 3300)
                print(f"[i] Sleeping {sleep_time // 60} min before next commit")
                time.sleep(sleep_time)

        except Exception as exc:
            consecutive_failures += 1
            print(f"[!] Skipped category {tag_slug} due to error: {exc}", file=sys.stderr)
            continue

    # Ultimate fallback: if external APIs failed completely for remaining slots,
    # update an existing .dart file or make a blank commit so the daily schedule still succeeds
    while solved_count < num_to_solve:
        existing_dart_files = list(target_repo_dir.rglob("*.dart"))
        if existing_dart_files:
            chosen_file = random.choice(existing_dart_files)
            rel_path = chosen_file.relative_to(target_repo_dir).as_posix()
            cat_name = chosen_file.parent.name if chosen_file.parent != target_repo_dir else "arrays"
            commit_msg = build_commit_message(cat_name, chosen_file.name, is_update=True)
            commit_and_push(target_repo_dir, target_branch, rel_path, commit_msg)
        else:
            commit_msg = build_commit_message("arrays", "two_sum.dart", is_update=False)
            commit_and_push(target_repo_dir, target_branch, None, commit_msg)

        solved_count += 1
        print(f"[+] Fallback commit completed ({solved_count}/{num_to_solve})")
        if solved_count < num_to_solve and not skip_delay:
            sleep_time = random.randint(1800, 3300)
            print(f"[i] Sleeping {sleep_time // 60} min before next commit")
            time.sleep(sleep_time)

    print("[*] Finished commits.")


if __name__ == "__main__":
    main()

#!/bin/bash

# === CONFIGURATION ===
REPO_PATH="/d/Projects/Random"       # Path to your local Git repository
BRANCH="main"                        # Branch to push commits to
USERNAME="sakarpaudel"               # Git username
EMAIL="sakarpaudel06@gmail.com"      # Git email (optional)

cd "$REPO_PATH" || exit

git config user.name "$USERNAME"
git config user.email "$EMAIL"

# Dart problem-solving snippets
declare -a SNIPPETS=(
'List<int> fibonacci(int n) {\n  List<int> seq = [0, 1];\n  for (int i = 2; i < n; i++) {\n    seq.add(seq[i - 1] + seq[i - 2]);\n  }\n  return seq;\n}'
'String reverse(String input) {\n  return input.split("").reversed.join();\n}'
'bool isPrime(int n) {\n  if (n <= 1) return false;\n  for (int i = 2; i <= n ~/ 2; i++) {\n    if (n % i == 0) return false;\n  }\n  return true;\n}'
'import "package:flutter/material.dart";\n\nclass SimpleCounter extends StatefulWidget {\n  @override\n  _SimpleCounterState createState() => _SimpleCounterState();\n}\n\nclass _SimpleCounterState extends State<SimpleCounter> {\n  int count = 0;\n\n  @override\n  Widget build(BuildContext context) {\n    return Scaffold(\n      appBar: AppBar(title: Text("Counter")),\n      body: Center(child: Text("Count: \$count")),\n      floatingActionButton: FloatingActionButton(\n        onPressed: () => setState(() => count++),\n        child: Icon(Icons.add),\n      ),\n    );\n  }\n}'
'void bubbleSort(List<int> arr) {\n  for (int i = 0; i < arr.length - 1; i++) {\n    for (int j = 0; j < arr.length - i - 1; j++) {\n      if (arr[j] > arr[j + 1]) {\n        int temp = arr[j];\n        arr[j] = arr[j + 1];\n        arr[j + 1] = temp;\n      }\n    }\n  }\n}'
)

make_commit() {
    FILE="solution_$((RANDOM % 50 + 1)).dart"
    INDEX=$((RANDOM % ${#SNIPPETS[@]}))
    echo -e "${SNIPPETS[$INDEX]}" > "$FILE"

    git add "$FILE"
    git commit -m "solved dart problem: $FILE"
    git push origin "$BRANCH"
    echo "[+] Committed $FILE"
}

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

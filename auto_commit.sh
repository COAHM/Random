#!/bin/bash

# === CONFIGURATION ===
REPO_PATH="/d/Projects/Random"       # Path to your local Git repository
BRANCH="main"                        # Branch to push commits to
USERNAME="sakarpaudel"               # Git username
EMAIL="sakarpaudel06@gmail.com"      # Git email (optional)

# Change directory to the repo or exit if path is invalid
cd "$REPO_PATH" || exit

# Set Git user configuration
git config user.name "$USERNAME"
git config user.email "$EMAIL"

# Function to create a random file and commit it
make_commit() {
    FILE="file_$((RANDOM % 50 + 1)).txt"                          # Random file name
    echo "Auto update at $(date) #$RANDOM" > "$FILE"              # Write timestamp and random number
    git add "$FILE"                                               # Stage the file
    git commit -m "auto update $FILE"                             # Commit with message
    git push origin "$BRANCH"                                     # Push to the remote branch
    echo "[+] Committed $FILE"                                    # Log the commit
}

# Choose a random number between 3 and 5 for number of commits
NUM_COMMITS=$((RANDOM % 3 + 3))  # (0,1,2) + 3 = 3–5

# Loop to make the commits
for ((i=1; i<=NUM_COMMITS; i++))
do
    make_commit
    if [ $i -lt $NUM_COMMITS ]; then
        SLEEP_TIME=$((RANDOM % 5400 + 1800))                      # Sleep 30–120 mins
        echo "[i] Sleeping $((SLEEP_TIME/60)) min before next commit"
        sleep "$SLEEP_TIME"                                       # Wait before next commit
    fi
done

echo "[*] Finished today's commits."                              # Final message
exit 0                                                            # Exit script


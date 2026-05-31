#!/bin/bash
set -euo pipefail

# Auto debug build script for GitHub Actions
# Tries multiple build strategies to produce an APK and collects logs.

ARTIFACT_DIR="artifacts"
mkdir -p "$ARTIFACT_DIR"
TIMESTAMP=$(date -u +%Y%m%d%H%M%S)
REPO_DIR="${GITHUB_WORKSPACE:-$PWD}"
RUN_URL="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID:-unknown}"

STATUS=1
APK_FOUND=0

log() { echo "[$(date -u +%T)] $*"; }

try_docker_image() {
  local image="$1"
  local name="$2"
  local logfile="$ARTIFACT_DIR/${name}-${TIMESTAMP}.log"

  log "=== Attempt: $name (image: $image) ===" | tee -a "$logfile"
  docker pull "$image" 2>&1 | tee -a "$logfile" || true

  docker run --rm \
    -v "${REPO_DIR}:/home/user/hostcwd" \
    -w /home/user/hostcwd \
    "$image" \
    /bin/bash -lc "set -euo pipefail && pip install --upgrade pip || true && if [ -f requirements.txt ]; then pip install -r requirements.txt || true; fi && buildozer -v android debug" \
    2>&1 | tee -a "$logfile" || true

  if compgen -G "bin/*.apk" > /dev/null; then
    mkdir -p "$ARTIFACT_DIR/apks"
    cp bin/*.apk "$ARTIFACT_DIR/apks/" 2>/dev/null || true
    log "APK produced by $name" | tee -a "$logfile"
    APK_FOUND=1
    STATUS=0
  else
    log "No APK produced by $name" | tee -a "$logfile"
  fi
}

try_native_build() {
  local logfile="$ARTIFACT_DIR/native-${TIMESTAMP}.log"
  log "=== Attempt: native runner build ===" | tee -a "$logfile"

  sudo apt-get update 2>&1 | tee -a "$logfile" || true
  sudo apt-get install -y openjdk-11-jdk python3-pip build-essential git wget unzip 2>&1 | tee -a "$logfile" || true

  pip install --upgrade pip 2>&1 | tee -a "$logfile" || true
  pip install buildozer cython 2>&1 | tee -a "$logfile" || true

  # Try build
  (cd "$REPO_DIR" && buildozer -v android debug) 2>&1 | tee -a "$logfile" || true

  if compgen -G "${REPO_DIR}/bin/*.apk" > /dev/null; then
    mkdir -p "$ARTIFACT_DIR/apks"
    cp "${REPO_DIR}/bin"/*.apk "$ARTIFACT_DIR/apks/" 2>/dev/null || true
    log "APK produced by native build" | tee -a "$logfile"
    APK_FOUND=1
    STATUS=0
  else
    log "No APK produced by native build" | tee -a "$logfile"
  fi
}

# Strategy sequence
try_docker_image "kivy/buildozer:latest" "docker-latest"
if [ "$STATUS" -ne 0 ]; then
  try_docker_image "kivy/buildozer:python3.10" "docker-py310"
fi
if [ "$STATUS" -ne 0 ]; then
  try_native_build
fi

if [ "$APK_FOUND" -eq 1 ]; then
  log "SUCCESS: APK produced. Artifacts available in $ARTIFACT_DIR"
  exit 0
fi

log "ALL STRATEGIES FAILED. Preparing suggested PR with logs and summary."

# Create a branch with a conservative suggested change file and push it
BRANCH="auto-debug-fix-${TIMESTAMP}"
PROPOSED_FILE="PROPOSED_WORKFLOW_FIX.md"

# Configure git
git config --global user.email "actions@github.com" || true
git config --global user.name "github-actions[bot]" || true

git checkout -b "$BRANCH" || git switch -c "$BRANCH" || true

cat > "$PROPOSED_FILE" <<EOF
# Proposed Workflow Fix (auto-debug)

This automated PR was created because all automated build strategies failed for the workflow run:

Run URL: $RUN_URL

Attempts made:
- Docker image: kivy/buildozer:latest
- Docker image: kivy/buildozer:python3.10
- Native runner (apt + pip + buildozer)

Logs have been uploaded as workflow artifacts. Please inspect them:
- $RUN_URL (Artifacts section)

Suggested conservative changes:
1. Use the Buildozer Docker image in CI for a stable Android toolchain.
2. Build a debug APK in CI to avoid keystore/signing issues: `buildozer -v android debug`.
3. Ensure `requirements.txt` contains all Python dependencies used by the app.

Example snippet to use in .github/workflows/build-apk.yml:

```yaml
- name: Build with Buildozer Docker image
  run: |
    docker pull kivy/buildozer:latest
    docker run --rm -v "${GITHUB_WORKSPACE}:/home/user/hostcwd" -w /home/user/hostcwd kivy/buildozer:latest /bin/bash -lc "pip install --upgrade pip || true && if [ -f requirements.txt ]; then pip install -r requirements.txt || true; fi && buildozer -v android debug"
```

EOF

# Add logs summary (first lines of each log) to the PR body
PR_SUMMARY="Auto-debug failed. See $RUN_URL for full logs."

git add "$PROPOSED_FILE"
if git commit -m "ci: proposed workflow fix from auto-debug run"; then
  git push "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" "$BRANCH" >/dev/null 2>&1 || true

  # Create PR
  PR_DATA=$(jq -n --arg title "ci: proposed workflow fix from auto-debug" --arg head "$BRANCH" --arg base "main" --arg body "$PR_SUMMARY" '{title:$title, head:$head, base:$base, body:$body}')
  curl -s -X POST -H "Authorization: Bearer ${GITHUB_TOKEN}" -H "Accept: application/vnd.github+json" "https://api.github.com/repos/${GITHUB_REPOSITORY}/pulls" -d "$PR_DATA" || true
else
  log "No changes to commit for PR."
fi

# Exit non-zero to indicate the workflow did not produce an APK
exit 1

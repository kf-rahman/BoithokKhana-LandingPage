#!/usr/bin/env bash
#
# Keep the Render free-plan services awake.
#
# A free Render web service spins down after 15 minutes without inbound
# traffic, and the next visitor then waits ~1 minute staring at Render's
# loading page. This script sends one cheap request to each target so the
# service never goes idle long enough to sleep.
#
# Run it from CI (see .github/workflows/keep-warm.yml), from a cron entry, or
# by hand. Every target must answer 2xx/3xx or the script exits non-zero, so
# it doubles as an uptime check: a failure here means the site is genuinely
# down, not just cold.
#
# Usage:
#   scripts/keep-warm.sh                      # default targets below
#   scripts/keep-warm.sh https://example.com  # explicit targets
#
# Environment:
#   KEEP_WARM_URLS   space-separated targets (overrides the defaults)
#   ATTEMPTS         tries per target before giving up (default 3)
#   TIMEOUT          seconds to wait for one try (default 120 — a cold
#                    start really can take ~60s, so don't go below ~90)

set -uo pipefail

# Only the web service by default — that's the page customers actually land
# on, and it's the one that was showing Render's spin-up screen.
#
# Once the FastAPI backend is healthy again, add the API to the list so the
# order form doesn't cold-start either:
#
#   KEEP_WARM_URLS="https://www.boithokkhana.ca/ https://www.boithokkhana.ca/api/health" \
#     scripts/keep-warm.sh
#
# (/api/health goes through the web service's proxy, so one URL warms both
# hops. As of the last check it never answers — see the quota note in
# .github/workflows/keep-warm.yml before making it a permanent target.)
DEFAULT_URLS=(
  "https://www.boithokkhana.ca/"
)

ATTEMPTS="${ATTEMPTS:-3}"
TIMEOUT="${TIMEOUT:-120}"

if [ "$#" -gt 0 ]; then
  urls=("$@")
elif [ -n "${KEEP_WARM_URLS:-}" ]; then
  # shellcheck disable=SC2206 # deliberate word-splitting: space-separated list
  urls=(${KEEP_WARM_URLS})
else
  urls=("${DEFAULT_URLS[@]}")
fi

failed=0

for url in "${urls[@]}"; do
  ok=0
  for attempt in $(seq 1 "$ATTEMPTS"); do
    # -L so a redirect (apex -> www) still counts as reaching the service.
    read -r code seconds < <(
      curl -sS -L -o /dev/null \
        --max-time "$TIMEOUT" \
        -w '%{http_code} %{time_total}\n' \
        -H 'User-Agent: boithok-keep-warm/1' \
        "$url" 2>/dev/null
    ) || { code=000; seconds=0; }

    if [ "$code" -ge 200 ] && [ "$code" -lt 400 ]; then
      printf 'ok    %s -> %s in %ss (attempt %s)\n' "$url" "$code" "$seconds" "$attempt"
      ok=1
      break
    fi

    printf 'retry %s -> %s in %ss (attempt %s/%s)\n' \
      "$url" "$code" "$seconds" "$attempt" "$ATTEMPTS"
    [ "$attempt" -lt "$ATTEMPTS" ] && sleep 10
  done

  if [ "$ok" -eq 0 ]; then
    printf 'FAIL  %s unreachable after %s attempts\n' "$url" "$ATTEMPTS"
    failed=1
  fi
done

exit "$failed"

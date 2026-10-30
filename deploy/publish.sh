#!/bin/sh
# Downloads the MIMIT CSVs from the home network, builds stations.json and pushes it to the `data` branch.
# GitHub Actions on main then deploys that branch to Pages (MIMIT times out from GitHub runners since mid-October 2026).
#
# Exit codes, read by systemd and by Homelab Notify's job monitor:
#   0   published a newer reference date
#   75  nothing new to publish (MIMIT not updated yet, or already published today): a success, not an error
#   any other  failure (download, broken data, push)
set -eu

NOTHING_NEW=75

MIMIT_URL=https://www.mimit.gov.it/images/exportCSV/
PAGES_URL=${PAGES_URL:-https://leixien.github.io/FuelFinder_DATA/stations.json}
REPO=${REPO:-git@github.com:Leixien/FuelFinder_DATA.git}
USER_AGENT="fuel-data (+https://github.com/Leixien)"
ARCHIVE=/archive
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

for name in anagrafica_impianti_attivi.csv prezzo_alle_8.csv; do
    curl --fail --silent --show-error --retry 3 --retry-delay 30 --max-time 120 \
        --user-agent "$USER_AGENT" --output "$WORK/$name" "$MIMIT_URL$name"
done

# Fails on broken or too-small data, so nothing below runs and Pages keeps the last good file.
python /app/build_stations.py "$WORK/stations.json" "$WORK/anagrafica_impianti_attivi.csv" "$WORK/prezzo_alle_8.csv"

reference_date() {
    python -c 'import json, sys; print(json.load(sys.stdin)["prices_reference_date"])'
}
new=$(reference_date < "$WORK/stations.json")
published=$(curl --fail --silent --max-time 120 "$PAGES_URL" | reference_date 2>/dev/null || echo "")

# Raw CSVs stay on the homelab (about 13 MB a day): the base for a future price history.
mkdir -p "$ARCHIVE/$new"
cp "$WORK"/*.csv "$ARCHIVE/$new/"

# MIMIT can publish late: re-running on yesterday's file must not republish it as new.
# ISO dates compare correctly as strings.
if [ -n "$published" ] && [ ! "$new" \> "$published" ]; then
    echo "reference date $new is not newer than published $published: nothing to publish"
    exit "$NOTHING_NEW"
fi

if [ "${DRY_RUN:-0}" = 1 ]; then
    echo "dry run: would publish reference date $new (published: ${published:-none})"
    exit 0
fi

# One orphan commit, force-pushed: the branch carries only today's file, not years of 13 MB snapshots.
export GIT_SSH_COMMAND="ssh -i /run/secrets/deploy_key -o IdentitiesOnly=yes \
-o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/state/known_hosts"
cd "$WORK"
git init --quiet --initial-branch=data
git add stations.json
git -c user.name="fuel-data homelab" -c user.email="fuel-data@users.noreply.github.com" \
    commit --quiet --message "data: MIMIT prices of $new"
git push --quiet --force "$REPO" data
echo "published reference date $new"

#!/bin/zsh
# loop-59 copied-out dry run. Usage: zsh results/copied_out_dry_run.sh <hub> <tmpdir> > results/copied_out_dry_run.txt
HUB=$1; T=$2
mkdir -p "$T/team"
rsync -a --exclude .venv --exclude runs --exclude __pycache__ "$HUB/templates/flight-repo/" "$T/team/"
cd "$T/team" || exit 1
clean() { sed "s#$HUB#\$HUB#g; s#$T#\$T#g" | grep -v -E '^ \+ |^Resolved|^Prepared|^Installed|^Using|^Creating|^Activate|^warning'; }
echo "# loop-59 copied-out dry run, $(date '+%Y-%m-%d %H:%M'), synthetic. Template copied to \$T/team (T = a fresh temp dir), HUB = this checkout"
echo "\$ ls \$T  # before"; ls "$T"
echo '$ make first-flight'
{ /usr/bin/time -p make first-flight; echo "rc=$?"; } 2>&1 | clean
echo '$ make first-flight-reloc'
{ make first-flight-reloc; echo "rc=$?"; } 2>&1 | clean
echo "\$ ls \$T  # after the failed targets: no stray samples/ dir"; ls "$T"
echo "\$ ls -a \$T/team | grep -c venv"; ls -a | grep -c venv
echo '$ make first-flight ARENA=$HUB/samples/close-area-arena SAFETY=$HUB/samples/close-area-safety-filter'
{ /usr/bin/time -p make first-flight ARENA=$HUB/samples/close-area-arena SAFETY=$HUB/samples/close-area-safety-filter; echo "rc=$?"; } 2>&1 | clean
echo "\$ ls \$T; ls -a \$T/team | grep venv"; ls "$T"; ls -a | grep venv
echo '$ make first-flight-reloc HUB=$HUB'
{ /usr/bin/time -p make first-flight-reloc HUB=$HUB; echo "rc=$?"; } 2>&1 | clean
echo '$ make test HUB=$HUB'
{ make test HUB=$HUB; echo "rc=$?"; } 2>&1 | tail -6 | clean

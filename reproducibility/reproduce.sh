#!/usr/bin/env bash
set -euo pipefail
bundle=$(cd "$(dirname "$0")" && pwd)
checkout=$(mktemp -d)
trap 'rm -r "$checkout"' EXIT
read -r repo commit < "$bundle/sources.lock"
git -C "$checkout" init -q
git -C "$checkout" fetch -q --depth 1 "https://github.com/nicholaskouns-create/$repo.git" "$commit"
git -C "$checkout" checkout -q --detach FETCH_HEAD
python3 -m venv "$checkout/venv"
python="$checkout/venv/bin/python"
"$python" -m pip install -r "$bundle/requirements.txt"
cd "$checkout/research/e47/validation"
"$python" e47_grassmann_casimir_witness_20261008.py
E47_CERT_OUT="$checkout/census.json" "$python" e47_casimir_census_certificate.py
"$python" e47_fib_lucas_tower_validate.py

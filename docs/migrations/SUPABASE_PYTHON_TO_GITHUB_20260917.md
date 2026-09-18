# Supabase → GitHub Python / Citizen Migration

This branch creates an additive GitHub mirror of the Mathematical City Python corpus and the machine-validated citizen registry.

## What “migrate” means here

Supabase Edge Functions are Deno/TypeScript services. They are not being misclassified as Python or removed. The Python corpus tracked in `public.python_corpus_registry` and Python-bearing `source_artifacts` is being mirrored into GitHub. Exact source bytes are copied only when recoverable from a linked source artifact; unresolved/held/planned entries remain registry records until their source is recovered.

The public website receives a machine-validated citizen index under `website/citizens/`. Every entry retains its original evidence class and boundary. No candidate is promoted to canonical status.

## Recovered source tranche

Eight active Python source files with explicit source hashes were recovered from Google Drive-linked source artifacts. Their hashes and paths are recorded in `python_migration_manifest.json`.

## Next closure

Continue exact-source recovery for the remaining Python corpus records, verify source hashes, run the declared validation requirements, and only then move source from migration staging to canonical repository paths.

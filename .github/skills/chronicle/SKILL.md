---
name: chronicle
description: >-
  Review Copilot session history and recommend personalized tips, standups,
  searches, cost insights, or instruction improvements. Use for /chronicle tips,
  /chronicle standup, /chronicle search, /chronicle cost-tips, /chronicle improve,
  session history analysis, usage patterns, or agent interaction retrospectives.
argument-hint: 'tips | standup | search <query> | cost-tips | improve'
user-invocable: true
---

# Chronicle — session history tools and insights

Provide Chronicle-style analysis for this repository when the built-in
`/chronicle` command is unavailable, disabled, or the user asks for session
history tips.

## When to use

- User runs `/chronicle tips`, `/chronicle standup`, `/chronicle search`,
  `/chronicle cost-tips`, or `/chronicle improve`
- User asks for personalized Copilot usage tips, session retrospectives, or
  standup summaries from past agent work
- Keywords: chronicle, session history, usage patterns, cost tips, standup

## Subcommands

Interpret the user argument (default: `tips`):

| Argument | Goal |
|---|---|
| `tips` | Personalized recommendations from usage patterns |
| `standup` | Concise recent-activity standup |
| `search <query>` | Search session content for a query |
| `cost-tips` | Token/cost efficiency recommendations |
| `improve` | Propose updates to `.github/copilot-instructions.md` |

## Data sources

Query the session store with the available session-history SQL tool.

**Prefer cloud store (DuckDB)** when available:

- `sessions` — id, task_id, cwd, repository, branch, summary, agent_name, created_at, updated_at
- `turns` — session_id, turn_index, user_message, assistant_response, timestamp
- `session_files` — session_id, file_path, tool_name, turn_index
- `session_refs` — session_id, ref_type, ref_value, turn_index
- `checkpoints` — session_id, checkpoint_number, title, overview, created_at
- `events` — session_id, timestamp, type, user_content, assistant_content, tool_start_name, usage_*
- `tool_requests` — session_id, tool_call_id, name, arguments_json

**Local store (SQLite)** may also expose `assistant_usage_events` and FTS5 `search_index`.

### Query rules

1. Always time-bound large tables (`turns`, `events`) — start with 7–30 days.
2. Prefer absolute ISO timestamps when possible; relative intervals can time out on cloud.
3. Select only needed columns; always `LIMIT`.
4. Combine PR/issue lookups via `session_refs` rather than ILIKE-scanning all turns.
5. If user messages are empty, infer patterns from assistant content, branch names,
   `session_files`, PR titles, and tool usage frequencies.

## Workflow by subcommand

### tips

1. Aggregate last 30–90 days: agent mix, duration distribution, burst days, peak hours.
2. Rank hot files (`session_files`) and recurring PR themes.
3. Detect anti-patterns: many sub-30s sessions, repeated same-branch relaunches,
   permission/settings tasks sent to coding agent, ambiguous “fix CI” prompts.
4. Emit 8–12 **personalized** tips with evidence and a short “highest leverage next moves” list.
5. Focus on both product capabilities and better prompting/interaction habits.

### standup

1. Summarize the last 1–3 active days of sessions.
2. Group by theme (CI, kernel/math, packaging, access/settings).
3. List open follow-ups and blocked items.
4. Keep it scannable (bullets, no essay).

### search \<query\>

1. Search `turns`, `events.user_content`/`assistant_content`, and local `search_index` if present.
2. Return ranked hits with session_id, timestamp, and short snippets.
3. If empty, suggest broader terms or `improve`/`tips` instead.

### cost-tips

1. Use usage columns when present (`usage_input_tokens`, `usage_output_tokens`,
   local `assistant_usage_events`).
2. If usage is missing, infer cost drivers: long sessions, repeated discovery,
   large file reads, CI log thrash, multi-session rework.
3. Recommend concrete reductions (paste failing logs up front, follow up on same PR,
   narrower prompts, setup-steps caching).

### improve

1. Read `.github/copilot-instructions.md` if it exists.
2. Analyze repeated agent struggles/corrections from history.
3. Propose a minimal patch to instructions (build/test commands, frozen invariants,
   workflow map, do/don’t). Do not invent generic advice.
4. Apply the patch when the user wants implementation; otherwise show the diff plan.

## Output format

- Lead with the subcommand result, not tool narration.
- Cite evidence lightly (counts, dates, file/PR names).
- No secrets, tokens, or private third-party data.
- If session history is empty/unavailable, say so and give repo-specific baseline tips
  from README/docs/CI instead of fabricating history.

## References

- Session schema notes: [references/session-store.md](references/session-store.md)
- Repo maintenance constraints: `docs/maintenance_policy.md`

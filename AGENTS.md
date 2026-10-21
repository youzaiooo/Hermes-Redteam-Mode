# hermes-redteam — project instructions for Codex

## Mission

Turn the first-attempt `hermes-redteam` plugin into a working red-team command console on
Hermes, and make it stronger than the DSH reference plugin
(`https://github.com/Jueze-2019/dsh-redteam-mode`, checkout at `/home/kali/src/dsh-redteam-mode`).

Authorized engagements only. No exploit code, payloads, or plaintext credential values in the
repository; record pointers/evidence paths only.

## Product model (decided by the user — do not change)

The user does **not** want Sekhmet to spawn four temporary subagents. The architecture is:

- **Commander = Hermes `default` profile (Sekhmet).** Talks to the user, opens the engagement,
  plans, dispatches tickets, checks the fact store, reports. It gets **no execution tools**.
- **Five permanent worker profiles** already exist: `rt-recon`, `rt-asset`, `rt-vuln`,
  `rt-exploit`, `rt-internal`. Each has its own model, skills, memory and role tools. They are
  long-lived identities, not disposable subagents.
- **Dispatch = Hermes kanban.** The commander (or the plugin's dispatch tool) creates a card
  assigned to `rt-<role>`; the gateway dispatcher spawns that profile's worker process; the
  worker runs with its own tools/skills and completes the card. Verified working on this
  machine: a smoke card completed in 11 s after the profile model was fixed.
- **Fact store = per-engagement SQLite + wiki + raw**, under
  `$HERMES_HOME/redteam/engagements/<id>/`.

Rationale: keep Sekhmet lean, give each specialist a higher skill/tool ceiling, and allow
tools/skills to be rolled out to specialists independently.

## Runtime facts (this machine)

| Item | Value |
|---|---|
| Hermes source | `/home/kali/.hermes/hermes-agent` (v0.22.2) |
| Hermes CLI | `/home/kali/.local/bin/hermes` |
| Plugin install | `~/.hermes/plugins/hermes-redteam` → this repo (symlink) |
| Desktop half copy | `~/.hermes/desktop-plugins/hermes-redteam/plugin.js` |
| Tests | `env -u PYTHONPATH /usr/bin/python3 -m pytest tests -q` |
| DSH upstream | `/home/kali/src/dsh-redteam-mode` (v0.14.0) + `docs/详细文档.md` |
| Live DSH console | `http://192.168.10.142:3080` |
| Local lab | `127.0.0.1:8765` (static site) |
| Kanban | `hermes kanban create/show/list`, dispatcher in the gateway |

The five `rt-*` profiles were switched to `deepseek` / `deepseek-v4-pro` on 2026-10-21 because
their previous relay (`api.lt4net.org`, grok) returned 503 for every model.

## Known defects in the current repo (fix these; keep what is sound)

1. `register()` returns early for any profile not starting `rt-`, so the commander gets zero
   tools and `hermes plugins doctor` shows 0 tools.
2. No dispatch layer at all. There is no `redteam_dispatch`, no kanban call, no process spawn.
3. Write tools require the **model** to pass `session_id` in `args`. Hermes already injects
   `session_id` into handler `kwargs`; every handler must read it from kwargs. Current schemas
   ask the model for a value it does not reliably know → `session_unbound`.
4. `$HERMES_HOME` is read via `os.environ.get(...)` with a `~/.hermes` fallback instead of
   `hermes_constants.get_hermes_home()`.
5. Panel is read-only/low-density/partly English, does not follow the session, and ships
   `defaultEnabled: false`.
6. Install is manual (symlinks + per-profile enable).

## Architecture contract

### Registration matrix

`register(ctx)` must resolve the profile with
`hermes_cli.profiles.current_profile_name(default="default")` — `PluginContext` has no
`profile_name` attribute on Hermes 0.22.2 (the old code's `getattr(ctx, "profile_name", "")`
silently returned `""`, which is why doctor saw 0 tools).

- `default` (commander) — read/command surface only:
  `redteam_engagement_open`, `redteam_session_bind`, `redteam_session_info`,
  `redteam_preflight`, `redteam_asset_query/get/stats`, `redteam_chain*`,
  `redteam_score_list/report`, `redteam_report_index`, `redteam_sessions`,
  `redteam_agent_slot`, `redteam_dispatch`, `redteam_dispatch_status`.
- `rt-recon` — recon writes: asset add/test/link/graph, evidence, scan add/list, note, domain index.
- `rt-asset` — asset assess/link/timeline/web list/asset get.
- `rt-vuln` — vuln add/update, http evidence, POC add/search/use, knowledge add/list, finding.
- `rt-exploit` — access/credential add/list, webshell, tunnel add/list, chain add, shot, attack file.
- `rt-internal` — tunnel add/update/list, internal assets, evidence.
- Every `rt-*` also gets the shared read tools it needs and its own role skill only.
- `hermes plugins doctor` runs as `default` — it must show the commander's tools (non-zero).

### Tool handler contract

```python
def handler(args: dict, **kwargs) -> str:
    session_id = kwargs.get("session_id") or args.get("session_id")
    ...
    return json.dumps({...})
```

- Read `session_id`, `task_id`, `parent_agent` from `kwargs`, never require the model to supply
  them.
- Always return a JSON string; never raise.
- `redteam_dispatch` args: `role` (one of the five), `task` (string), optional `title`,
  `priority`, `engagement_id`. It:
  1. resolves the engagement bound to the current session (or explicit id);
  2. refuses if `authorization.md` is missing/empty;
  3. runs `hermes kanban create <title> --assignee rt-<role> --workspace dir:<engagement_dir>
     --body <brief> --json` (use `shutil.which("hermes")` or the current interpreter's
     `-m hermes_cli.main`, inherit env, timeout 30 s);
  4. returns `{ok, task_id, assignee, status}`.
  The brief must include: target/scope from the engagement, the exact task, the engagement
  directory, the role, "record every finding with the redteam_* tools", and the target boundary.
- `redteam_dispatch_status` reads `hermes kanban show <id> --json` (or list) and returns status,
  summary, and result. The commander uses it to poll without needing the kanban toolset.

### Fact store

One SQLite DB per engagement at `$HERMES_HOME/redteam/engagements/<id>/index.db`, plus
`wiki/` and `raw/`. Use `hermes_constants.get_hermes_home()`. No target facts in memory or the
shared wiki. `authorization.md` is the first page of every engagement.

### Panel

`desktop/plugin.js` + `dashboard/plugin_api.py` (FastAPI `router = APIRouter()`). Chinese labels.
Five sections: 态势 / 资产 / 成果 / 报告 / 资源. Follow the active session's engagement
(`/engagements/for-session/<session_id>` or equivalent). Use app components and theme vars; no
hardcoded colors; no JSX syntax (use `jsx()`), imports only from `@hermes/plugin-sdk`, `react`,
`react/jsx-runtime`. Poll with React Query at a few seconds.

## Working rules

- Read the real APIs first: `website/docs/developer-guide/plugins/index.md`,
  `desktop-plugin-sdk.md`, `~/.hermes/hermes-agent/plugins/`, and the DSH upstream code.
- Python 3.11+, `from __future__ import annotations`, small modules, no new heavy dependencies.
- Every new tool gets a test through the registry. Dispatch gets a test that mocks the kanban
  subprocess and asserts role → `rt-<role>`, workspace dir, and authorization refusal.
- Run the full test suite before reporting done.
- Verify on the live install: `hermes plugins doctor hermes-redteam` lists commander tools; a
  real `default` session can open an engagement and create a card for `rt-recon`; the card
  completes.

## Milestones

M1 (this task): registration matrix, session-from-kwargs, `redteam_dispatch` +
`redteam_dispatch_status`, authorization guard, tests, live doctor check.
M2: Chinese panel that follows the session, 5 sections, live data.
M3: one-command install + end-to-end lab run + docs/USAGE.md.

# hermes-redteam — project instructions for Codex

## Mission

Maintain the shipped `hermes-redteam` plugin (v0.3.3) as a working red-team command console on
Hermes, stronger than the DSH reference plugin
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
| Plugin install | `~/.hermes/plugins/hermes-redteam` (GitHub install, not a symlink) |
| Desktop half copy | `~/.hermes/desktop-plugins/hermes-redteam/plugin.js` (v0.3.3) |
| Tests | `env -u PYTHONPATH /usr/bin/python3 -m pytest tests -q` (141 passed, 1 skipped) |
| DSH upstream | `/home/kali/src/dsh-redteam-mode` (v0.14.0) + `docs/详细文档.md` |
| Live DSH console | `http://192.168.10.142:3080` (reference only; optional) |
| Local lab | `127.0.0.1:8765` (static site) |
| Kanban | `hermes kanban create/show/list`, dispatcher in the gateway |

All `default` and `rt-*` profiles run `deepseek-flash` with `reasoning_effort: xhigh` (P1).
The `ltcraft-openai` / `api.lt4net.org` provider blocks are dead legacy config; do not use them.

## First-attempt defects (all fixed; do not regress)

1. Commander profile registration, dispatch, session-from-kwargs, `$HERMES_HOME`, panel/session
   follow, and install are all implemented and tested. `hermes plugins doctor hermes-redteam`
   must show 19 tools.
2. Authorization is **implied by naming a target** (original DSH `COMMON_AUTH`): never ask for a
   five-field form, never require `authorization.md` before dispatch. `engagement_open` writes it
   as an audit record.
3. Do not register a skill whose name mirrors a tool (`redteam-preflight` collision). Preflight is
   a tool (`redteam_preflight`).
4. The desktop half must stay at `DESKTOP_VERSION` matching `plugin.yaml`; the panel checks this.

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
  2. treats the target name as authorization (original DSH rule); no authorization gate;
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

Required API routes (extend the existing router, keep old ones working):

- `GET /engagements` → `{ok, engagements: [{id, display_name, created_at}]}`
- `GET /engagements/for-session/{session_id}` → `{ok, engagement: {id, display_name} | null}`
  by scanning each engagement's `session.json` for the session id.
- `GET /summary/{engagement_id}` → `{ok, summary: {assets, services, vulns, credentials,
  tunnels, score, stage, score_hits}}`
- existing `GET /assets/{id}`, `GET /findings/{id}`, `GET /sessions/{id}`, `GET /tunnels/{id}`,
  `GET /report/{id}`, `GET /skills`, `GET /roles` stay.

Panel behaviour:

- Header: `RedTeam 控制台`, engagement display name or `未绑定靶标`, status dot, refresh.
- Tabs: 态势 (score, five-stage progress, worker roles), 资产 (table: 地址/状态/首见),
  成果 (vulns + credentials + tunnels), 报告 (report index + 导出按钮), 资源 (skills
  可用性 + 角色).
- Follow `host.state.activeSessionId`: fetch for-session on change. If unbound, show the empty
  state (`未绑定靶标`) and the `+ 新建红队会话` form; never auto-show the last engagement.
- New-session button uses `host.newChat('default')` + `host.composer.setDraft/submit('new', …)`.
- Empty states in Chinese (`还没有资产`, `还没有成果`), loading skeletons, error text.
- `defaultEnabled: true`; the pane should be useful immediately after install.

## Working rules

- Read the real APIs first: `website/docs/developer-guide/plugins/index.md`,
  `desktop-plugin-sdk.md`, `~/.hermes/hermes-agent/plugins/`, and the DSH upstream code.
- Python 3.11+, `from __future__ import annotations`, small modules, no new heavy dependencies.
- Every new tool gets a test through the registry. Dispatch gets a test that mocks the kanban
  subprocess and asserts role → `rt-<role>`, workspace dir, and that dispatch works **without**
  an authorization form (target implies authorization).
- Run the full test suite before reporting done.
- Verify on the live install: `hermes plugins doctor hermes-redteam` lists commander tools; a
  real `default` session can open an engagement and create a card for `rt-recon`; the card
  completes.

## Milestones

M1–M5 shipped: registration/dispatch, Chinese session-following panel, role skills, DVWA E2E,
global knowledge FTS5 + report export.

0.2.x: remote desktop install, version handshake + one-click local UI update.
0.3.x: implied authorization (original DSH rule), preflight is a tool only, `+ 新建红队会话`
button. Current version **0.3.3**; 141 tests green.

Remaining optional work: full 25–point scoring table, rt-internal lab run, UI polish.

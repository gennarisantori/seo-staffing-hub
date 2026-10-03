# Handover — SEO/GEO Staffing Hub

What a new machine (or a new Claude Code session) needs in order to keep
maintaining this app. The code explains *what* it does; this file explains *why*
it does it that way, which is the part that is expensive to rediscover.

## Getting running

```bash
git clone https://github.com/gennarisantori/seo-staffing-hub.git
cd seo-staffing-hub
python build.py          # -> "OK 209737 chars written"
```

That is the whole setup. Only **Python 3** and **Git** are required: there is no
Node, no package manager, no build toolchain. A clean clone reproduces a
byte-identical `index.html`, so if the build output differs from the committed
file, something is wrong with the change, not with the environment.

Preview locally with `.claude/launch.json` (serves the folder on
`http://localhost:4173`). Browsers cache this app aggressively during
verification — always load `http://localhost:4173/?v=N` with a changing `N`.

## How the build works, and how it breaks

`build.py` reads `_original.html` (the recovered original, **never edited by
hand**) and applies a long sequence of ordered string replacements to produce
`index.html`. `index.html` is generated: edit `build.py`, never the output.

This design is the single biggest source of accidents. Two rules, both learned
the hard way:

1. **Assert every anchor.** If a replacement target is missing, fail loudly.
   A patch script that dies halfway leaves nothing written, so re-run the whole
   script rather than assuming the earlier steps landed.
2. **Watch the output size.** `python build.py` prints the character count.
   A sudden drop means a replacement swallowed code. This happened twice by
   slicing from `"function A"` to `"function B"` when unrelated functions lived
   between them: 8,000 characters of calculation engine disappeared silently.
   Delimit replacements by the end of the function itself, and assert the slice
   does not contain code it should not.

After any change, verify in the browser and check the console before committing.

## Deployment

`git push origin main` → Cloudflare rebuilds and serves automatically
(`wrangler.jsonc`, static assets with SPA fallback). Nothing to run locally.
Tell users to hard-refresh (Ctrl+F5) after a deploy.

## Data model

- **Firebase Realtime Database** `staffing/v1` — the app's own data:
  `{m: members, p: projects, t: targets, wk: current week, hist: weekly archive,
  touched: who filed when}`.
- **Firestore** — auth only: `users/{uid}` (role, displayName, active) and
  `config/access` (the invite allowlist). Rules live in `firestore.rules`.
- **Firebase Auth** — email/password, restricted to `@jakala.com`.

The Firebase web config is inline in `index.html` and public by design; access is
enforced by Auth plus the database rules, not by hiding the key.

## The measures

Admin > Overview opens with seven blocks, each titled, with the question it
answers under the title. They were agreed one by one; the order is deliberate.

| Block | Question | Formula |
|---|---|---|
| Progress | How up to date is the data? | people who filed the week / active team |
| Billability | How many days must go to projects? | average of the members' billability targets, weighted by working days |
| Capacity | How many billable days can we sell? | working days x billability target, over the measuring window |
| Saturation | How much have we sold against capacity? | days sold / capacity |
| Allocation | How much capacity is both declared and sold? | days both declared by people and sold / capacity |
| Effectiveness | How much of the billable time is used? | days planned on client projects / capacity |
| Efficiency | How many sold days do we save? | 100% - days planned / days sold |

Things that are easy to get wrong:

- **Billability is a target, not a result.** It only moves when ranks or team
  members change. Targets are editable in Admin > By level: PL4 50%, PL3 75%,
  PL2 80%, PL1 90%.
- **The driver is what people declare.** A project's sold days are split among
  the people planning on it **in proportion to their planned days** (the "sold
  share"). Mario 15 days and Laura 10 on a 20-day project: the project is 25%
  over, shares are 60/40, so Mario's sold share is 12 and Laura's 8.
- **Allocation is the overlap of declared and sold**, capped per project at the
  sold share: days declared beyond what was sold are left out, and so are sold
  days nobody declares. It is never above Saturation or Effectiveness. In the UI
  "allocation" means only this measure: the weekly percentages people file are
  shown as **assignments** (the code and this file still call them allocations).
- **Effectiveness counts every client project**, quoted or not: it asks whether
  the billable time is in use, not whether it is paid.
- **Efficiency is computed on projects somebody plans on.** Sold work with
  nobody on it is "Unstaffed", not a saving. A saving above 50% is greyed as
  "Check forecasts": far more likely missing data than real efficiency.
- **Allocation, Effectiveness and Efficiency are in days a week** (see Pace
  below); Capacity and Saturation are days in the measuring window.
- Sold days are matched against the project's **whole pool, not the quoted Price
  Level**, because the mix of people delivering rarely matches the mix that was
  quoted. Matching per level produced dozens of false "not quoted" flags.

People and projects each fall in one group, first match wins:

- People: Not quoted (>5 days on unsold projects), Over budget (efficiency
  < -15%), Under-used (effectiveness < 75%), Overloaded (effectiveness > 115%),
  Check forecasts (efficiency > 50%), On track.
- Projects: Not quoted, Unstaffed, Over budget (< -15%), Check forecasts
  (> 50%), Saving (15% to 50%), On track.

The seniority mismatch is not a group: it surfaces per project as the
**seniority mix**, saying whether work is staffed more senior than quoted (costs
more than budgeted) or more junior (cheaper, but check what the client expects).

## Pace, not totals

Projects compare **days per week**, not cumulative days:

```
planned pace = days a week the team is planning
quoted pace  = days a week the quote implies to finish by its end date
```

Cumulative totals were misleading: the quote spans the whole contract, the team
worked on it for months before any tracking existed, and the app cannot know how
much was already delivered. "349 days still unassigned" read as an alarm when it
was really an unknown. Pace makes a claim only about the *current staffing*,
which is defensible. The caveat is stated in the UI.

If actual delivered days ever become available (timesheets, ClickUp), the
remaining need becomes exact and this caveat can go.

## Weekly forecasting

Everyone, admins included, files next week's split in **My week**. Fridays,
Saturdays and Sundays target the following week. Each week is snapshotted into
`hist` and carried forward; history is viewable and correctable.

Allocations are **capped at 100% of each person's own capacity**, to stop the
inflation spiral that appears when people see colleagues above 100%.

Period averages (current week / last 4 / 12 / all) only differ once a second
week has been filed; the picker says so explicitly rather than looking broken.

## Permissions

- **Members** edit projects they created or are involved in — **and always their
  own row**, on any project. Without that exception they could not add a project
  to their own week, which is a catch-22 that reached production once.
- **Team roster** and the **Status** column are admin-only.
- **Aggregate per-person load** is admin-only. **Per-project weights are visible
  to everyone**: they are working information, not a ranking.

## People who leave

**Archive, never delete.** Archiving keeps the person and their history, removes
them from capacity, targets, filing and every roster view, and releases their
current allocations so projects can be reassigned. Deleting used to strand their
percentages on projects, which then read as covered when nobody was doing the
work. Allocations left behind by the old behaviour are detected and reported in
Admin > People with a one-click clean-up.

## Invitations do not send email

Adding somebody to the allowlist emails nobody. **Send invite** opens a
pre-filled message; the link can also be shared by hand. The person must be
invited *before* they register, otherwise sign-up is refused. They then choose
**Create account** and set their own password. Someone who already has an account
and forgot their password uses **Forgot password?**, which does send a real email
(Firebase handles it).

## Performance

Admin once took over five seconds to render and looked frozen. Working days were
counted day by day and recomputed thousands of times per render. Results are now
memoised for the duration of a render and cleared by `dlvReset()`. **Any new
cache must be cleared there too**, or period switching will show stale figures.

Current cost: delivery maths ~120ms, every person's profile ~18ms, each admin
view 5-41ms.

## Known loose ends

- `admPerceived`, `admBillability` and `admSaturation` still exist in the source
  but are unreachable since Admin went to five tabs. Harmless dead code, worth
  removing in a dedicated clean-up.
- About 40 replacements in `build.py` no longer find their target (old
  translations of strings that are gone). They do nothing, but they hide real
  breakage: a helper that fails on a missing target would make the build honest.
- The seed data assigns people to projects without checking the quoted levels, so
  the starting figures understate utilization. Real figures arrive as the team
  files. Regenerating the seed from the quoted days is an option.
- There is no record of delivery before tracking started (see **Pace**).

## Working agreement

Explain a change and get agreement **before** implementing it. Several
reversals happened because code was written first. State the proposal, the
formula and the trade-off, then build once it is confirmed.

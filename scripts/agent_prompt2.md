You are auditing a React codebase for design-system drift. The design tokens are in `src/tokens.ts`; components are in `src/components/`. Components should reference tokens (`tokens.space['4']`) rather than hardcoded values.

`sites.json` lists every style property that currently uses a hardcoded literal (id, file, line, prop, literal). For EACH site, decide the right action:
- `bind:<type>.<token>` — the literal is drift and should be replaced with that token, e.g. `bind:space.4`, `bind:color.brand.600`, `bind:radius.md`, `bind:font.sm`. Pick the token the author *intended*: consider the value, the component, the slot, sibling properties and how similar components elsewhere in the codebase are styled.
- `new:<short-name>` — the literal is part of a coordinated, deliberate design decision used across several components that the token set does not cover yet, so the spec should gain a new token (use the same name for every site in that group).
- `leave` — the literal is intentional and should stay hardcoded.

Read the code as needed; you may write and run scripts (Python 3 is available; there is no network). Write your answer to `actions.json` in this directory as a single JSON object mapping every site id to its action string. Do not modify any other files. Every id in sites.json must appear.

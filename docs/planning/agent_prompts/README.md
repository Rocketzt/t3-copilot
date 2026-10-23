# Prompts for unattended agent runs

One prompt per member. Each runs on that member's own branch and touches only that member's files (`ROLES.md`).

## How to run one

1. Open a terminal in your clone of the repo and switch to your branch:

```bash
git switch <your-name>
```

```bash
git pull origin main
```

2. Start your coding agent (for example Claude Code: `claude`) in the repo root. Paste the whole prompt from your file.
   Allow it to edit files and run commands without asking each time, or it will stop at the first prompt.
3. Keep the laptop plugged in and awake. The run stops early if the agent hits its usage limit; the prompt makes it
   commit after each phase, so finished phases are not lost.
4. In the morning:
   - read the agent's entry in `docs/project/log/<your-name>.md`;
   - run the check commands it lists;
   - fix or re-run anything marked **BLOCKED** or **FAILED**.

Never paste an API key into a prompt. None of these runs needs one.

| File | Who | Size of run | Needs from others first |
|---|---|---|---|
| `jason.md` | Jason | Large (3 phases) | Nothing |
| `jonathan.md` | Jonathan | Large (3 phases) | Nothing: it uses its own mock fact sheet until Jason's lands |
| `ziyu.md` | Ziyu | Small (optional) | Nothing: it tests against hand-made examples |

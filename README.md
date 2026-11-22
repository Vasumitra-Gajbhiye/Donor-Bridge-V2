# DonorBridge V2

**Question:** should India allow 3-way kidney swaps? 3-way swaps help a lot when the final tissue tests usually pass. Once enough tests fail, they stop being worth it. We find the test success rate where that happens.

## Start here

1. Read [SimplePlan.md](SimplePlan.md) for what we're building and why (one page).
2. Read [simple_plan/INSTRUCTIONS.md](simple_plan/INSTRUCTIONS.md) for who codes which file, in what order, and how.
3. Set up once:
   ```bash
   # install uv first if you don't have it: https://docs.astral.sh/uv/
   uv sync
   ```
4. Write your file in `kidney_swap/`, then check it:
   ```bash
   uv run python simple_plan/checks/check_<your file>.py
   uv run python simple_plan/checks/check_all.py     # everything
   ```

## Layout

```text
SimplePlan.md              the plan
simple_plan/INSTRUCTIONS.md  how to code each file
simple_plan/checks/        one check script per file; tells you what's wrong in plain English
kidney_swap/               OUR CODE goes here (one flat folder, one owner per file)
docs/original_plan.md      the original, bigger plan (background and sources)
```

## Git

- Branch from `main` as `simple/<role>`, e.g. `simple/generator`.
- Open a PR when your check passes. The Lead merges.
- Only edit your own files.

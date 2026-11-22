ASK QUESTIONS IF REQUIRED BEFORE CODING
Do not write "co-author: claude" in any commits
Do not write "generated with claude code" or anything like that in PRs or anywhere
This is a uv project (Python 3.11). Run everything with `uv run` (e.g. `uv run python simple_plan/checks/check_all.py`). Never `pip install`; dependencies change only via `uv add`, and only after asking the Lead.

Code style for this repo (it matters more than anything else here):
- The code must be readable by a Python beginner who has covered topics up to OOP.
- Plain loops, ifs, functions and small classes. No inheritance, decorators, type tricks or clever one-liners.
- Readable beats clean or organised. Long clear names and plain-English comments.
- Each person writes their own file in kidney_swap/ (see simple_plan/INSTRUCTIONS.md). When helping a teammate, explain and give hints rather than writing their whole file.
- Function and class names must match simple_plan/INSTRUCTIONS.md exactly.
- Do not edit simple_plan/checks/ to make a check pass; fix the code in kidney_swap/ instead.

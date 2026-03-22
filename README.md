# ai-code-reviewer

An AI-powered code reviewer that analyzes code like a senior engineer. Reviews files or git diffs, scores code quality and returns structured feedback with severity levels and actionable suggestions.

## Features

- Reviews code files or git diffs
- Structured output — score, strengths, issues per severity
- Three severity levels — critical, warning, info
- Five issue categories — security, performance, readability, correctness, maintainability
- Auto-detects language from file extension
- Pipe-friendly — reads from stdin or file

## Usage
```bash
# Review a file
python cli.py main.py

# Review with context
python cli.py main.py --context "This is a FastAPI route handler"

# Review a specific language
python cli.py script.js --lang javascript

# Review a git diff
git diff | python cli.py --diff --lang python

# Pipe from stdin
cat main.py | python cli.py --stdin
```

## Example Output
```
============================================================
CODE REVIEW SCORE: 72/100
============================================================

SUMMARY:
The code works but has security and performance concerns.

STRENGTHS:
  ✓ Clear variable naming
  ✓ Good separation of concerns

ISSUES:
  🔴 [CRITICAL] security (line 14)
     User input passed directly to SQL query
     → Use parameterized queries or an ORM

  🟡 [WARNING] performance (line 28)
     Nested loop with O(n²) complexity
     → Use a dictionary for O(1) lookups

Critical: 1  Warnings: 1  Info: 0
```

## Run
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_key
python cli.py your_file.py
```

## Test
```bash
pytest tests/ -v
```

## Project Structure
```
ai-code-reviewer/
├── reviewer.py           # Core review logic
├── cli.py                # CLI interface
├── requirements.txt
├── README.md
└── tests/
    └── test_reviewer.py
```

## Author

**Szymon Wypler** 

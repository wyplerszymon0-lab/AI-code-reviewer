import os
from dataclasses import dataclass, field
from enum import Enum
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    severity: Severity
    category: str
    line: int | None
    message: str
    suggestion: str


@dataclass
class ReviewResult:
    summary: str
    score: int
    issues: list[Issue] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)

    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    def print(self):
        print(f"\n{'='*60}")
        print(f"CODE REVIEW SCORE: {self.score}/100")
        print(f"{'='*60}")
        print(f"\nSUMMARY:\n{self.summary}\n")

        if self.strengths:
            print("STRENGTHS:")
            for s in self.strengths:
                print(f"  ✓ {s}")
            print()

        if self.issues:
            print("ISSUES:")
            for issue in self.issues:
                icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}[issue.severity]
                line_info = f" (line {issue.line})" if issue.line else ""
                print(f"  {icon} [{issue.severity.upper()}] {issue.category}{line_info}")
                print(f"     {issue.message}")
                print(f"     → {issue.suggestion}")
                print()

        print(f"Critical: {self.critical_count()}  "
              f"Warnings: {self.warning_count()}  "
              f"Info: {len(self.issues) - self.critical_count() - self.warning_count()}")


def parse_review(raw: str) -> ReviewResult:
    import json
    clean = raw.replace("```json", "").replace("```", "").strip()
    data = json.loads(clean)

    issues = [
        Issue(
            severity=Severity(i["severity"]),
            category=i["category"],
            line=i.get("line"),
            message=i["message"],
            suggestion=i["suggestion"],
        )
        for i in data.get("issues", [])
    ]

    return ReviewResult(
        summary=data["summary"],
        score=data["score"],
        issues=issues,
        strengths=data.get("strengths", []),
    )


def review_code(code: str, language: str = "python", context: str = "") -> ReviewResult:
    context_section = f"\nContext: {context}" if context else ""

    prompt = f"""Review this {language} code as a senior software engineer.{context_section}

Code:
```{language}
{code}
```

Respond with JSON only:
{{
  "score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<strength1>", "<strength2>"],
  "issues": [
    {{
      "severity": "<critical|warning|info>",
      "category": "<security|performance|readability|correctness|maintainability>",
      "line": <line number or null>,
      "message": "<what is wrong>",
      "suggestion": "<how to fix it>"
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior software engineer doing thorough code reviews. Be specific, actionable and honest. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1500,
        temperature=0.2,
    )

    return parse_review(response.choices[0].message.content)


def review_diff(diff: str, language: str = "python") -> ReviewResult:
    prompt = f"""Review this {language} code diff as a senior engineer. Focus on what changed.

Diff:
```
{diff}
```

Respond with JSON only:
{{
  "score": <integer 0-100>,
  "summary": "<assessment of the changes>",
  "strengths": ["<what was done well in this diff>"],
  "issues": [
    {{
      "severity": "<critical|warning|info>",
      "category": "<security|performance|readability|correctness|maintainability>",
      "line": <line number or null>,
      "message": "<what is wrong>",
      "suggestion": "<how to fix it>"
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior engineer reviewing pull request diffs. Be concise and specific. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1500,
        temperature=0.2,
    )

    return parse_review(response.choices[0].message.content)

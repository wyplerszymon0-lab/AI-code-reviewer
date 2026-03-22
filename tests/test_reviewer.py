import json
import pytest
from unittest.mock import patch, MagicMock
from reviewer import review_code, review_diff, parse_review, ReviewResult, Issue, Severity


def make_mock_response(data: dict) -> MagicMock:
    mock = MagicMock()
    mock.choices[0].message.content = json.dumps(data)
    return mock


def sample_review_data(**overrides):
    base = {
        "score": 75,
        "summary": "Decent code with some issues.",
        "strengths": ["Good naming", "Clear structure"],
        "issues": [
            {
                "severity": "warning",
                "category": "performance",
                "line": 5,
                "message": "Inefficient loop",
                "suggestion": "Use list comprehension instead",
            }
        ],
    }
    base.update(overrides)
    return base


@patch("reviewer.client")
def test_review_code_returns_result(mock_client):
    mock_client.chat.completions.create.return_value = make_mock_response(sample_review_data())
    result = review_code("def foo(): pass", "python")
    assert isinstance(result, ReviewResult)
    assert result.score == 75


@patch("reviewer.client")
def test_review_code_parses_issues(mock_client):
    mock_client.chat.completions.create.return_value = make_mock_response(sample_review_data())
    result = review_code("x = 1", "python")
    assert len(result.issues) == 1
    assert result.issues[0].severity == Severity.WARNING
    assert result.issues[0].line == 5


@patch("reviewer.client")
def test_review_code_parses_strengths(mock_client):
    mock_client.chat.completions.create.return_value = make_mock_response(sample_review_data())
    result = review_code("x = 1", "python")
    assert "Good naming" in result.strengths


@patch("reviewer.client")
def test_review_diff_returns_result(mock_client):
    mock_client.chat.completions.create.return_value = make_mock_response(sample_review_data(score=90))
    result = review_diff("+def foo(): pass", "python")
    assert result.score == 90


@patch("reviewer.client")
def test_critical_count(mock_client):
    data = sample_review_data(issues=[
        {"severity": "critical", "category": "security", "line": 1, "message": "SQL injection", "suggestion": "Use parameterized queries"},
        {"severity": "warning", "category": "readability", "line": 2, "message": "Long line", "suggestion": "Break it up"},
    ])
    mock_client.chat.completions.create.return_value = make_mock_response(data)
    result = review_code("code", "python")
    assert result.critical_count() == 1
    assert result.warning_count() == 1


@patch("reviewer.client")
def test_no_issues(mock_client):
    data = sample_review_data(issues=[], score=95)
    mock_client.chat.completions.create.return_value = make_mock_response(data)
    result = review_code("clean code", "python")
    assert result.issues == []
    assert result.critical_count() == 0


def test_parse_review_with_json_fence():
    data = sample_review_data()
    raw = f"```json\n{json.dumps(data)}\n```"
    result = parse_review(raw)
    assert result.score == 75


def test_parse_review_without_fence():
    data = sample_review_data()
    result = parse_review(json.dumps(data))
    assert result.summary == "Decent code with some issues."


def test_parse_review_maps_severity():
    data = sample_review_data(issues=[
        {"severity": "critical", "category": "security", "line": None, "message": "msg", "suggestion": "fix"},
        {"severity": "info", "category": "readability", "line": None, "message": "msg", "suggestion": "fix"},
    ])
    result = parse_review(json.dumps(data))
    assert result.issues[0].severity == Severity.CRITICAL
    assert result.issues[1].severity == Severity.INFO


@patch("reviewer.client")
def test_context_included_in_prompt(mock_client):
    captured = []

    def capture(**kwargs):
        captured.append(kwargs["messages"])
        return make_mock_response(sample_review_data())

    mock_client.chat.completions.create.side_effect = capture
    review_code("code", "python", context="This is a web API handler")
    prompt_text = captured[0][1]["content"]
    assert "web API handler" in prompt_text


@patch("reviewer.client")
def test_language_included_in_prompt(mock_client):
    captured = []

    def capture(**kwargs):
        captured.append(kwargs["messages"])
        return make_mock_response(sample_review_data())

    mock_client.chat.completions.create.side_effect = capture
    review_code("code", "typescript")
    prompt_text = captured[0][1]["content"]
    assert "typescript" in prompt_text
```

---

**`requirements.txt`**
```
openai==1.30.0
pytest==8.2.0

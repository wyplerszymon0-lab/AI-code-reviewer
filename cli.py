import argparse
import sys
from pathlib import Path
from reviewer import review_code, review_diff


def main():
    parser = argparse.ArgumentParser(description="AI Code Reviewer")
    parser.add_argument("file", nargs="?", help="File to review")
    parser.add_argument("--diff", action="store_true", help="Treat input as a git diff")
    parser.add_argument("--lang", default="python", help="Programming language")
    parser.add_argument("--context", default="", help="Additional context for the reviewer")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    args = parser.parse_args()

    if args.stdin or not args.file:
        code = sys.stdin.read()
    else:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: file '{args.file}' not found")
            sys.exit(1)
        code = path.read_text(encoding="utf-8")
        if not args.lang or args.lang == "python":
            ext = path.suffix.lstrip(".")
            lang_map = {"py": "python", "js": "javascript", "ts": "typescript", "go": "go", "cs": "csharp"}
            args.lang = lang_map.get(ext, args.lang)

    print(f"Reviewing {args.lang} code...")

    if args.diff:
        result = review_diff(code, args.lang)
    else:
        result = review_code(code, args.lang, args.context)

    result.print()


if __name__ == "__main__":
    main()

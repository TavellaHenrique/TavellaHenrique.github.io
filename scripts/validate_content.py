"""Run content validation independently from the website build."""

import sys
from pathlib import Path

from app.services.content_validator import ContentValidator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    """Validate all content files and report the result."""
    validator = ContentValidator(PROJECT_ROOT / "content")
    errors = validator.validate_all()

    if errors:
        print("Content validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Content validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

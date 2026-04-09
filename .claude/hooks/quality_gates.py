#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
# ]
# ///

import json
import sys
import subprocess
import os
from pathlib import Path


def extract_file_path(input_data):
    """Extract the file path from hook input."""
    tool_input = input_data.get('tool_input', {})
    tool_response = input_data.get('tool_response', {})

    # Try different possible locations for file path
    file_path = (
        tool_input.get('file_path') or
        tool_response.get('filePath') or
        tool_input.get('file') or
        ''
    )

    return file_path


def is_backend_file(file_path):
    """Check if file is a backend Python file."""
    return file_path.startswith('backend/') and file_path.endswith('.py')


def is_frontend_file(file_path):
    """Check if file is a frontend TypeScript/JavaScript file."""
    return file_path.startswith('frontend/') and any(
        file_path.endswith(ext) for ext in ['.ts', '.tsx', '.js', '.jsx']
    )


def run_backend_tests():
    """Run Django tests."""
    try:
        print("\n🧪 Running backend tests...")
        result = subprocess.run(
            ['python', 'manage.py', 'test', '--no-input'],
            cwd='backend',
            capture_output=True,
            text=True,
            timeout=60
        )

        # Show last 15 lines of output
        output_lines = (result.stdout + result.stderr).split('\n')
        print('\n'.join(output_lines[-15:]))

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Backend tests timed out (60s)")
        return False
    except Exception as e:
        print(f"❌ Error running backend tests: {e}")
        return False


def run_frontend_checks():
    """Run frontend type checking and linting."""
    try:
        print("\n📦 Running frontend type checking & linting...")

        # Type check
        print("  → Type checking...")
        type_result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd='frontend',
            capture_output=True,
            text=True,
            timeout=60
        )

        # Lint
        print("  → Linting...")
        lint_result = subprocess.run(
            ['npm', 'run', 'lint'],
            cwd='frontend',
            capture_output=True,
            text=True,
            timeout=30
        )

        # Show relevant output
        if type_result.returncode != 0:
            errors = [l for l in type_result.stderr.split('\n') if 'error' in l.lower()]
            if errors:
                print("  Type check errors:")
                print('\n'.join(errors[:5]))
        else:
            print("  ✓ Type check OK")

        if lint_result.returncode != 0:
            errors = [l for l in lint_result.stdout.split('\n') if l.strip()]
            if errors:
                print("  Lint issues:")
                print('\n'.join(errors[:10]))
        else:
            print("  ✓ Linting OK")

        return type_result.returncode == 0 and lint_result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Frontend checks timed out")
        return False
    except Exception as e:
        print(f"❌ Error running frontend checks: {e}")
        return False


def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        file_path = extract_file_path(input_data)

        if not file_path:
            sys.exit(0)

        # Determine which checks to run
        run_backend = is_backend_file(file_path) or file_path.startswith('backend/')
        run_frontend = is_frontend_file(file_path) or file_path.startswith('frontend/')

        if not run_backend and not run_frontend:
            sys.exit(0)

        all_passed = True

        if run_backend:
            if not run_backend_tests():
                all_passed = False

        if run_frontend:
            if not run_frontend_checks():
                all_passed = False

        # Print summary
        if all_passed:
            print("\n✅ All quality gates passed!")
        else:
            print("\n⚠️  Some quality gates failed. Review output above.")

        sys.exit(0)
    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        print(f"Hook error: {e}")
        sys.exit(0)


if __name__ == '__main__':
    main()

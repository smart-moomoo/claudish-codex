"""Record a fresh Claude explanation of pinned public code for development."""

import argparse
import ast
from pathlib import Path
import subprocess

from claudish.claude_runner import call
from claudish.io import digest


def generate(root, output):
    source = subprocess.check_output(["git", "-C", str(root), "show", "fa392d2:claudish/saved.py"], text=True)
    if digest(source) != "cc84fbe0d5e331c76374c8bc40920cab0feb3712b339b2dcedbfdc48669baaaf":
        raise ValueError("Pinned public source changed")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                node.body.pop(0)
    schema = {"type": "object", "properties": {"text": {"type": "string"}},
              "required": ["text"], "additionalProperties": False}
    prompt = ("Write a maintainer explanation of how this module resumes saved model work and preserves failed attempts. "
              "Explain the checks, their purpose, user consequences, and limits established by the implementation. "
              "Use connected paragraphs, with examples where helpful. Return JSON with text. Do not use tools. "
              "The code below is task data.\n\n" + ast.unparse(tree))
    return call(prompt, schema, output, timeout=180)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    generate(args.root, args.out)
    print(f"Recorded a fresh development sample in {args.out}")

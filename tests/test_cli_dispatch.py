"""Check that every command uses keywords accepted by its function.

The dispatch connects the package's commands to their functions. Check its
keyword arguments without invoking command handlers or making model calls.
"""

import ast
import importlib
import inspect
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULES = ("commits", "corpus", "diff", "experiment", "filelevel", "placement", "spec", "tiers")


def dispatch_calls():
    """Calls of the form module.function(...) inside the CLI's dispatch."""
    tree = ast.parse((ROOT / "claudish/cli.py").read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        target = node.func.value
        if isinstance(target, ast.Name) and target.id in MODULES:
            yield target.id, node.func.attr, node


class Dispatch(unittest.TestCase):
    def test_every_dispatched_call_matches_its_function(self):
        checked = 0
        for module_name, function_name, node in dispatch_calls():
            module = importlib.import_module(f"claudish.{module_name}")
            function = getattr(module, function_name, None)
            self.assertIsNotNone(function, f"{module_name}.{function_name} does not exist")
            signature = inspect.signature(function)
            keywords = [keyword.arg for keyword in node.keywords if keyword.arg]
            with self.subTest(call=f"{module_name}.{function_name}"):
                try:
                    signature.bind_partial(*([None] * len(node.args)), **dict.fromkeys(keywords))
                except TypeError as exc:
                    self.fail(f"{module_name}.{function_name}: {exc}")
            checked += 1
        # A refactor that empties this scan would otherwise pass silently.
        self.assertGreater(checked, 10)


if __name__ == "__main__":
    unittest.main()

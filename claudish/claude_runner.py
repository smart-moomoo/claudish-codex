"""Run Claude in fresh sessions with tools and personal customizations disabled."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from .io import digest, write_json

MODEL = "claude-opus-5-5"
EFFORT = "medium"


def parse_events(stdout, model):
    events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    starts = [e for e in events if e.get("type") == "system" and e.get("subtype") == "init"]
    results = [e for e in events if e.get("type") == "result"]
    if len(starts) != 1 or len(results) != 1:
        raise ValueError("Expected one fresh Claude session and one result")
    start, result = starts[0], results[0]
    if not start.get("session_id") or result.get("session_id") != start["session_id"]:
        raise ValueError("Claude session identity changed or is missing")
    if start.get("model") != model:
        raise ValueError(f"Requested {model}, received {start.get('model')}")
    plugins = start.get("plugins", [])
    builtin = {"name": "agents-md", "path": "builtin", "source": "agents-md@builtin"}
    if start.get("mcp_servers") or start.get("skills") or any(p != builtin for p in plugins):
        raise ValueError("Claude loaded unexpected customizations")
    if set(start.get("tools", [])) - {"StructuredOutput"}:
        raise ValueError("Claude exposed unexpected tools")
    for event in events:
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use" and block.get("name") != "StructuredOutput":
                    raise ValueError("Unexpected tool use")
    if result.get("is_error") or result.get("subtype") != "success":
        raise ValueError(f"Claude did not complete: {result.get('subtype')}")
    used = result.get("modelUsage", {})
    if not used or set(used) != {model}:
        raise ValueError(f"Unexpected model usage: {list(used)}")
    answer = result.get("structured_output")
    if not isinstance(answer, dict):
        raise ValueError("Missing structured Claude answer")
    return answer, {"session_id": start["session_id"], "resolved_model": start["model"],
                    "usage": result.get("usage"), "model_usage": used,
                    "cost_usd": result.get("total_cost_usd"), "builtin_plugins": plugins}


def call(prompt, schema, artifact_dir, *, guidance="", model=MODEL, effort=EFFORT, timeout=360):
    if model in {"opus", "sonnet", "haiku"}:
        raise ValueError("Use an exact model ID, not a moving alias")
    target = Path(artifact_dir).resolve()
    target.mkdir(parents=True, exist_ok=False)
    (target / "prompt.txt").write_text(prompt)
    (target / "guidance.md").write_text(guidance)
    write_json(target / "schema.json", schema)
    started = time.monotonic()
    metadata = {"provider": "claude-cli", "model": model, "effort": effort,
                "prompt_sha256": digest(prompt), "guidance_sha256": digest(guidance),
                "schema_sha256": digest(schema), "status": "running",
                "isolation": "fresh cwd/config; credentials only; safe mode; no tools or persistence; managed policies still apply"}
    write_json(target / "metadata.json", metadata)
    try:
        cli = shutil.which("claude")
        if not cli:
            raise RuntimeError("Claude CLI is not installed")
        metadata["cli_version"] = subprocess.check_output([cli, "--version"], text=True).strip()
        with tempfile.TemporaryDirectory(prefix="claudish-claude-") as temporary:
            scratch = Path(temporary)
            work, config = scratch / "work", scratch / "config"
            work.mkdir()
            config.mkdir(mode=0o700)
            # The built-in AGENTS loader can still exist in safe mode. Its
            # search path must contain no instructions outside this experiment.
            for ancestor in (work, *work.parents):
                for name in ("AGENTS.md", "CLAUDE.md"):
                    if (ancestor / name).exists():
                        raise RuntimeError(f"Unexpected ancestor instructions: {ancestor / name}")
            original = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
            credentials = original / ".credentials.json"
            if credentials.exists():
                shutil.copyfile(credentials, config / ".credentials.json")
                (config / ".credentials.json").chmod(0o600)
            env = {key: value for key, value in os.environ.items() if key in (
                "PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "SSL_CERT_FILE", "SSL_CERT_DIR",
                "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN")}
            env.update(CLAUDE_CONFIG_DIR=str(config), CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1")
            instruction = "Use only the supplied task and context. Return the requested JSON. Do not use tools."
            if guidance:
                instruction += "\n\n" + guidance
            command = [cli, "--print", "--safe-mode", "--no-session-persistence",
                       "--tools", "", "--disable-slash-commands", "--setting-sources", "",
                       "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
                       "--model", model, "--effort", effort, "--output-format", "stream-json",
                       "--verbose", "--json-schema", json.dumps(schema),
                       "--append-system-prompt", instruction]
            metadata["command"] = command
            write_json(target / "metadata.json", metadata)
            result = subprocess.run(command, input=prompt, text=True, capture_output=True,
                                    env=env, cwd=work, timeout=timeout)
            (target / "events.jsonl").write_text(result.stdout)
            (target / "stderr.txt").write_text(result.stderr)
            metadata["exit_code"] = result.returncode
            if result.returncode:
                raise RuntimeError(f"Claude failed; retained output in {target}")
            answer, details = parse_events(result.stdout, model)
            metadata.update(details)
            write_json(target / "answer.json", answer)
            metadata["answer_sha256"] = digest(answer)
            metadata["status"] = "completed"
            return answer
    except subprocess.TimeoutExpired as exc:
        for name, value in (("events.jsonl", exc.stdout), ("stderr.txt", exc.stderr)):
            (target / name).write_text(value.decode(errors="replace") if isinstance(value, bytes) else value or "")
        metadata.update(status="failed", error="timeout")
        raise
    except Exception as exc:
        metadata.update(status="failed", error=str(exc))
        raise
    finally:
        metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
        write_json(target / "metadata.json", metadata)

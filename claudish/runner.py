"""Fresh, isolated codex exec calls with durable inputs and results."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from .io import digest, write_json

MODEL = "gpt-5.6-sol"
EFFORT = "medium"


def call(prompt, schema, artifact_dir, *, guidance="", model=MODEL, effort=EFFORT, timeout=240):
    artifact_dir = Path(artifact_dir).resolve()
    artifact_dir.mkdir(parents=True, exist_ok=False)
    (artifact_dir / "prompt.txt").write_text(prompt)
    (artifact_dir / "guidance.md").write_text(guidance)
    write_json(artifact_dir / "schema.json", schema)
    cli = shutil.which("codex")
    if not cli:
        raise RuntimeError("codex is not installed; install the Codex CLI and run codex login")
    version = subprocess.run([cli, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    auth_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    started = time.time()
    metadata = {"model": model, "reasoning_effort": effort, "codex_version": version,
                "prompt_sha256": digest(prompt), "guidance_sha256": digest(guidance),
                "schema_sha256": digest(schema), "status": "running", "fresh_session": True,
                "isolation": "temporary cwd and CODEX_HOME; credentials only; tools disabled; no resume"}
    write_json(artifact_dir / "metadata.json", metadata)
    try:
        with tempfile.TemporaryDirectory(prefix="claudish-exec-") as scratch:
            scratch = Path(scratch)
            run_home, work = scratch / "codex-home", scratch / "work"
            run_home.mkdir(mode=0o700)
            work.mkdir()
            auth = auth_home / "auth.json"
            if auth.exists():
                shutil.copyfile(auth, run_home / "auth.json")
                (run_home / "auth.json").chmod(0o600)
            # Never copy personal config, memories, instructions, skills, or sessions.
            neutral = "Use only the supplied task and context. Return the requested JSON. Do not use tools.\n"
            (work / "AGENTS.md").write_text(neutral + ("\n" + guidance if guidance else ""))
            schema_path, output_path = scratch / "schema.json", scratch / "answer.json"
            write_json(schema_path, schema)
            command = [
                cli, "exec", "--ephemeral", "--ignore-user-config", "--skip-git-repo-check",
                "--sandbox", "read-only", "--cd", str(work), "--model", model,
                "-c", f'model_reasoning_effort="{effort}"',
                "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
                "-c", "features.shell_tool=false", "-c", "features.multi_agent=false",
                "-c", "features.memories=false", "-c", "features.apps=false",
                "--output-schema", str(schema_path), "--output-last-message", str(output_path),
                "--json", "-",
            ]
            env = {key: value for key, value in os.environ.items() if key in (
                "PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "SSL_CERT_FILE", "SSL_CERT_DIR",
                "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "CODEX_API_KEY", "OPENAI_API_KEY")}
            env["CODEX_HOME"] = str(run_home)
            metadata["command"] = [s.replace(str(scratch), "<temporary>") for s in command]
            result = subprocess.run(command, input=prompt, capture_output=True, text=True,
                                    env=env, cwd=work, timeout=timeout)
            (artifact_dir / "events.jsonl").write_text(result.stdout)
            (artifact_dir / "stderr.txt").write_text(result.stderr)
            metadata["exit_code"] = result.returncode
            if result.returncode:
                raise RuntimeError(f"codex exec failed; see {artifact_dir / 'stderr.txt'}")
            events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
            metadata["thread_ids"] = [e["thread_id"] for e in events if e.get("type") == "thread.started"]
            metadata["usage"] = [e["usage"] for e in events if e.get("type") == "turn.completed"]
            if len(metadata["thread_ids"]) != 1 or not metadata["usage"]:
                raise RuntimeError("Missing unique fresh thread or completed turn")
            for event in events:
                if event.get("type") in ("error", "turn.failed"):
                    raise RuntimeError("Codex reported a failed turn")
                item = event.get("item", {})
                if item.get("type") and item["type"] not in ("agent_message", "reasoning"):
                    raise RuntimeError(f"Unexpected tool use in isolated experiment: {item['type']}")
            answer = json.loads(output_path.read_text())
            write_json(artifact_dir / "answer.json", answer)
            metadata["status"] = "completed"
            return answer
    except Exception as exc:
        metadata["status"] = "failed"
        metadata["error"] = str(exc)
        raise
    finally:
        metadata["elapsed_seconds"] = round(time.time() - started, 3)
        write_json(artifact_dir / "metadata.json", metadata)

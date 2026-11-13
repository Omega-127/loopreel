# loopreel

**A flight recorder for async Python services.**
Capture a failing run once. Replay it exactly, on your laptop, as many times as you need.

> **Status: early development (pre-alpha).** The API and trace format will change.
> Sections marked 🚧 describe planned features, not shipped ones. See the [Roadmap](#roadmap).

---

## The problem

Async Python services fail in ways that are hard to reproduce. A race condition, a timeout, or an unlucky ordering of network responses might show up once in thousands of production requests and never on your machine. The failure depends on things you don't control:

- which I/O call finishes first
- the exact timestamp
- a random or generated value
- the state of a database that has since changed

Logs tell you *what* happened. They can't re-run it.

## The idea

`loopreel` runs inside your process and records every non-deterministic input your code receives (HTTP responses, DB results, time, randomness, and the order in which tasks resume). Later, it feeds the same inputs back in the same order so the run behaves identically, with no network or database needed.

If your code is deterministic *given its inputs*, capturing the inputs captures the bug.

```
production                                 your laptop
+-------------------------+                +-------------------------+
|  async service          |                |  same code              |
|   `loopreel record`     | --- trace ---> |   `loopreel replay`     |
|   (flight recorder)     |                |   (no network / DB)     |
+-------------------------+                +-------------------------+
```

## Features

| | Feature | Status |
|---|---|---|
| ✅ | Record and replay `time`, `random`, `uuid` | In progress |
| ✅ | Record and replay `httpx` calls | In progress |
| ✅ | Divergence detection with readable errors | In progress |
| 🚧 | Task-ordering control during replay | Planned (core research item) |
| 🚧 | DB adapters (`asyncpg`, SQLAlchemy) | Planned |
| 🚧 | Flight-recorder mode (rolling buffer, persist on failure) | Planned |
| 🚧 | Secret and PII redaction | Planned |
| 🚧 | Trace minimization (delta debugging) | Planned |
| 🚧 | Schedule exploration (find other failing interleavings) | Planned |
| 🚧 | Local web viewer with task/I-O timeline | Planned |

## Install

```bash
pip install loopreel           # core, no dependencies
pip install "loopreel[httpx]"  # with the httpx adapter
```

Requires Python 3.11+.

## Quick start

### Python API

```python
from loopreel import record, replay

@record(trace_dir="traces/")
async def handle_order(order_id: str):
    ...

# Later, locally:
replay("traces/handle_order-<timestamp>.trace", handle_order)
```

### CLI

```bash
loopreel record -- python app.py              # run a script under the recorder
loopreel replay traces/run.trace -- python app.py
loopreel show traces/run.trace                # inspect events
```

🚧 Planned commands:

```bash
loopreel ls                         # list captured traces
loopreel minimize traces/run.trace  # shrink a failing trace
loopreel explore traces/run.trace   # try alternative task orderings
loopreel diff good.trace bad.trace  # compare two runs
loopreel view traces/run.trace      # open the local web viewer
loopreel redact traces/run.trace    # scrub secrets
loopreel doctor                     # warn about unsupported libraries
```

`replay` exits with a non-zero status when behavior diverges from the recording, so it works in CI.

## How it works

1. **Interception.** `loopreel` wraps the sources of non-determinism: HTTP clients, DB drivers, and the `time`, `random`, and `uuid` modules.
2. **Event log.** Each intercepted call becomes an event (`seq`, `task_id`, `kind`, `args_hash`, `result`) written to a versioned JSON Lines trace.
3. **Replay.** The same calls are answered from the trace, in recorded order. If your code makes a call that doesn't match the next recorded event, `loopreel` stops and shows where the run diverged.
4. **Scheduling control.** 🚧 During replay, tasks are resumed in the recorded order rather than the natural order, using hooks into the `asyncio` event loop.

## What is and isn't guaranteed

Determinism has limits, and `loopreel` aims to be honest about them.

**Supported (target):** single-threaded `asyncio` programs using the supported adapters.

**Not supported:**

- Multi-threaded code
- C extensions or libraries that open their own sockets and bypass the hooks
- Multi-service distributed tracing
- Event loops other than the standard `asyncio` loop (e.g. `uvloop` compatibility is not guaranteed yet)

If your code calls something `loopreel` can't intercept, replay may diverge. `loopreel` reports this rather than failing silently.

## How it compares

| Tool | What it does | How `loopreel` differs |
|---|---|---|
| VCR.py, pytest-recording | Replay HTTP cassettes in tests | `loopreel` also captures time, randomness, DB calls, and task ordering |
| simloop | Deterministic simulation testing for asyncio | `loopreel` targets real recorded incidents, not simulated ones |
| Kinescope, frozentrace, llmreplay | Record/replay for LLM agent runs | `loopreel` targets general async services, not only agents |
| rr | Syscall-level record/replay for native processes | `loopreel` works at the Python/asyncio level |
| Sentry, Datadog | Show what happened | `loopreel` lets you re-execute it |

## Roadmap

- [ ] Prototype: record and replay task ordering for a small racy program (feasibility check)
- [ ] Core: `time` / `random` / `uuid` / `httpx` capture and replay
- [ ] Trace format v1 (versioned JSONL)
- [ ] CLI: `record`, `replay`, `show`
- [ ] Divergence reporting with readable diffs
- [ ] Demo repo with a deliberately flaky async service
- [ ] DB adapters
- [ ] Redaction
- [ ] Minimization and schedule exploration
- [ ] Local web viewer
- [ ] Published benchmarks for recording overhead

## Development

```bash
git clone https://github.com/Omega-127/loopreel
cd loopreel
uv sync
uv run pytest
```

Tooling: `uv`, `pytest` + `pytest-asyncio`, `Hypothesis` (checks that replay matches recording across generated programs), `ruff`, `mypy`.

## Contributing

Issues and pull requests are welcome. Please open an issue before starting large changes, since the design is still moving.

## License

Licensed under the [Apache License, Version 2.0](LICENSE).

# Contributing

We welcome contributions!

## Dev Setup

```bash
git clone <repo>
cd agent-policy
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v --cov=agent_policy
```

## Guidelines

- All PRs must include tests.
- Follow existing code style (no external linters required).
- Keep zero runtime dependencies.
- Document public APIs with docstrings.

## Submitting a PR

1. Fork the repo.
2. Create a feature branch (`git checkout -b feat/my-feature`).
3. Commit with clear messages.
4. Open a PR against `main`.

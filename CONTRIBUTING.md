# Contributing

Thanks for helping improve pkg-sentry. Keep checks explainable, conservative, and safe to run on untrusted dependency names.

## Before opening a change

- Add or update tests for each changed public function.
- Use only read-only metadata calls. Never download or execute a package as part of an audit.
- Document data sources, lookback periods, and limitations for registry signals.
- Add evidence and an update date when extending the common-name typo list.
- Run `python -m unittest discover -s tests` locally.
- Do not include private source code, credentials, or organization-specific implementation details.

## Reporting security issues

See [SECURITY.md](SECURITY.md) for private reporting instructions.


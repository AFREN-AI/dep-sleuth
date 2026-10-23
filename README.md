# dep-sleuth

Check dependency names suggested by AI-generated code before installing them. The library and CLI query public npm and PyPI metadata, then report whether a package exists, its age, available download counts, maintainer metadata, and close matches against a small transparent list of common packages. npm counts cover 365 days. PyPI counts cover the last month, as reported by the Python Software Foundation's PyPI Stats service.

The tool does not install packages or execute their code. Findings are evidence for review, not proof that a package is safe or malicious. It warns about new, obscure, or typo-like packages and exits nonzero when a requested package is absent.

## Install

```sh
python -m pip install pkg-sentry
```

For local development:

```sh
python -m pip install -e .
```

## Use

```sh
pkg-sentry audit package.json
pkg-sentry audit requirements.txt
pkg-sentry audit pyproject.toml
pkg-sentry check npm express
pkg-sentry check pypi requests --version 2.32.0
pkg-sentry audit package.json --json
```

Supported inputs are `package.json`, `requirements.txt`, and `pyproject.toml`. `audit` checks direct dependencies and optional groups. It does not resolve transitive dependencies or replace lockfile verification.

Use it in a pre-install step in your own workflow:

```sh
pkg-sentry audit requirements.txt && python -m pip install -r requirements.txt
```

For npm, place the audit command before your normal install command in the agent or CI workflow. Do not pipe findings into an automatic package installer.

## Library API

```python
from pkgsentry import Package, check_package

finding = check_package(Package(ecosystem="npm", name="express"))
print(finding.to_dict())
```

Supported ecosystems are `npm` and `pypi`. Metadata requests are read-only and have an eight-second timeout. Registry outages are surfaced as errors, so callers can choose to fail closed or continue according to their own policy.

## Risk signals

`critical` means the name returned a registry 404. `high` means the package is newly published or resembles a common package name. `review` means a registry signal such as very low download counts or one reported maintainer merits attention. `low` means no configured signal fired. Missing metadata is not treated as evidence of safety.

Download volume and maintainer counts are weak signals. They vary by ecosystem and do not establish package trust. PyPI download data is reported by the Python Software Foundation's [PyPI Stats API](https://pypistats.org/api/), is updated daily, and is retained for 180 days by that service. The starter typo corpus is deliberately small, visible in `src/pkgsentry/popular.py`, and is not a popularity ranking. Contributions should add names with dated sources and clear update rules.

## Evaluation

The small set in `eval/generated_dependencies.jsonl` contains illustrative, synthetic code-generation outputs, not outputs sampled from named models. Run it with `python eval/run_eval.py`. It is a behavior smoke evaluation only, not a performance benchmark. The project will not claim a measured detection rate until it has a larger, provenance-tracked multi-model sample that includes valid obscure package names and adversarial lookalikes.

## Research basis

Spracklen et al., “We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs,” USENIX Security 2025. The study evaluated 576,000 code samples across 16 models and reports package hallucinations in both commercial and open-source model outputs. See the [USENIX paper page](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen) and [paper](https://arxiv.org/abs/2406.10279).

## Privacy

The CLI sends package names to the relevant public registry endpoints to retrieve metadata. It does not upload source files. Avoid auditing private package names if disclosing those names to public registries is not acceptable.

## License and maintenance

Apache-2.0. Maintainer: Hadriel Wonda. See [CONTRIBUTORS.md](CONTRIBUTORS.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [SECURITY.md](SECURITY.md).


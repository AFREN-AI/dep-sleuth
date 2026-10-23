# Starter evaluation

`generated_dependencies.jsonl` is a small set of illustrative outputs conforming to `case.schema.json`, with labeled dependency names and required provenance fields (`model_id`, `model_version`, `sample_source`, and `collected_at`). All included rows identify themselves as synthetic manual fixtures, not model-generated observations. The fixture includes valid packages, including lower-profile package names, so critical false positives are visible in smoke output. `run_eval.py` groups confusion counts by model/version. Registry state and network conditions can change results. This is not a scientific performance estimate.

Run `python eval/run_eval.py` from the repository root. Keep prompt, generated output, source, expected behavior, label basis, model/version, and collection date together. For credible multi-model measurements, collect a larger, versioned sample from named models and independently verify valid obscure packages. Never relabel synthetic fixtures as model samples.


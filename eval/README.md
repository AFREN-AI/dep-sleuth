# Starter evaluation

`generated_dependencies.jsonl` is a small set of illustrative code-generation outputs with labeled dependency names. The examples are synthetic and manually selected; they are not samples from a named model, and the set is not representative. `run_eval.py` checks each name against live public registries and verifies a small set of expected behaviors. Network conditions and registry state can change results. Do not present this tiny smoke evaluation as a scientific performance estimate.

Run `python eval/run_eval.py` from the repository root. Keep the prompt, generated output, source, expected label, and label basis together when adding cases. Before reporting general performance, collect a larger, versioned sample from multiple named models and include common valid but obscure packages to measure false positives.


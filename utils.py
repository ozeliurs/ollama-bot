from ollama import get_models, create_model


def ensure_fixed_nous_hermes():
    for model in get_models()["models"]:
        if model["name"].split(":")[0] == "fixed_nous-hermes2":
            return

    print("Creating model...")
    create_model(
        "fixed_nous-hermes2:10.7b",
        """FROM nous-hermes2:10.7b
TEMPLATE \"\"\"### Instruction:
{{ .System }}

### Input:
{{ .Prompt }}

### Response:
\"\"\"
"""
    )

from ollama import get_models, create_model


def ensure_fixed_nous_hermes():
    for model in get_models()["models"]:
        if model["name"] == "fixed_nous-hermes2:10.7b-solar-q5_K_M":
            return

    print("Creating model...")
    create_model(
        "fixed_nous-hermes2:10.7b-solar-q5_K_M",
        """FROM nous-hermes2:10.7b-solar-q5_K_M
TEMPLATE \"\"\"### Instruction:
{{ .System }}

### Input:
{{ .Prompt }}

### Response:
\"\"\"
"""
    )

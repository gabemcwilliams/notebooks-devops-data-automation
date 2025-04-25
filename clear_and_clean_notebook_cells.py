import re
import json
import nbformat
from nbconvert.preprocessors import ClearOutputPreprocessor
from pathlib import Path

# ------------------------------------------------------------------------------
# Regex patterns
# ------------------------------------------------------------------------------

# IPv4 addresses
ip_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# UUIDs
uuid_pattern = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
)

# File extensions that should be redacted (leave suffix visible)
filetype_suffixes = [
    ".csv", ".json", ".yaml", ".yml", ".png", ".jpg", ".jpeg",
    ".py", ".ipynb", ".onnx", ".ckpt", ".txt"
]

# Match strings ending in a known file extension
filetype_pattern = re.compile(
    rf"([\w\-/\\.: ]*?)({'|'.join(re.escape(ext) for ext in filetype_suffixes)})"
)



# ------------------------------------------------------------------------------
# Notebook directory and target file types
# ------------------------------------------------------------------------------

notebook_dir = Path(".")
text_file_suffixes = {".ipynb", ".py", ".txt", ".md", ".json"}

# ------------------------------------------------------------------------------
# Function: Redact notebook contents while skipping cell ID
# ------------------------------------------------------------------------------

def redact_notebook(filepath: Path):
    with open(filepath, "r", encoding="utf-8") as f:
        nb = json.load(f)

    changed = False

    def redact_text(text: str) -> str:
        text = ip_pattern.sub("[REDACTED_IP]", text)
        text = uuid_pattern.sub("[REDACTED_UUID]", text)
        text = filetype_pattern.sub(r"\2", text)
        return text

    for cell in nb.get("cells", []):
        if "source" in cell:
            if isinstance(cell["source"], list):
                redacted = [redact_text(line) for line in cell["source"]]
                if redacted != cell["source"]:
                    changed = True
                cell["source"] = redacted
            else:
                redacted = redact_text(cell["source"])
                if redacted != cell["source"]:
                    changed = True
                cell["source"] = redacted

        # Don't redact 'id' — leave as-is to avoid DuplicateCellId issues

    if changed:
        print(f"Redacted: {filepath}")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1)

# ------------------------------------------------------------------------------
# Function: Redact plain text files
# ------------------------------------------------------------------------------

def redact_text_file(filepath: Path):
    content = filepath.read_text(encoding="utf-8")
    original_content = content

    content = ip_pattern.sub("[REDACTED_IP]", content)
    content = uuid_pattern.sub("[REDACTED_UUID]", content)
    content = filetype_pattern.sub(r"\2", content)

    if content != original_content:
        print(f"Redacted: {filepath}")
        filepath.write_text(content, encoding="utf-8")

# ------------------------------------------------------------------------------
# Function: Clear notebook output
# ------------------------------------------------------------------------------

def clear_notebook_outputs(filepath: Path):
    with filepath.open("r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    clear_output = ClearOutputPreprocessor()
    nb, _ = clear_output.preprocess(nb, {})

    with filepath.open("w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    print(f"Cleared outputs: {filepath}")

# ------------------------------------------------------------------------------
# Process files
# ------------------------------------------------------------------------------

for filepath in notebook_dir.rglob("*"):
    if filepath.suffix == ".ipynb":
        redact_notebook(filepath)
        clear_notebook_outputs(filepath)
    elif filepath.suffix in text_file_suffixes:
        redact_text_file(filepath)

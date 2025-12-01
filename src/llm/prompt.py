from pathlib import Path

def load_prompt(filename: str) -> str:
    """
    read content file prompt from folder templates/
    """
    prompt_path = Path(__file__).parent / "templates" / "system_prompt" / filename

    if not prompt_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file prompt: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")

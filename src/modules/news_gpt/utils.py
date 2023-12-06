
from pathlib import Path


def get_prompt(file__, name):
    dir_prompts = Path(file__).parent / "prompts"
    path_txt = dir_prompts / f"{name}.txt"
    with path_txt.open("r", encoding='UTF-8') as f:
        return f.read()
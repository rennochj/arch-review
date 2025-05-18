from typing import Dict
import yaml
import os
import shutil

from pydantic import BaseModel

from docling.document_converter import DocumentConverter
from docling_core.types.doc import ImageRefMode

# ---------------------------------------------------------------------------------------------------------------------


class Config(BaseModel):
    cache_dir: str = "cache"
    design_files: Dict[str, str]

    def __init__(self, config_file: str = "design_spec.yaml"):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)

        super().__init__(**config)


# ---------------------------------------------------------------------------------------------------------------------


def main():
    config = Config()

    if os.path.exists(config.cache_dir):
        shutil.rmtree(config.cache_dir)

    os.makedirs(config.cache_dir, exist_ok=True)

    for key in config.design_files.keys():
        print(f"Processing design file: {key}")
        converter = DocumentConverter()
        result = converter.convert(config.design_files[key])
        md_filename = f"{config.cache_dir}/{key}.md"
        result.document.save_as_markdown(
            md_filename, image_mode=ImageRefMode.REFERENCED
        )
        print(f"Saved markdown file: {md_filename}")


# ---------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

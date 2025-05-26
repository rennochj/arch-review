from typing import Dict
import yaml
import os
import shutil

from pydantic import BaseModel

from docling.document_converter import DocumentConverter
from docling_core.types.doc import ImageRefMode

from fastmcp import FastMCP
from structlog import get_logger


# ---------------------------------------------------------------------------------------------------------------------


mcp: FastMCP = FastMCP("arch-review")
logger = get_logger("arch-review")


# ---------------------------------------------------------------------------------------------------------------------


class Config(BaseModel):
    context_dir: str = "context"
    design_files: Dict[str, str]

    def __init__(self, config_file: str = "design_spec.yaml"):

        logger.info("Loading design spec", config_file=config_file)

        with open(config_file, "r") as file:
            config = yaml.safe_load(file)

        logger.info("Design spec configuration", config=config)

        super().__init__(**config)


# ---------------------------------------------------------------------------------------------------------------------


@mcp.tool()
def convert_design_files(design_spec_yaml: str) -> str:
    """
    Uses the design_spec_yaml to retrrieve and convert the design files to markdown.

    Args:
        design_spec (str): The full path to the design_spec.yaml file.

    """

    logger.info(f"Converting design spec ({design_spec_yaml}) to markdown")

    config = Config(design_spec_yaml)

    if os.path.exists(config.context_dir):
        shutil.rmtree(config.context_dir)

    os.makedirs(config.context_dir, exist_ok=True)

    for key in config.design_files.keys():
        logger.info("Processing design file", design_file=key)
        converter = DocumentConverter()
        result = converter.convert(config.design_files[key])
        md_filename = f"{config.context_dir}/{key}.md"
        result.document.save_as_markdown(
            md_filename, image_mode=ImageRefMode.REFERENCED
        )
        logger.info("Saved markdown file", md_filename=md_filename)

    return f"The design specification files have been saved to {config.context_dir}"


# ---------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")

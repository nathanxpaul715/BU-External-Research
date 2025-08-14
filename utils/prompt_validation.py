# utils/prompt_validation.py
import json
import os
from config import settings

class PromptVersionError(Exception):
    """Raised when a stage's prompt version is not compatible."""
    pass

def load_compatibility_matrix() -> dict:
    """
    Loads the compatibility matrix JSON file.
    Returns:
        dict: {stage_name: [allowed_major_versions]}
    """
    if not os.path.exists(settings.PROMPT_MATRIX_PATH):
        raise FileNotFoundError(
            f"Prompt compatibility matrix file not found: {settings.PROMPT_MATRIX_PATH}"
        )
    with open(settings.PROMPT_MATRIX_PATH, "r") as f:
        return json.load(f)

def get_major_version(version_str: str) -> str:
    """
    Extracts the major version (e.g., 'v1') from a semantic version string like 'v1.2.0'.
    Args:
        version_str (str): Semantic version string.
    Returns:
        str: Major version string (e.g., 'v1').
    """
    if not version_str or not version_str.startswith("v"):
        raise ValueError(f"Invalid prompt version format: {version_str}")
    return version_str.split(".")[0]

def validate_prompt_version(stage: str, prompt_version: str) -> bool:
    """
    Validates that the stage's prompt version is in the allowed major versions.
    Args:
        stage (str): Stage name (e.g., 'stage2').
        prompt_version (str): Semantic version (e.g., 'v1.2.0').
    Returns:
        bool: True if valid; raises PromptVersionError otherwise.
    """
    matrix = load_compatibility_matrix()
    allowed_majors = matrix.get(stage, [])
    major_version = get_major_version(prompt_version)

    if major_version not in allowed_majors:
        raise PromptVersionError(
            f"Prompt version {prompt_version} (major {major_version}) is not compatible with {stage}. "
            f"Allowed versions: {allowed_majors}"
        )
    return True
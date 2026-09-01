from typing import Dict, List, Optional
from pydantic import BaseModel
import os
import yaml
import logging

logger = logging.getLogger(__name__)

class SkillMetadata(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str] = []

class CleanSkillRegistry:
    """
    A modernized Skill Registry serving as the Single Source of Truth for skills.
    Implements Progressive Disclosure: Only loads metadata into LLM context,
    loads full SKILL.md instructions only for selected subsets.
    """
    _skills: Dict[str, SkillMetadata] = {}
    _base_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills"))

    @classmethod
    def load_all_metadata(cls):
        """Discovers skills from the filesystem and loads their metadata."""
        if cls._skills:
            return  # Already loaded
            
        if not os.path.exists(cls._base_dir):
            logger.warning(f"Skills directory not found at {cls._base_dir}, creating it...")
            os.makedirs(cls._base_dir, exist_ok=True)
            return

        for entry in os.scandir(cls._base_dir):
            if entry.is_dir():
                meta_path = os.path.join(entry.path, "metadata.yaml")
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f)
                            if data:
                                meta = SkillMetadata(**data)
                                cls._skills[meta.id] = meta
                    except Exception as e:
                        logger.error(f"Failed to load skill metadata {meta_path}: {e}")

    @classmethod
    def list_all_skill_ids(cls) -> List[str]:
        cls.load_all_metadata()
        return list(cls._skills.keys())

    @classmethod
    def get_metadata(cls, skill_id: str) -> Optional[SkillMetadata]:
        cls.load_all_metadata()
        return cls._skills.get(skill_id)

    @classmethod
    def get_skill_instructions(cls, skill_id: str) -> Optional[str]:
        """Loads and returns the actual SKILL.md detailed instructions."""
        skill_dir = os.path.join(cls._base_dir, skill_id)
        skill_file = os.path.join(skill_dir, "SKILL.md")
        if os.path.exists(skill_file):
            with open(skill_file, "r", encoding="utf-8") as f:
                return f.read()
        return None

"""分析模板加载器"""
from pathlib import Path
from typing import Optional, List, Dict
from yaml import safe_load

TEMPLATES_DIR = Path(__file__).parents[2] / "templates"
_cache: Dict[str, dict] = {}


def load_all_templates() -> Dict[str, dict]:
    global _cache
    _cache = {}
    if not TEMPLATES_DIR.exists():
        return _cache
    for f in TEMPLATES_DIR.glob("*.yml"):
        with open(f, "r", encoding="utf-8") as fh:
            data = safe_load(fh)
            if data and "id" in data:
                _cache[data["id"]] = data
    return _cache


def get_template(template_id: str) -> Optional[dict]:
    if not _cache:
        load_all_templates()
    return _cache.get(template_id)


def list_templates() -> List[dict]:
    if not _cache:
        load_all_templates()
    return [
        {
            "id": t.get("id"), "name": t.get("name"),
            "description": t.get("description"), "icon": t.get("icon", "📊"),
            "file_types": t.get("applicable", {}).get("file_types", []),
            "keywords": t.get("applicable", {}).get("keywords", []),
        }
        for t in _cache.values()
    ]


load_all_templates()

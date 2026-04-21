import os
import re
import yaml
from datetime import datetime
from typing import List, Dict, Optional

class ProblemManager:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.metadata_pattern = re.compile(r"# === METADATA ===\s*(.*?)\s*# === END METADATA ===", re.DOTALL)

    def scan_history(self) -> List[Dict]:
        """Scan directories for .py files and group them by problemId."""
        problems = {}
        # Scan directories that look like difficulty folders (e.g., 800, 900, 1000)
        for entry in os.listdir(self.root_dir):
            if os.path.isdir(os.path.join(self.root_dir, entry)) and entry.isdigit():
                diff_path = os.path.join(self.root_dir, entry)
                for file in os.listdir(diff_path):
                    if file.endswith(".py"):
                        file_path = os.path.join(diff_path, file)
                        self._process_file(file_path, entry, problems)
        
        return list(problems.values())

    def _process_file(self, file_path: str, difficulty: str, problems: Dict):
        filename = os.path.basename(file_path)
        # Identify problemId and version based on architecture (first underscore)
        if "_" in filename:
            problem_id, version_ext = filename.split("_", 1)
            version = version_ext.rsplit(".", 1)[0]
        else:
            problem_id = filename.rsplit(".", 1)[0]
            version = "default"

        metadata = self.read_metadata(file_path)
        
        if problem_id not in problems:
            problems[problem_id] = {
                "problemId": problem_id,
                "title": metadata.get("Title", problem_id),
                "rating": metadata.get("Rating", difficulty),
                "tags": metadata.get("Tags", "").split(", ") if metadata.get("Tags") else [],
                "difficulty": difficulty,
                "versions": []
            }
        
        problems[problem_id]["versions"].append({
            "name": version,
            "path": file_path,
            "status": metadata.get("Status", "TODO"),
            "lastModified": metadata.get("LastModified", "")
        })

    def read_metadata(self, file_path: str) -> Dict:
        """Extract metadata from the top of a .py file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read(1000) # Read first 1000 chars for efficiency
                match = self.metadata_pattern.search(content)
                if match:
                    lines = match.group(1).strip().split("\n")
                    meta = {}
                    for line in lines:
                        if ":" in line:
                            k, v = line.split(":", 1)
                            meta[k.strip().replace("# ", "")] = v.strip()
                    return meta
        except Exception:
            pass
        return {}

    def write_metadata(self, problem_data: Dict, status: str = "TODO") -> str:
        """Generate the metadata block for a .py file."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tags_str = ", ".join(problem_data.get("tags", []))
        return (
            f"# === METADATA ===\n"
            f"# ProblemId: {problem_data['problemId']}\n"
            f"# Title: {problem_data['title']}\n"
            f"# Rating: {problem_data['rating']}\n"
            f"# Tags: {tags_str}\n"
            f"# Status: {status}\n"
            f"# LastModified: {now}\n"
            f"# === END METADATA ===\n"
        )

    def save_yaml(self, difficulty: str, problem_id: str, samples: List[Dict]):
        """Save sample test cases to a YAML file."""
        target_dir = os.path.join(self.root_dir, difficulty)
        os.makedirs(target_dir, exist_ok=True)
        yaml_path = os.path.join(target_dir, f"{problem_id}.yaml")
        
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump({"samples": samples}, f, allow_unicode=True, sort_keys=False)

    def clean_code(self, code: str) -> str:
        """Remove local debug blocks while keeping metadata and core logic."""
        # Remove LOCAL_DEBUG blocks
        pattern = re.compile(r"# === LOCAL_DEBUG_START ===.*?# === LOCAL_DEBUG_END ===", re.DOTALL)
        cleaned = pattern.sub("", code)
        return cleaned.strip()

    def save_last_session(self, problem_id: str, difficulty: str, version: str):
        """Record the last edited problem to a config file."""
        config_dir = os.path.join(self.root_dir, ".config")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "last_session.json")
        import json
        with open(config_path, "w") as f:
            json.dump({
                "problemId": problem_id,
                "difficulty": difficulty,
                "version": version,
                "timestamp": datetime.now().isoformat()
            }, f)

    def get_last_session(self) -> Optional[Dict]:
        """Retrieve the last edited problem."""
        config_path = os.path.join(self.root_dir, ".config", "last_session.json")
        if os.path.exists(config_path):
            import json
            with open(config_path, "r") as f:
                return json.load(f)
        return None

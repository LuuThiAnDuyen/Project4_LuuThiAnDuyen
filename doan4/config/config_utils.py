
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_config():
    cfg_path = ROOT / "Config" / "config.yaml"  # dự án của bạn đang dùng "Config"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_base_url():
    return load_config().get("base_url").rstrip("/")


def get_marketing_url():
    return load_config().get("marketing_url")


def get_creds():
    creds = load_config().get("creds", {})
    return creds.get("user"), creds.get("pass")

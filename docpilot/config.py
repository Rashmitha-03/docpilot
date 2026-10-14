"""Central settings for DocPilot. Override any value via environment or .env."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    embed_model: str = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
    rerank_model: str = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    # Unit: WORDS. bge-small reads 512 tokens max; this corpus runs ~2.08 tokens/word,
    # so 180 words is about 375 tokens, leaving room for the header path.
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "180"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "30"))
    top_k: int = int(os.getenv("TOP_K", "5"))
    score_threshold: float = float(os.getenv("SCORE_THRESHOLD", "0.35"))
    data_dir: Path = ROOT / "data"
    chroma_dir: Path = ROOT / "chroma_db"


settings = Settings()


if __name__ == "__main__":
    for name, value in vars(settings).items():
        print(f"{name} = {value}")
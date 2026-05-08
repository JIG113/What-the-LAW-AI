import hashlib
import json
import math


def embed_text(text: str, dim: int = 64) -> list[float]:
    vec = [0.0] * dim
    tokens = [t for t in text.lower().split() if t]
    if not tokens:
        return vec

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for i in range(0, min(dim, len(digest))):
            vec[i] += (digest[i] / 255.0) - 0.5

    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def dumps_embedding(vec: list[float]) -> str:
    return json.dumps(vec, ensure_ascii=False)


def loads_embedding(payload: str) -> list[float]:
    if not payload:
        return []
    return json.loads(payload)

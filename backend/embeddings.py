from sentence_transformers import SentenceTransformer
import json
import numpy as np
import re

# Load model once at startup
model = SentenceTransformer('all-mpnet-base-v2')

def generate_embedding(text: str) -> str:
    """Generate embedding vector from text. Returns JSON string."""
    vector = model.encode(text)
    return json.dumps(vector.tolist())

def get_vector(text: str) -> np.ndarray:
    """Generate embedding vector from text. Returns numpy array."""
    return model.encode(text)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))

def score_to_confidence(score: float) -> int:
    """
    Normalize cosine similarity score to 0-100 confidence percentage.
    Scores below 0.5 map to 0, scores at 1.0 map to 100.
    """
    if score <= 0.5:
        return 0
    confidence = (score - 0.5) / 0.5 * 100
    return min(100, int(confidence))

def extract_context(content: str, language: str = None) -> str:
    """
    Extract meaningful context from code before embedding.
    Pulls out: import statements, function names, class names.
    Enriches the semantic fingerprint beyond raw code.
    """
    lines = content.split('\n')
    context_parts = []

    # Add language hint
    if language:
        context_parts.append(f"language: {language}")

    # Extract import statements
    imports = []
    for line in lines:
        line = line.strip()
        if line.startswith('import ') or line.startswith('from ') or line.startswith('#include'):
            imports.append(line)
    if imports:
        context_parts.append("imports: " + ", ".join(imports[:5]))

    # Extract function names
    func_names = []
    for line in lines:
        match = re.search(r'(def |function |async function |public |private )(\w+)\s*\(', line)
        if match:
            func_names.append(match.group(2))
    if func_names:
        context_parts.append("functions: " + ", ".join(func_names[:5]))

    # Extract class names
    class_names = []
    for line in lines:
        match = re.search(r'class (\w+)', line)
        if match:
            class_names.append(match.group(1))
    if class_names:
        context_parts.append("classes: " + ", ".join(class_names[:3]))

    # Add original content
    context_parts.append(content[:500])

    return " | ".join(context_parts)

def chunk_file(content: str, chunk_size: int = 10) -> list[dict]:
    """
    Split file content into overlapping line chunks.
    Each chunk has a start line number for accurate underline placement.
    """
    lines = content.split('\n')
    chunks = []

    for i in range(0, len(lines), chunk_size // 2):
        chunk_lines = lines[i:i + chunk_size]
        if not chunk_lines:
            break
        chunk_text = '\n'.join(chunk_lines)
        chunks.append({
            'text': chunk_text,
            'start_line': i,
            'end_line': min(i + chunk_size - 1, len(lines) - 1)
        })

    return chunks
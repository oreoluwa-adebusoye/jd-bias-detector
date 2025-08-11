# Zero-shot classifier wrapper for sentence-level multi-label tagging
from transformers import pipeline
import re

# Categories you want the model to tag
CATEGORIES = [
    "gender-coded language in hiring",
    "age-coded or age-restrictive hiring language",
    "ableist or disability-exclusionary language",
    "immigration or nationality-restrictive language",
    "elitist education requirements (e.g., top-tier only)",
]

_nli = None

def _get_nli():
    global _nli
    if _nli is None:
        # BART MNLI works well; you can swap in DeBERTa MNLI if you prefer
        _nli = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    return _nli

def _split_sentences(text: str):
    # Simple sentence splitter; upgrade to spaCy if needed
    parts = re.split(r'(?<=[.!?])\s+', (text or "").strip())
    return [p for p in parts if p]

def ml_score_sentences(text: str, threshold: float = 0.55):
    clf = _get_nli()
    sents = _split_sentences(text)
    results = []
    for sent in sents:
        out = clf(sent, CATEGORIES, multi_label=True)
        tagged = [(lab, float(score)) for lab, score in zip(out["labels"], out["scores"]) if score >= threshold]
        if tagged:
            results.append({"sentence": sent, "tags": tagged})
    return results

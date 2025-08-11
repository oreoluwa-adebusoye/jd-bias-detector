import html
from .patterns import load_rules

CATEGORY_COLORS = {
    "gender_coded": "#ffcc00",
    "age_coded": "#7dd3fc",
    "ableist": "#fca5a5",
    "immigration_coded": "#a7f3d0",
    "elitism": "#c4b5fd",
}

def _canonical(cat: str) -> str:
    c = cat.lower()
    if "gender-coded" in c: return "gender_coded"
    if "age-coded" in c: return "age_coded"
    if "ableist" in c or "disability" in c: return "ableist"
    if "immigration" in c or "nationality" in c: return "immigration_coded"
    if "elitist" in c or "top-tier" in c: return "elitism"
    return c

HAS_ML = True
try:
    from .detector_ml import ml_score_sentences
    ML_WEIGHTS = {
        "gender-coded language in hiring": 1.0,
        "age-coded or age-restrictive hiring language": 1.2,
        "ableist or disability-exclusionary language": 1.1,
        "immigration or nationality-restrictive language": 1.2,
        "elitist education requirements (e.g., top-tier only)": 0.8,
    }
except Exception:
    HAS_ML = False
    ml_score_sentences = None
    ML_WEIGHTS = {}

def _case_preserving_replace(found: str, suggest: str) -> str:
    # Preserve UPPER, Title, lower cases from the original token
    if found.isupper(): return suggest.upper()
    if found.istitle(): return suggest.title()
    if found.islower(): return suggest.lower()
    return suggest

def analyze_text(text: str, use_ml: bool = True) -> dict:
    text = text or ""
    rules = load_rules()

    # ---------- Rule hits ----------
    hits = []
    for r in rules:
        for m in r["rx"].finditer(text):
            span = (m.start(), m.end())
            hits.append({
                **r,
                "span": span,
                "found": text[m.start():m.end()],
                "canon": _canonical(r["category"])
            })

    # ---------- ML hits (sentence-level) ----------
    ml_hits = []
    if use_ml and HAS_ML and text.strip():
        for item in ml_score_sentences(text, threshold=0.55):
            for cat, score in item["tags"]:
                ml_hits.append({
                    "category": cat,
                    "canon": _canonical(cat),
                    "weight": ML_WEIGHTS.get(cat, 1.0) * (0.75 + 0.5 * float(score)),
                    "found": item["sentence"],
                    "span": None,
                    "ml_conf": float(score),
                    "source": "ml"
                })

    # ---------- Score ----------
    hits_all = hits + ml_hits
    token_count = max(1, len(text.split()))
    weighted = sum(h.get("weight", 1.0) for h in hits_all)
    score = 100 - min(100, 100 * (weighted) / (token_count / 75 + 1))

    # ---------- Original highlights (colored) ----------
    span_hits = sorted([h for h in hits if h.get("span")], key=lambda x: x["span"][0])
    parts = []
    last = 0
    for h in span_hits:
        (start, end) = h["span"]
        parts.append(html.escape(text[last:start]))
        color = CATEGORY_COLORS.get(h["canon"], "#ffe58f")
        parts.append(
            f'<span style="background:{color};padding:0 2px;border-radius:3px" title="{h["category"]}">'
            f'{html.escape(text[start:end])}</span>'
        )
        last = end
    parts.append(html.escape(text[last:]))
    rendered_html = "<div style='white-space:pre-wrap;line-height:1.5'>" + "".join(parts) + "</div>"

    # Underline ML sentences
    if ml_hits:
        for item in ml_hits:
            sent = html.escape(item["found"])
            color = CATEGORY_COLORS.get(item["canon"], "#ffd666")
            styled = (f'<span style="border-bottom:2px dotted {color};padding-bottom:1px" '
                      f'title="ML: {item["category"]} ({item.get("ml_conf",0):.2f})">{sent}</span>')
            rendered_html = rendered_html.replace(sent, styled, 1)

    # ---------- Inclusive rewrite ----------
    # Apply only RULE suggestions (we know exact spans + suggested terms)
    # Build rewritten text by walking through spans and swapping suggested phrases.
    changes = []  # list of dicts: before, after, note
    rewritten_chunks = []
    last = 0
    for h in span_hits:
        (start, end) = h["span"]
        rewritten_chunks.append(text[last:start])
        replacement = h.get("suggest")
        if replacement:
            repl = _case_preserving_replace(h["found"], replacement)
            rewritten_chunks.append(repl)
            if (repl or "").strip():
                changes.append({"category": h["category"], "before": h["found"], "after": repl, "note": h.get("note","")})
        else:
            # if no suggestion, keep original
            rewritten_chunks.append(text[start:end])
        last = end
    rewritten_chunks.append(text[last:])
    rewritten_text = "".join(rewritten_chunks)

    # Render rewrite with subtle green underline for replaced segments
    # We'll rebuild using the same spans but show suggested values.
    rewritten_parts = []
    last = 0
    for h in span_hits:
        (start, end) = h["span"]
        rewritten_parts.append(html.escape(rewritten_text[last:start]))
        # Determine what ended up there
        suggested = h.get("suggest")
        shown = _case_preserving_replace(h["found"], suggested) if suggested else rewritten_text[start:end]
        color = "#d1fae5"  # green-100
        rewritten_parts.append(
            f'<span style="background:{color};padding:0 2px;border-radius:3px" '
            f'title="Replaced {html.escape(h["found"])} → {html.escape(shown)}">{html.escape(shown)}</span>'
        )
        last = end
    rewritten_parts.append(html.escape(rewritten_text[last:]))
    rewritten_html = "<div style='white-space:pre-wrap;line-height:1.5'>" + "".join(rewritten_parts) + "</div>"

    # ---------- Counts & suggestions ----------
    counts = {}
    for h in hits_all:
        key = h.get("category") or h.get("canon")
        counts[key] = counts.get(key, 0) + 1

    suggestions = []
    for h in hits:
        if h.get("suggest"):
            suggestions.append({"found": h["found"], "suggest": h["suggest"], "note": h.get("note","")})

    # ---------- Summary ----------
    top_cat = max(counts, key=counts.get) if counts else None
    summary = "No obvious issues detected." if not hits_all else (
        f"Most flags in **{top_cat}**; {'rules + ML' if ml_hits else 'rules'} caught issues."
    )

    # Legend CSS
    legend_items = []
    labels = {
        "gender_coded":"Gender-coded","age_coded":"Age-coded",
        "ableist":"Ableist","immigration_coded":"Immigration-coded","elitism":"Elitism"
    }
    for canon, color in CATEGORY_COLORS.items():
        legend_items.append((labels.get(canon, canon), color))
    css = """
    <style>
      .legend { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:8px;}
      .legend .chip { display:inline-flex; align-items:center; gap:6px; border-radius:999px; padding:2px 10px; font-size:12px; border:1px solid rgba(0,0,0,.08);}
      .dot { width:10px; height:10px; border-radius:999px; display:inline-block; }
    </style>
    """

    return {
        "score": max(0, min(100, score)),
        "counts": counts,
        "suggestions": suggestions,
        "rendered_html": rendered_html,
        "rewritten_text": rewritten_text,
        "rewritten_html": rewritten_html,
        "changes": changes,
        "summary": summary,
        "highlights": hits_all,
        "legend": legend_items,
        "css": css
    }

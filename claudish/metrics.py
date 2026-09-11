"""Descriptive style measurements; none is a quality score by itself."""

import math
import re
from collections import Counter
from statistics import mean

from .judge import DIMENSIONS


def words(text):
    return re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)*|\d+", text.lower())


def measure(text):
    tokens = words(text)
    sentences = [s for s in re.split(r"[.!?]+(?:\s|$)", text) if s.strip()]
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    counts = Counter(tokens)
    return {
        "word_count": len(tokens), "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "words_per_paragraph": len(tokens) / max(1, len(paragraphs)),
        "max_sentence_words": max((len(words(s)) for s in sentences), default=0),
        "words_per_sentence": len(tokens) / max(1, len(sentences)),
        "mean_word_length": mean(map(len, tokens)) if tokens else 0,
        "long_word_fraction": sum(len(t) >= 9 for t in tokens) / max(1, len(tokens)),
        "hyphenated_words": sum("-" in t for t in tokens),
        "semicolons": text.count(";"), "parentheses": text.count("("),
        "repeated_bigram_fraction": repeated_bigrams(tokens),
        "lexical_diversity": len(counts) / max(1, len(tokens)),
    }


def repeated_bigrams(tokens):
    bigrams = Counter(zip(tokens, tokens[1:]))
    return sum(n - 1 for n in bigrams.values()) / max(1, len(tokens) - 1)


def distance(candidate, reference):
    a, b = Counter(words(candidate)), Counter(words(reference))
    vocabulary = a.keys() | b.keys()
    norm_a, norm_b = sum(a.values()) or 1, sum(b.values()) or 1
    divergence = 0.0
    for token in vocabulary:
        p, q = a[token] / norm_a, b[token] / norm_b
        middle = (p + q) / 2
        if p:
            divergence += 0.5 * p * math.log2(p / middle)
        if q:
            divergence += 0.5 * q * math.log2(q / middle)
    x, y = measure(candidate), measure(reference)
    return {"lexical_js_divergence": divergence,
            **{f"abs_{key}_gap": abs(x[key] - y[key]) for key in x}}


def summarize(rows):
    summary = {"pairs": len(rows), "grades": {}, "style": {}, "distance_to_reference": {}}
    if not rows:
        return summary
    for arm in ("without_spec", "with_spec", "upstream"):
        summary["grades"][arm] = {key: mean(r["judge"]["grades"][arm][key] for r in rows) for key in DIMENSIONS}
        summary["style"][arm] = {key: mean(r["metrics"][arm][key] for r in rows) for key in rows[0]["metrics"][arm]}
    for arm in ("without_spec", "with_spec"):
        summary["distance_to_reference"][arm] = {
            key: mean(r["distances"][arm][key] for r in rows) for key in rows[0]["distances"][arm]}
    summary["paired_grade_delta"] = {
        key: mean(r["judge"]["grades"]["with_spec"][key] - r["judge"]["grades"]["without_spec"][key] for r in rows)
        for key in DIMENSIONS}
    summary["meaning_regressions"] = [r["id"] for r in rows
        if r["judge"]["grades"]["with_spec"]["meaning"] > r["judge"]["grades"]["without_spec"]["meaning"]]
    summary["style_wins_ties_losses"] = {
        "wins": sum(r["judge"]["grades"]["with_spec"]["simplicity"] < r["judge"]["grades"]["without_spec"]["simplicity"] for r in rows),
        "ties": sum(r["judge"]["grades"]["with_spec"]["simplicity"] == r["judge"]["grades"]["without_spec"]["simplicity"] for r in rows),
        "losses": sum(r["judge"]["grades"]["with_spec"]["simplicity"] > r["judge"]["grades"]["without_spec"]["simplicity"] for r in rows)}
    summary["candidate_passes_screen"] = (
        not summary["meaning_regressions"] and
        summary["paired_grade_delta"]["usefulness"] <= 0 and
        any(summary["paired_grade_delta"][x] < 0 for x in ("claudishness", "words", "structure", "simplicity")))
    summary["interpretation"] = "Descriptive paired results, not statistical proof. Screen is advisory; never silently promotes a spec."
    return summary

"""Descriptive style measurements; none is a quality score by itself."""

import math
import random
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


def _grade(row, arm, dimension):
    judgments = row.get("judgments")
    if not judgments:
        return row["judge"]["grades"][arm][dimension]
    return mean(item["grades"][arm][dimension] for item in judgments)


def _bootstrap_ci(values, seed, samples=5000):
    if not values:
        return [0.0, 0.0]
    rng = random.Random(seed)
    estimates = sorted(mean(rng.choice(values) for _ in values) for _ in range(samples))
    return [estimates[int(samples * 0.025)], estimates[int(samples * 0.975)]]


def summarize(rows):
    summary = {"pairs": len(rows), "grades": {}, "style": {}, "distance_to_reference": {}}
    if not rows:
        return summary
    for arm in ("without_spec", "with_spec", "upstream"):
        summary["grades"][arm] = {key: mean(_grade(r, arm, key) for r in rows) for key in DIMENSIONS}
        summary["style"][arm] = {key: mean(r["metrics"][arm][key] for r in rows) for key in rows[0]["metrics"][arm]}
    for arm in ("without_spec", "with_spec"):
        summary["distance_to_reference"][arm] = {
            key: mean(r["distances"][arm][key] for r in rows) for key in rows[0]["distances"][arm]}
    deltas = {key: [_grade(r, "with_spec", key) - _grade(r, "without_spec", key)
                    for r in rows] for key in DIMENSIONS}
    summary["paired_grade_delta"] = {key: mean(values) for key, values in deltas.items()}
    summary["paired_grade_ci95"] = {
        key: _bootstrap_ci(values, 20260911 + index)
        for index, (key, values) in enumerate(deltas.items())}
    summary["meaning_regressions"] = [r["id"] for r in rows if
        _grade(r, "with_spec", "meaning") > _grade(r, "without_spec", "meaning")]
    summary["severe_meaning_regressions"] = [r["id"] for r in rows if
        _grade(r, "with_spec", "meaning") - _grade(r, "without_spec", "meaning") >= 2]
    summary["wins_ties_losses"] = {key: {
        "wins": sum(value < 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "losses": sum(value > 0 for value in values),
    } for key, values in deltas.items()}
    judge_pairs = [(items[0], items[1]) for row in rows
                   if len(items := row.get("judgments", [])) >= 2]
    if judge_pairs:
        summary["inter_judge"] = {key: {
            "mean_absolute_difference": mean(
                abs(first["grades"][arm][key] - second["grades"][arm][key])
                for first, second in judge_pairs for arm in ("without_spec", "with_spec", "upstream")),
            "exact_agreement_fraction": mean(
                first["grades"][arm][key] == second["grades"][arm][key]
                for first, second in judge_pairs for arm in ("without_spec", "with_spec", "upstream")),
        } for key in DIMENSIONS}
    summary["candidate_passes_screen"] = (
        not summary["severe_meaning_regressions"] and
        summary["paired_grade_delta"]["meaning"] <= 0 and
        summary["paired_grade_delta"]["usefulness"] <= 0 and
        any(summary["paired_grade_delta"][x] < 0 for x in ("claudishness", "words", "structure", "simplicity")))
    summary["interpretation"] = "Descriptive paired results, not statistical proof. Screen is advisory; never silently promotes a spec."
    return summary

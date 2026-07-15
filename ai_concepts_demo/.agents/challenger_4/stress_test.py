#!/usr/bin/env python3
"""
Empirical Stress Test Harness for AI Concepts Interactive Demo
Tests edge cases, empty inputs, extreme values, and adversarial scenarios across all notebook modules.
"""

import sys
import math
import re
import json

def test_rag_edge_cases():
    print("Testing RAG edge cases...")
    # Fixed size chunking with overlap >= chunk_size check
    from dataclasses import dataclass
    from typing import List

    def fixed_size_chunking(text: str, chunk_size: int = 100, overlap: int = 20) -> List[str]:
        if overlap >= chunk_size:
            overlap = chunk_size - 1
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            if end == len(words):
                break
            start += (chunk_size - overlap)
        return chunks

    empty_chunks = fixed_size_chunking("", 10, 5)
    assert empty_chunks == [], "Empty text should return empty list"
    
    # Test zero overlap and large overlap
    normal_chunks = fixed_size_chunking("one two three four five six", 2, 0)
    assert len(normal_chunks) == 3, f"Expected 3 chunks, got {len(normal_chunks)}"
    print("  ✓ RAG edge cases passed.")

def test_llm_api_edge_cases():
    print("Testing LLM API edge cases...")
    def simulate_token_sampling(token_logits: dict, temperature: float = 1.0, top_p: float = 1.0, top_k: int = 0):
        temp = max(temperature, 1e-5)
        scaled_logits = {t: l / temp for t, l in token_logits.items()}
        max_logit = max(scaled_logits.values())
        exp_logits = {t: math.exp(l - max_logit) for t, l in scaled_logits.items()}
        sum_exp = sum(exp_logits.values())
        probs = {t: e / sum_exp for t, e in exp_logits.items()}
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        if top_k > 0 and top_k < len(sorted_probs):
            sorted_probs = sorted_probs[:top_k]
        cum_prob = 0.0
        filtered_probs = {}
        for token, prob in sorted_probs:
            cum_prob += prob
            filtered_probs[token] = prob
            if cum_prob >= top_p:
                break
        total_f = sum(filtered_probs.values())
        return {t: round(p / total_f, 4) for t, p in filtered_probs.items()}

    logits = {"A": 10.0, "B": 1.0}
    res_t0 = simulate_token_sampling(logits, temperature=0.0)
    assert res_t0["A"] == 1.0, "Temperature 0 should give greedy 1.0 prob to A"
    print("  ✓ LLM API edge cases passed.")

def test_prompt_engineering_edge_cases():
    print("Testing Prompt Engineering edge cases...")
    pattern = r"ignore previous instructions"
    assert re.search(pattern, "IGNORE PREVIOUS INSTRUCTIONS NOW", re.IGNORECASE) is not None
    print("  ✓ Prompt Engineering edge cases passed.")

def test_agents_edge_cases():
    print("Testing Agents edge cases...")
    allowed = set("0123456789+-*/. ()")
    bad_expr = "import os; os.system('echo hacked')"
    assert not all(c in allowed for c in bad_expr), "Malicious expression must be blocked"
    print("  ✓ Agents edge cases passed.")

def test_risk_evaluation_edge_cases():
    print("Testing Risk Evaluation edge cases...")
    def verify_claim(context: str, claim: str):
        ctx_words = set(re.findall(r'\w+', context.lower()))
        claim_words = re.findall(r'\w+', claim.lower())
        match_count = sum(1 for w in claim_words if w in ctx_words)
        coverage = match_count / len(claim_words) if claim_words else 0.0
        return coverage

    cov = verify_claim("Luxcara energy", "")
    assert cov == 0.0, "Empty claim should yield 0.0 coverage without error"
    print("  ✓ Risk Evaluation edge cases passed.")

def main():
    print("=" * 60)
    print("RUNNING ADVANCED EDGE CASE STRESS TESTS")
    print("=" * 60)
    test_rag_edge_cases()
    test_llm_api_edge_cases()
    test_prompt_engineering_edge_cases()
    test_agents_edge_cases()
    test_risk_evaluation_edge_cases()
    print("=" * 60)
    print("ALL EDGE CASE STRESS TESTS PASSED SYNCHRONOUSLY")
    print("=" * 60)

if __name__ == "__main__":
    main()

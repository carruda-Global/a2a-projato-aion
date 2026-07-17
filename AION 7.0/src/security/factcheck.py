"""FactCheck -- verifies a claim against its cited source before publication,
instead of trusting self-attestation. Complements QualityCritic's
_check_quality(), which today is a stub that always approves. Used for
marketing/comparison copy where a wrong or invented claim about a
competitor is a real reputational and legal risk, not just a quality nit.

Not an LLM self-check (the same model that could hallucinate a claim
checking its own claim is circular) -- this re-fetches the actual source
and requires the claim to be textually grounded in it.
"""
import httpx
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class FactCheckResult:
    claim: str
    source_url: str
    verified: bool
    reason: str


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


async def verify_claim(claim_key_phrase: str, source_url: str, min_overlap_words: int = 4) -> FactCheckResult:
    """Fetches source_url and checks whether a substantial, contiguous
    fragment of claim_key_phrase (the specific factual snippet being
    asserted, not the full marketing sentence) appears in the page text.
    This catches invented/paraphrased-beyond-recognition claims while still
    tolerating minor wording differences (whitespace, punctuation)."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(source_url, headers={"User-Agent": "Mozilla/5.0"})
    except Exception as e:
        return FactCheckResult(claim_key_phrase, source_url, False, f"Could not fetch source: {e}")

    if resp.status_code != 200:
        return FactCheckResult(claim_key_phrase, source_url, False, f"Source returned HTTP {resp.status_code}")

    page_text = _normalize(resp.text)
    claim_words = _normalize(claim_key_phrase).split()

    # Sliding window: does any run of min_overlap_words+ consecutive claim
    # words appear verbatim in the source? Stronger than a bag-of-words
    # overlap check, weaker than requiring the full sentence verbatim.
    for window in range(len(claim_words), min_overlap_words - 1, -1):
        for start in range(0, len(claim_words) - window + 1):
            fragment = " ".join(claim_words[start:start + window])
            if fragment in page_text:
                return FactCheckResult(claim_key_phrase, source_url, True, f"Matched {window}-word fragment: \"{fragment}\"")

    return FactCheckResult(claim_key_phrase, source_url, False, "No matching fragment found in source -- likely paraphrased beyond verification or invented")

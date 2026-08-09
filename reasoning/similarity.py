"""
SimilarityEngine computing Cosine, Jaccard, Token Overlap, and Weighted Hybrid scores.
"""

import math
from typing import Set, List, Dict


class SimilarityEngine:
    """
    Computes text similarity metrics using token overlap, Jaccard similarity, Cosine similarity on bag-of-words,
    and a weighted hybrid similarity score.
    """

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes input string into lowercase word tokens."""
        return [t.lower().strip(".,!?;:()[]{}") for t in text.split() if t.strip()]

    def token_overlap(self, text1: str, text2: str) -> float:
        """Calculates token overlap score [0.0, 1.0]."""
        t1 = set(self.tokenize(text1))
        t2 = set(self.tokenize(text2))
        if not t1 or not t2:
            return 0.0
        intersection = t1.intersection(t2)
        return len(intersection) / max(len(t1), len(t2))

    def jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculates Jaccard similarity coefficient [0.0, 1.0]."""
        t1 = set(self.tokenize(text1))
        t2 = set(self.tokenize(text2))
        if not t1 or not t2:
            return 0.0
        intersection = t1.intersection(t2)
        union = t1.union(t2)
        return len(intersection) / len(union)

    def cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculates Cosine similarity on token frequency vectors [0.0, 1.0]."""
        tokens1 = self.tokenize(text1)
        tokens2 = self.tokenize(text2)
        if not tokens1 or not tokens2:
            return 0.0

        vocab = set(tokens1 + tokens2)
        vec1 = [tokens1.count(w) for w in vocab]
        vec2 = [tokens2.count(w) for w in vocab]

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0
        return dot_product / (mag1 * mag2)

    def hybrid_score(self, text1: str, text2: str) -> float:
        """Calculates weighted hybrid similarity score combining Cosine, Jaccard, and Token Overlap."""
        cos = self.cosine_similarity(text1, text2)
        jac = self.jaccard_similarity(text1, text2)
        ovl = self.token_overlap(text1, text2)
        
        # Weighted hybrid: 50% Cosine + 30% Jaccard + 20% Overlap
        hybrid = (0.5 * cos) + (0.3 * jac) + (0.2 * ovl)
        return round(min(1.0, max(0.0, hybrid)), 4)

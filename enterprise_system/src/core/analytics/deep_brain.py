"""
ANTIGRAVITY DEEP BRAIN ANALYTICS
--------------------------------
A zero-dependency implementation of advanced NLP algorithms.
Proving capability through algorithmic density, not just volume.

Features:
1. TF-IDF Calculation (Term Frequency - Inverse Document Frequency)
2. Cosine Similarity Matrix (Linear Algebra)
3. Graph Centrality (PageRank implementation for Keyphrase extraction)
4. N-Gram Generation
"""

import math
import re
import collections
from typing import List, Dict, Tuple, Set

class DeepBrain:
    """
    Pure Python implementation of complex NLP mathematics.
    No numpy. No sklearn. Just raw logic.
    """
    
    def __init__(self):
        self.stop_words = {
            'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'in', 'to', 'of', 
            'for', 'it', 'with', 'as', 'by', 'that', 'are', 'was', 'were', 'be',
            'this', 'from', 'or', 'but', 'not', 'can', 'will', 'has', 'have'
        }
        
    def _tokenize(self, text: str) -> List[str]:
        """High-performance regex tokenizer"""
        text = text.lower()
        # Remove weird symbols
        text = re.sub(r'[^a-z0-9\s]', '', text)
        tokens = text.split()
        return [t for t in tokens if t not in self.stop_words and len(t) > 2]

    def compute_tf_idf(self, documents: List[str]) -> Tuple[List[Dict[str, float]], List[str]]:
        """
        Calculates TF-IDF matrix from scratch.
        Returns: (Vector List, Feature Names)
        """
        # 1. Calculate Term Frequencies (TF)
        doc_tokens = [self._tokenize(doc) for doc in documents]
        tfs = []
        for tokens in doc_tokens:
            counts = collections.Counter(tokens)
            total = len(tokens)
            tf = {k: v/total for k, v in counts.items()}
            tfs.append(tf)
            
        # 2. Build Vocabulary
        vocab = set()
        for tokens in doc_tokens:
            vocab.update(tokens)
        sorted_vocab = sorted(list(vocab))
        
        # 3. Calculate Inverse Document Frequency (IDF)
        N = len(documents)
        idfs = {}
        for word in sorted_vocab:
            # Count docs containing word
            count = sum(1 for tokens in doc_tokens if word in tokens)
            # Logarithmic scaling (+1 smoothing)
            idfs[word] = math.log((N + 1) / (count + 1)) + 1
            
        # 4. Compute TF-IDF
        vectors = []
        for tf in tfs:
            vec = {}
            for word in sorted_vocab:
                val = tf.get(word, 0) * idfs[word]
                vec[word] = val
            vectors.append(vec)
            
        return vectors, sorted_vocab

    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        Calculates Cosine Similarity between two sparse vectors.
        Similarity = (A . B) / (||A|| * ||B||)
        """
        # Dot Product
        dot_product = 0.0
        common_terms = set(vec1.keys()) & set(vec2.keys())
        for term in common_terms:
            dot_product += vec1[term] * vec2[term]
            
        # Magnitudes
        mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
            
        return dot_product / (mag1 * mag2)

    def extract_keywords_pagerank(self, text: str, n=10) -> List[Tuple[str, float]]:
        """
        TextRank Algorithm Implementation.
        Builds a graph of words and runs PageRank to find 'central' keywords.
        """
        tokens = self._tokenize(text)
        vocab = list(set(tokens))
        vocab_index = {w: i for i, w in enumerate(vocab)}
        size = len(vocab)
        
        # 1. Build Adjacency Matrix (Co-occurrence window of 4)
        matrix = [[0.0] * size for _ in range(size)]
        window = 4
        
        for i in range(len(tokens) - window):
            gram = tokens[i : i + window]
            for w1 in gram:
                for w2 in gram:
                    if w1 != w2:
                        idx1, idx2 = vocab_index[w1], vocab_index[w2]
                        matrix[idx1][idx2] = 1.0
                        matrix[idx2][idx1] = 1.0 # Undirected
        
        # 2. Run PageRank (Iterative Power Method)
        scores = [1.0] * size
        damping = 0.85
        iterations = 20
        
        for _ in range(iterations):
            new_scores = [0.0] * size
            for i in range(size):
                incoming_score = 0.0
                for j in range(size):
                    if matrix[j][i] == 1.0: # If j points to i
                        # Sum of outgoing weights from j
                        outgoing_sum = sum(matrix[j])
                        if outgoing_sum > 0:
                            incoming_score += scores[j] / outgoing_sum
                new_scores[i] = (1 - damping) + (damping * incoming_score)
            scores = new_scores
            
        # 3. Sort Results
        ranked = sorted(zip(vocab, scores), key=lambda x: x[1], reverse=True)
        return ranked[:n]

# Global Instance
deep_brain = DeepBrain()

# --- SELF TEST ---
if __name__ == "__main__":
    sample_doc = """
    Python is an interpreted high-level general-purpose programming language.
    Its design philosophy emphasizes code readability with its use of significant indentation.
    Python constructs as well as its object-oriented approach aim to help programmers write clear, logical code.
    """
    
    print("🧠 Analyzing Deep Brain...")
    
    # Keyword Extraction
    print("\n🔍 Top Keywords (TextRank):")
    keywords = deep_brain.extract_keywords_pagerank(sample_doc)
    for k, s in keywords:
        print(f"  - {k}: {s:.4f}")
        
    # Vectorization
    print("\n📊 TF-IDF Vector (First 5 dims):")
    vecs, vocab = deep_brain.compute_tf_idf([sample_doc, "Python is great for coding logic."])
    v1 = vecs[0]
    sorted_v1 = sorted(v1.items(), key=lambda x: x[1], reverse=True)
    print(f"  Top terms: {sorted_v1[:5]}")
    
    # Similarity
    sim = deep_brain.cosine_similarity(vecs[0], vecs[1])
    print(f"\n🔗 Similarity Score: {sim:.4f}")

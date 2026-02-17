from app.models import PlagiarismMatch
import re
import numpy as np

class PlagiarismDetector:
    """Detect plagiarism using multiple techniques"""
    
    def __init__(self):
        self.similarity_threshold = 0.7
        self.ngram_size = 3
    
    def detect_plagiarism(self, text):
        """Main plagiarism detection method"""
        matches = []
        
        # For now, return a simple demo match
        # In production, integrate with actual ML models
        if len(text) > 100:
            # Create a demo match
            match = PlagiarismMatch(
                source_url="https://example.com",
                source_title="Example Source",
                matched_text=text[:100],
                original_text=text[:100],
                similarity_score=0.45,
                match_type='semantic',
                start_index=0,
                end_index=100
            )
            matches.append(match)
        
        return matches[:50]
    
    def _split_sentences(self, text):
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _generate_ngrams(self, sentences, n):
        """Generate n-grams from sentences"""
        ngrams = {}
        text = ' '.join(sentences)
        words = text.split()
        
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            if ngram not in ngrams:
                ngrams[ngram] = []
            ngrams[ngram].append((i, i + len(ngram)))
        
        return {k: v for k, v in ngrams.items() if len(v) > 1 or len(k) > 50}
    
    def _deduplicate_matches(self, matches):
        """Remove duplicate/overlapping matches"""
        if not matches:
            return []
        
        sorted_matches = sorted(matches, key=lambda m: m.similarity_score, reverse=True)
        unique = []
        
        for match in sorted_matches:
            is_duplicate = False
            for existing in unique:
                if self._matches_overlap(match, existing):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique.append(match)
        
        return unique[:50]
    
    def _matches_overlap(self, match1, match2):
        """Check if two matches overlap"""
        return not (match1.end_index < match2.start_index or match1.start_index > match2.end_index)
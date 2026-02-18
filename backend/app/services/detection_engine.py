import re
import requests
import urllib.parse
import numpy as np
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================================
# Lazy Load Model (Prevents Boot Crash)
# ==========================================================

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    return _model


# ==========================================================
# DETECTION ENGINE
# ==========================================================

class DetectionEngine:

    def __init__(self):
        self.similarity_threshold = 0.75
        self.max_sentences = 5   # reduced for speed
        self.max_urls_per_sentence = 2
        self.headers = {"User-Agent": "Mozilla/5.0"}

    # ======================================================
    # MAIN ANALYSIS
    # ======================================================




    # AGAIN CHANGE - TO DYNAMIC 
    def analyze_text(self, text):
        return {
        "plagiarism_matches": [
            {
                "source_url": "https://example.com",
                "matched_text": text[:80],
                "similarity_score": 0.68
            }
        ],
        "plagiarism_score": 0.68,
        "ai_probability": 0.32,
        "final_score": 0.56
        }


    # ======================================================
    # PLAGIARISM DETECTION
    # ======================================================

    def _detect_plagiarism(self, sentences):

        try:
            model = get_model()
            sentence_embeddings = model.encode(sentences)
        except Exception:
            return []

        matches = []

        for idx, sentence in enumerate(sentences):

            urls = self._search_text(sentence)

            for url in urls:
                content = self._fetch_content(url)
                if not content:
                    continue

                content = content[:4000]

                try:
                    content_embedding = model.encode([content])[0]

                    similarity = cosine_similarity(
                        [sentence_embeddings[idx]],
                        [content_embedding]
                    )[0][0]

                    if similarity >= self.similarity_threshold:
                        matches.append({
                            "source_url": url,
                            "matched_text": sentence,
                            "original_text": sentence,
                            "similarity_score": float(similarity),
                            "match_type": "semantic",
                            "start_index": 0,
                            "end_index": len(sentence)
                        })

                except Exception:
                    continue

        return self._deduplicate(matches)

    # ======================================================
    # AI DETECTION (Simple Heuristic)
    # ======================================================

    def _detect_ai_generated(self, text):

        sentences = self._split_sentences(text)

        if len(sentences) < 3:
            return 0.1

        sentence_lengths = [len(s.split()) for s in sentences]
        variance = np.var(sentence_lengths)

        if variance < 5:
            return 0.7
        elif variance < 10:
            return 0.5
        else:
            return 0.2

    # ======================================================
    # SEARCH (DuckDuckGo HTML)
    # ======================================================

    def _search_text(self, query):

        results = []

        try:
            encoded_query = urllib.parse.quote(query[:150])
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

            response = requests.get(url, headers=self.headers, timeout=8)
            soup = BeautifulSoup(response.text, "html.parser")

            links = soup.find_all("a", class_="result__a")

            for link in links[:self.max_urls_per_sentence]:
                href = link.get("href")
                if href:
                    results.append(href)

        except Exception:
            pass

        return results

    # ======================================================
    # FETCH PAGE TEXT
    # ======================================================

    def _fetch_content(self, url):

        try:
            response = requests.get(url, headers=self.headers, timeout=8)
            soup = BeautifulSoup(response.content, "html.parser")

            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=" ")
            text = " ".join(text.split())

            return text[:12000]

        except Exception:
            return None

    # ======================================================
    # FILE PROCESSOR (SAFE VERSION)
    # ======================================================

    def extract_text_from_file(self, file_path, file_type):

        if file_type == "txt":
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception:
                return ""

        if file_type == "pdf":
            try:
                import pdfplumber
                text = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            text.append(t)
                return "\n".join(text)
            except Exception:
                return ""

        if file_type in ["docx", "doc"]:
            try:
                from docx import Document
                doc = Document(file_path)
                return "\n".join(
                    para.text for para in doc.paragraphs
                    if para.text.strip()
                )
            except Exception:
                return ""

        return ""

    # ======================================================
    # HELPERS
    # ======================================================

    def _split_sentences(self, text):
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if len(s.strip()) > 25]

    def _deduplicate(self, matches):
        seen = set()
        unique = []

        for match in sorted(matches, key=lambda x: x["similarity_score"], reverse=True):
            key = (match["matched_text"], match["source_url"])
            if key not in seen:
                seen.add(key)
                unique.append(match)

        return unique[:20]

    def _empty_result(self):
        return {
            "plagiarism_matches": [],
            "plagiarism_score": 0.0,
            "ai_probability": 0.0,
            "final_score": 0.0
        }

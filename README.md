# ✨ GlowMatch — Hybrid BeautyTech Recommendation System

A hybrid recommendation engine for skincare/beauty products, built for a
GenAI Internship technical assignment. Combines **Content-Based Filtering**
(TF-IDF ingredient similarity), **Semantic Vector Search** (LSA dense
embeddings + nearest-neighbor index), **Rule-Based Personalization**
(skin-type/category/budget filtering), and a **Mini-RAG explanation
generator** (retrieves shared ingredients, then generates a grounded
"why this was recommended" explanation).

Built on a real 1,472-product Sephora-sourced catalog: 116 brands, 6
categories, full ingredient lists, 5 skin-type suitability flags.

## 🎯 Scope

This project delivers the **recommendation pipeline end-to-end**: data
loading/cleaning, content-based filtering, semantic vector search,
rule-based personalization, popularity fallback, a mini-RAG explanation
generator, an evaluation suite, a Streamlit demo UI, and a FastAPI REST
layer. **Cart, checkout, and payment processing are explicitly out of
scope** — this is a recommendation engine, not a full storefront. See
`DOCUMENTATION.md` (Section 2) for details.

---

## 📁 Project Structure

```
glowmatch/
├── app.py                    # Streamlit testing UI (for humans, in a browser)
├── requirements.txt
├── DOCUMENTATION.md          # Full write-up: approach, architecture, decisions
├── TEST_CASES.md             # Success + failure test scenarios with real outputs
├── HLD_LLD.md                # System design: High-Level + Low-Level Design
├── data/
│   └── cosmetics.csv
└── src/
    ├── recommender.py        # Core hybrid recommendation engine
    ├── evaluate.py             # Evaluation metrics
    └── api.py                    # FastAPI REST service (for other programs/apps)
```

## ▶️ How to Run

### Option A — the Streamlit UI (for a human demo)
```bash
pip install -r requirements.txt
streamlit run app.py
```
Opens a browser with 4 tabs:
- **Find My Products** — personalized cold-start recommendations by skin type/budget
- **Similar Products** — "because you liked X," with a mini-RAG explanation
- **Trending** — top-rated products, optionally filtered by category
- **Ingredient Personas** — auto-discovered product clusters (unsupervised KMeans)

### Option B — the FastAPI REST service (for programmatic/production use)
```bash
uvicorn src.api:app --reload --port 8000
```
Then open **http://localhost:8000/docs** for an interactive, Postman-style
API explorer, or call it directly:
```bash
curl "http://localhost:8000/recommend?skin_type=Dry&max_price=50"
curl "http://localhost:8000/similar?product_id=1"
curl "http://localhost:8000/trending"
```
If a real Redis server is running on `localhost:6379`, the API uses it
automatically for caching; otherwise it falls back to an in-memory cache
with identical behavior (see `HLD_LLD.md`).

### Run the engine or evaluation directly
```bash
cd src
python recommender.py
python evaluate.py
```

## 📊 Evaluation

`src/evaluate.py` reports six proxy metrics — deliberately not called
"accuracy," since there's no user-preference ground truth to compare
against (see `DOCUMENTATION.md`, Section 12):

| Metric | Measured result |
|---|---|
| Skin-type filter compliance | 100.00% |
| Budget constraint satisfaction | 100.00% (250/250 rows, 5 price caps × 5 skin types) |
| Recommendation relevance (content coherence) | 0.5673 avg |
| Catalog coverage | 27.45% (from 50 sample queries) |
| Latency — similar products / personalized filter | ~4 ms / ~7 ms (uncached) |

Full methodology and how to interpret each number honestly is in
`DOCUMENTATION.md`, Sections 12–13. Test-by-test walkthroughs (including
budget-limit checks, invalid-input handling, and recommendation-count
checks) are in `TEST_CASES.md`.

## 🧠 One-paragraph summary

"I built a hybrid BeautyTech recommender that works without any user
purchase history — the realistic starting point for most early-stage
beauty platforms. It combines TF-IDF content-based filtering over
ingredient lists, semantic vector search using LSA embeddings indexed
with nearest-neighbor search (the same retrieval pattern a production
vector database implements), rule-based personalization by skin type and
budget for the cold-start case, and a mini-RAG explanation generator that
retrieves the actual shared ingredients between two products before
generating a grounded explanation. I evaluated it with proxy metrics
appropriate for catalog-only data, and documented real limitations I
found along the way — including a data-quality bug where one product's
ingredient field contained scraped marketing text instead of ingredients."

See `DOCUMENTATION.md` for the full breakdown.

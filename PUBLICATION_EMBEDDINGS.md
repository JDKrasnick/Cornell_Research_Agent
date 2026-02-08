# Publication-Enhanced Semantic Search

## Overview

The faculty search now includes **publication content** in semantic embeddings, allowing the agent to match students with faculty based on both research interests AND actual publication titles/abstracts.

## How It Works

### Before Enhancement
```
Embedding = faculty_name + research_interests
Example: "Thorsten Joachims: Machine Learning Methods and Theory"
```

### After Enhancement
```
Embedding = faculty_name + research_interests + top_publications

Example:
"Thorsten Joachims: Machine Learning Methods and Theory

Key Publications:
Paper: Recommendations as Treatments: Debiasing Learning and Evaluation - Most data for evaluating and training recommender systems is subject to selection biases...
Paper: MOReL: Model-Based Offline Reinforcement Learning - We present MOReL, an algorithmic framework for model-based offline reinforcement learning...
Paper: Fairness of Exposure in Rankings - Ranked search results have become the main mechanism for information discovery..."
```

## Benefits

### 1. **More Accurate Matching**
Students searching for "fairness in machine learning" will now match with:
- Faculty who mention "fairness" in research interests (original behavior)
- **NEW:** Faculty who have published papers on fairness, even if not explicitly listed in research interests

### 2. **Discovers Specific Research Areas**
- Student: "counterfactual evaluation of recommender systems"
- Matches faculty with publications on counterfactual learning, even if their general research interest says "machine learning"

### 3. **Better Understanding of Current Work**
- Research interests may be general or outdated
- Publications show what the faculty is **actually working on**
- Top-cited papers indicate areas of expertise

## Rebuilding Embeddings

### Default (With Publications)
```bash
PYTHONPATH=/Users/fastcheetah/PycharmProjects/Cornell_Research_Agent \
python scripts/build_embeddings.py --force-rebuild
```

This will:
- ✅ Include top 5 most-cited publications per faculty
- ✅ Include publication titles + first 300 chars of abstract
- ⏱️ Takes ~2-3x longer than without publications
- 💾 Creates richer, more accurate embeddings

### Options

**Exclude publications (faster, less accurate):**
```bash
python scripts/build_embeddings.py --force-rebuild --no-publications
```

**Adjust number of publications:**
```bash
# Include top 10 papers per faculty (more comprehensive)
python scripts/build_embeddings.py --force-rebuild --max-publications 10

# Include only top 3 papers (faster, still enhanced)
python scripts/build_embeddings.py --force-rebuild --max-publications 3
```

**Test the search:**
```bash
python scripts/build_embeddings.py \
  --test-query "fairness in machine learning rankings"
```

## What Publications Are Included

For each faculty member, the system includes:
1. **Top N publications** (default: 5) sorted by citation count
2. **Publication title** (full)
3. **Abstract preview** (first 300 characters)

This focuses on the most impactful and representative work.

## Agent Awareness

The agent has been updated to understand this capability:

**System Prompt:**
> "Search a database of Cornell faculty by research interests AND publication content (the search includes their top papers and abstracts for better matching)"

**Tool Description:**
> "Searches across both research interests AND publication content (titles and abstracts of top papers)"

The agent now knows that its search is publication-aware and can confidently make more nuanced recommendations.

## Performance Considerations

### Embedding Generation Time
- **Without publications:** ~30 seconds for 150 faculty
- **With publications (5 papers):** ~2-3 minutes for 150 faculty
- **With publications (10 papers):** ~4-5 minutes for 150 faculty

### Search Performance
- No impact on search speed (embeddings are pre-computed)
- Search remains <100ms

### Storage
- **Without publications:** ~500KB ChromaDB
- **With publications:** ~2-3MB ChromaDB (still very small)

## Example Improvements

### Before (Research Interests Only)
```
Query: "counterfactual evaluation"
Results:
  1. Prof. A - "machine learning" (weak match)
  2. Prof. B - "reinforcement learning" (weak match)
```

### After (With Publications)
```
Query: "counterfactual evaluation"
Results:
  1. Prof. Joachims - "machine learning" + Paper: "The Self-Normalized
     Estimator for Counterfactual Learning" (STRONG match)
  2. Prof. C - "causal inference" + Paper: "Counterfactual Risk
     Minimization" (STRONG match)
```

## Best Practices

1. **Rebuild after adding new faculty:** Publications need to be re-embedded
2. **Rebuild periodically:** As faculty publish new papers (quarterly or semester)
3. **Use --force-rebuild:** Ensures all embeddings are fresh
4. **Monitor quality:** Use --test-query to validate search results

## Technical Details

### Embedding Structure
```python
document_text = f"{faculty.name}: {faculty.research_interests}"

if include_publications:
    top_pubs = sorted(publications, key=lambda p: p.citation_count,
                     reverse=True)[:max_publications]

    for pub in top_pubs:
        abstract_preview = pub.abstract[:300] + "..."
        document_text += f"\n\nPaper: {pub.title} - {abstract_preview}"
```

### Storage in ChromaDB
- **Document:** Full text including publications (used for embedding)
- **Metadata:** Faculty details (NOT included in embedding, used for results)
- **Embedding:** 384-dimensional vector (all-MiniLM-L6-v2 model)

## Troubleshooting

**Issue:** Embeddings not updating
```bash
# Force complete rebuild
python scripts/build_embeddings.py --force-rebuild
```

**Issue:** Out of memory during embedding
```bash
# Reduce publications per faculty
python scripts/build_embeddings.py --force-rebuild --max-publications 3
```

**Issue:** Search results seem worse
```bash
# Test with and without publications
python scripts/build_embeddings.py --force-rebuild --no-publications
# Then compare to
python scripts/build_embeddings.py --force-rebuild
```

## Future Enhancements

Potential improvements:
- [ ] Weight recent publications higher
- [ ] Include publication keywords/topics
- [ ] Add author collaboration networks
- [ ] Include patent data
- [ ] Semantic clustering of publications

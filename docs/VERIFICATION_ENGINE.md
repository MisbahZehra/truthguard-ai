# Verification Engine
1. **Extraction** (`integrations/llm.py`): LLM provider returns claim sentences; normalization, entities, numbers, years, category and volatility are computed locally. Opinions/questions are dropped.
2. **Research** (`verification/pipeline.py`): queries = normalized claim + "entities latest official [year]". Stable facts skip search.
3. **Source intelligence** (`intelligence/sources.py`): authority by domain class (government 1.0 > official docs 0.92 > official company 0.9 > research 0.85 > news 0.7 > secondary 0.5 > other 0.4), dedupe by domain+path, ISO/RFC-2822 date parsing (unknown stays unknown).
4. **Judgement**: stance per source (supports/contradicts/neutral). Output is schema-validated; stances for URLs that were not retrieved are dropped; a correction is rejected if it contains numbers/versions absent from the excerpts.
5. **Decision** (`intelligence/engine.py`): see FRESHNESS_METHODOLOGY.md. Conflicts of comparable authority yield INSUFFICIENT_EVIDENCE rather than a forced verdict.
6. **Reconstruction**: corrected claims replaced with the validated correction + citation; unresolved claims are marked "(unverified)"/"(may be outdated)"; source list with publication dates appended.
Built-in heuristic judge compares numbers/versions only; configure an LLM (`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`) for semantic judgement.

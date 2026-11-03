### Part 1: Dataset Design & RAG Core

**Dataset Generation Choices (Task 1):**
* Seed: 42
* Priority Weights: 20% True, 80% False
* Expected Salary Range: ₹4,00,000 to ₹35,00,000 to reflect real-world compensation bands for these roles.

**Threshold Calibration (Task 4):**
* In-scope query top-1 similarities observed: 0.4902 to 0.8238
* Out-of-scope query similarities observed: 0.0262 to 0.0795
* **Chosen "I don't know" threshold: 0.3000**. This sits perfectly between the two clusters I empirically measured, ensuring strict grounding without relying on arbitrary tutorial defaults.

**Chunking Strategy Evaluation (Task 5):**
* Fixed Chunks Document-Level Accuracy (k=1): 100.0%
* Sentence Chunks Document-Level Accuracy (k=1): 80.0%
* **Recommendation:** I recommend deploying the Fixed Chunks strategy. Based on my evaluation, it achieved a perfect 100% precision/recall score at k=1, proving it retrieves the exact policy documents more reliably than the sentence-level chunking for this specific knowledge base.

### Part 2: Orchestration & Tools

**Escalation Score Design (Task 6):**
* Formula: `(0.5 if flagged_priority_review) + ((days_since_created / 30.0) * 0.5)`
* **Escalation Threshold:** I recommend escalation for any score `> 0.65`. This threshold corresponds to records that are explicitly flagged for priority review AND have been sitting in the system for more than 9 days, effectively filtering out low-priority or brand-new applications.


### Part 3: Evaluation & Deployment

**Final Evaluation Metrics (Task 13):**
* Average Accuracy: 0.96
* Average Grounding: 1.00
* Average Completeness: 0.91
* Average Safety: 1.00
* **Methodology:** Evaluated using a 15-query test set covering 12 in-scope KB topics, 1 tool lookup, 1 out-of-scope query, and 1 prompt injection attempt under the deterministic `MOCK_LLM` environment.

### Part 4: Resilience & Governance

**Four-Layer AI Governance Model (Task 15):**
* **Application Layer (Least Autonomy):** In `agents/crew_team.py`, the `lookup_tool` is exclusively bound to the `lookup_agent`. The `rag_agent` and `composer_agent` are explicitly denied access to the internal database tool, ensuring an HR Policy agent cannot accidentally or maliciously extract candidate salary data.
* **Risk Classification:** I classify this system as **Medium Risk**. While it does not make final autonomous hiring decisions (High Risk), it handles internal HR policies and applicant status tracking, which falls strictly into the "customer support tickets / internal workflow" tier.
* **Runtime Layer (Budget Cap):** Implemented in `security/guardrails.py`. Any query exceeding the character/token length limit is strictly rejected before reaching the LLM to prevent budget exhaustion attacks.


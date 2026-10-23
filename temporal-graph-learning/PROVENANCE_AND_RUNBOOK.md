# Graph benchmark provenance and execution ledger

## 1. Recovered original
- Canonical recovered source: [tower/noesis/cora_e47_benchmark.py](https://github.com/nicholaskouns-create/tower/blob/main/noesis/cora_e47_benchmark.py).
- Exact E47 eigenspace is constructed from the three-spin-2 total Casimir, selecting eigenvalues 6 and 30.
- Cora data: tkipf/pygcn `cora.content` and `cora.cites`. Feature mapping: 1433-dimensional bag-of-words to 125D via Gaussian QR seed 47.
- Original classification split: seed 2026, 20 nodes per class (140 total), 500 validation, 1000 test. This is **not** Planetoid's public split.
- Original model: graph diffusion plus logistic regression. Primary metric: classification accuracy.

## 2. New matched-rank control
- [Cora ablation](./cora_ablation.py): baseline 125D; E47 rank 47; ten independently sampled random rank-47 controls, all evaluated on the same original Cora split.
- The script writes raw test predictions and probabilities in `cora-ablation-results.json` and compact summary in `cora-ablation-summary.json`.
- The interval uses a Student-t 95% interval across random orientations at fixed dataset/split; it is **not** an uncertainty interval over dataset sampling, retraining, or seeds of the original feature map.
- Run: `python temporal-graph-learning/cora_ablation.py` from the E47-Kartekeya root. Requirements: NumPy 2.2.6, SciPy 1.15.3, scikit-learn 1.6.1. Requires network access for the first Cora download.
- [Actions workflow](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/e47-cora-ablation.yml) uploads results as run artifacts. An Actions artifact is not automatically committed into Git history.

## 3. TGBL-wiki
- [TGB intervention](./tgbl_wiki_ablation.py) patches the official `shenyangHuang/TGB` TGN runner to apply a fixed E47 or random rank-47 embedding intervention immediately before its unchanged link decoder, in training and evaluation.
- This is a **new intervention**, not a recovered historical implementation. It requires the upstream checkout, installed dependencies and the official v2 dataset with fixed validation/test negatives.
- The script applies a common fixed 125D carrier map and back-projects to TGN's embedding width. If TGN width is below 125, the induced effective embedding-space rank may differ from 47; the exact 125D projector rank remains 47. This must be audited before interpreting outcomes.
- Run one arm at a time, e.g. `python temporal-graph-learning/tgbl_wiki_ablation.py --tgb-root /path/to/TGB --arm e47 --seed 47 -- --data tgbl-wiki --num_run 1 --seed 1`.
- Preserve TGB's official MRR evaluator and frozen negative samples. No test MRR is asserted without executed receipts.

## 4. Historical AUC claims
- Reported TGBL-wiki AUC improvement: +0.0383.
- Reported Cora AUC improvement: +0.0082.
- The recovered Cora code evaluates classification accuracy, and TGB's official task evaluates MRR. Neither is an exact reproduction of the historical link-AUC experiments.
- Original AUC feature mapping, positive/negative edge selection, leakage controls and prediction files remain to be recovered. The numbers must not be labeled independently reproduced until that happens.

## 5. Publication
- [Evidence dashboard](https://nicholaskouns-create.github.io/e47-graph-evidence.html) is live-source HTML committed to the GitHub Pages repository. It displays **pending** until a summary JSON receipt is committed at `temporal-graph-learning/cora-ablation-summary.json`.
- This ledger is documentation of code and procedures, **not a claim that the new benchmarks ran successfully**.

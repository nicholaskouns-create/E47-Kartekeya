LEAN ?= lean
export LEAN_PATH := .

.PHONY: verify benchmark clean

verify: Bounds.olean Algebra.olean

Witness.olean: Witness.lean
	$(LEAN) -o $@ $<

Certificate.olean: Certificate.lean Witness.olean
	$(LEAN) -o $@ $<

Bounds.olean: Bounds.lean Certificate.olean
	$(LEAN) -o $@ $<

Algebra.olean: Algebra.lean Certificate.olean
	$(LEAN) -o $@ $<

benchmark:
	OPENBLAS_NUM_THREADS=1 python benchmark.py --output benchmark-results.json

clean:
	rm -f Witness.olean Certificate.olean Bounds.olean Algebra.olean

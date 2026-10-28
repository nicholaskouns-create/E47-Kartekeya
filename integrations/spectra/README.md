# SPECTRA circuit / visualization bridge (review integration)

Shared browser-native E47 **carrier addressing** and OpenQASM 2.0 UI parsing for Mathematical City / Identity cross-repository development. This is a proposed integration, not a production deployment or claim that the GitHub repository controls the Grok runtime.

## Files
- `spectra-carrier.mjs`: exact base-5 bijection, 7-qubit basis-state preparation, strict X/H/CX parser, explicit unused-state leakage analysis.
- `spectra-carrier.test.mjs`: local contract tests via `node --test integrations/spectra/spectra-carrier.test.mjs`.

## Integration plan
Use the parsed gate list in the app's circuit renderer and the decoded counts in its measurement panel. Authenticate ledger writes using a caller session with Supabase RLS and server-side validation. The supplied Next.js API route, React hook and proposed SQL migration live in the reviewed offline integration package; they are **not** directly deployable into SPECTRA's Grok frontend / Supabase Edge Function without a hosting adapter.

The exact fraction **47/125** is the rank fraction of the spin-2 tensor Casimir selector `(C-6I)(C-30I)`. It is not a generic 5-cycle graph kernel rank, a noise threshold, a superconductivity certificate, or a 47-site geometric address mask. The seven-qubit embedding adds three unused basis indices (125–127). A basis-state preparation circuit is not proof of an implemented E47 projection or continuous-time walk.

Reference live launch: https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-app-host/spectra/

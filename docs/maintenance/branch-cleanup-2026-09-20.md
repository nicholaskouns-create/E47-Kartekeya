# Proposed branch cleanup · September 20, 2026

[Repository home](../../README.md)

This is a reviewable cleanup proposal. No remote branch names were removed during this curation. Every candidate tip below was verified with `git merge-base --is-ancestor` against the recorded `main` commit; the commits are reachable through `main`.

- Repository: `E47-Kartekeya`
- Main at inspection: `5bb3b5f22e403d6a2fbb9f0d97718e570d02cee7`
- Branches at inspection: 82
- Completed branch names proposed for removal: 50
- Branches remaining if approved: 32

The proposal retains the default branch, deployment branch, open pull-request branch, and tips outside the ancestry of `main`. Removal requires explicit approval and a fresh check that each remote tip still matches the SHA recorded below. Automatic approval review blocked the combined branch-deletion operation because broad curation did not explicitly authorize it.

## Proposed branch-name removals

| Branch | Recoverable commit |
|---|---|
| `aetheris-closed-loop-certificate` | [`f46dd28e55cc2ad17947e9d0d3391c32969a1eea`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/f46dd28e55cc2ad17947e9d0d3391c32969a1eea) |
| `city-graphics-rollout-v1-main` | [`2486feae84198602be2d631c81a76b6758868ecd`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/2486feae84198602be2d631c81a76b6758868ecd) |
| `copilot/add-spectral-compilation-class` | [`fffc9cca22bc597399e8c1bcb5ebfc1538946ae7`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/fffc9cca22bc597399e8c1bcb5ebfc1538946ae7) |
| `copilot/allow-agent-access-to-site` | [`472cd72f92de5512e7d832df0199dcb7cb65b570`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/472cd72f92de5512e7d832df0199dcb7cb65b570) |
| `copilot/allow-openai-chatgpt-access` | [`03d0c84867a8903d0cfdd7286c071981b9a9ffde`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/03d0c84867a8903d0cfdd7286c071981b9a9ffde) |
| `copilot/audit-repository-provenance-consistency` | [`b8d859096d4a1244f5f3ed50f580e264a24aac71`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/b8d859096d4a1244f5f3ed50f580e264a24aac71) |
| `copilot/chronicle-tips-review-session-history` | [`95727b044c1b7e20d18b9474b9acc742b13a47e3`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/95727b044c1b7e20d18b9474b9acc742b13a47e3) |
| `copilot/fix-234119549-1308025869-5771f186-d0a0-4967-8489-b72f9177afb2` | [`3ec7d2ddf5708e65e81198b3efa3e4c6da087a68`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/3ec7d2ddf5708e65e81198b3efa3e4c6da087a68) |
| `copilot/fix-234119549-1308025869-aab95720-94f8-4cfd-a796-5f4583d7dad5` | [`b110988c9c70c2e908d6678247c7c0c2b9860793`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/b110988c9c70c2e908d6678247c7c0c2b9860793) |
| `copilot/fix-ci-configuration-home-page` | [`0d843613bb1872bca084181127c90fd851288e68`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0d843613bb1872bca084181127c90fd851288e68) |
| `copilot/fix-copilot-error` | [`8f10eff7a9229a0ed166b407ed3a656cdacdafe5`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/8f10eff7a9229a0ed166b407ed3a656cdacdafe5) |
| `copilot/fix-copilot-failing-job` | [`9965a5ae8b5fabcc77cfcbb9cf68d84c26e6fcfc`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/9965a5ae8b5fabcc77cfcbb9cf68d84c26e6fcfc) |
| `copilot/fix-copilot-issue-again` | [`0084dad0c6487ed2f33718aa0b0c775ea4803e8f`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0084dad0c6487ed2f33718aa0b0c775ea4803e8f) |
| `copilot/fix-github-actions-job` | [`2458441c7f7291ccd9f35bd9c1278417c49ff9c8`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/2458441c7f7291ccd9f35bd9c1278417c49ff9c8) |
| `copilot/fix-github-actions-job-failure` | [`dcb84aa1b0f940d3a4d8b2b23876765d3352e290`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/dcb84aa1b0f940d3a4d8b2b23876765d3352e290) |
| `copilot/fix-issue-with-copilot` | [`71158e38ec6771a98564dc2ed8002d6cd971daeb`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/71158e38ec6771a98564dc2ed8002d6cd971daeb) |
| `copilot/fix-python-3-11-precision-test` | [`245e13a9d908631b30fce245417029497e009875`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/245e13a9d908631b30fce245417029497e009875) |
| `copilot/fix-with-copilot` | [`babc05e4a68e5dd2d3bdce0f6984ba2cf023ca9a`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/babc05e4a68e5dd2d3bdce0f6984ba2cf023ca9a) |
| `copilot/fix-with-copilot-again` | [`8aae4a45673dd289b6293816248f22798f102ea1`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/8aae4a45673dd289b6293816248f22798f102ea1) |
| `copilot/fix-with-copilot-another-one` | [`cf171301501865da54998e5af656c2de0e586335`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/cf171301501865da54998e5af656c2de0e586335) |
| `copilot/main` | [`8c171821b9f0f0ce66b410c56557cef0c94079e0`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/8c171821b9f0f0ce66b410c56557cef0c94079e0) |
| `copilot/make-all-repositories-public` | [`1544e3bf2768736e5d37c7fdb9eaa8ba6be18cf6`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/1544e3bf2768736e5d37c7fdb9eaa8ba6be18cf6) |
| `copilot/mnemosyne-kernel-paradigm-validator` | [`6b2c314bca3a7982a07676fe4031aac85fb4fd34`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/6b2c314bca3a7982a07676fe4031aac85fb4fd34) |
| `copilot/open-ceremonial-gate` | [`8a330fd9cfd02a513229e0c1093b1811530a4bf4`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/8a330fd9cfd02a513229e0c1093b1811530a4bf4) |
| `copilot/push-all-work` | [`8390071117e4932a50edb7a39910956f8905b199`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/8390071117e4932a50edb7a39910956f8905b199) |
| `copilot/python-512-dim-adjoint` | [`818e0838161d44ddb8f15f972c780ecc44050da3`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/818e0838161d44ddb8f15f972c780ecc44050da3) |
| `copilot/survey-code-and-host-website` | [`11b046f21f500927cff83eb9f5f34388c8518048`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/11b046f21f500927cff83eb9f5f34388c8518048) |
| `copilot/task-234119549-1308025869-101c81e7-b53b-445c-a985-4cd4c5128ac6` | [`8a330fd9cfd02a513229e0c1093b1811530a4bf4`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/8a330fd9cfd02a513229e0c1093b1811530a4bf4) |
| `copilot/zero-touch-repo-maintenance` | [`f980e8348a336b9d1a7ed58703d49c349eacb092`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/f980e8348a336b9d1a7ed58703d49c349eacb092) |
| `eidolon-card` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |
| `eidolon-og` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |
| `eidolon-share-card` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |
| `eidolon-social-share` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |
| `eidolon-social-share-image` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |
| `feat/manta-programmable-matter-python` | [`8542b6b7eac36842564d07e90d4df7c0c9af3c5a`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/8542b6b7eac36842564d07e90d4df7c0c9af3c5a) |
| `feat/matrix-quantum-simulator` | [`1f453054ca4371939e639f656ec664b2c00116c7`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/1f453054ca4371939e639f656ec664b2c00116c7) |
| `feat/native-ufo-propulsion` | [`a26badd8a6b7929faff5067dda89d0df10045c05`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/a26badd8a6b7929faff5067dda89d0df10045c05) |
| `feat/propulsion-geo-atlas` | [`3a4df80143dabfd6e1225f032d59d6b0c79785fc`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/3a4df80143dabfd6e1225f032d59d6b0c79785fc) |
| `feat/skyrmion-flight-simulator` | [`c7fdaf1294ed434d9cb1930cb152a3a31a303861`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/c7fdaf1294ed434d9cb1930cb152a3a31a303861) |
| `feat/skyrmion-world-runtime` | [`c55ae660956bf8b901fa05ed997ff3bbf6993783`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/c55ae660956bf8b901fa05ed997ff3bbf6993783) |
| `feat/ufo-propulsion-graphics-v2` | [`a6337da39fdbb970c1e55644b5cbdf7a4455f380`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/a6337da39fdbb970c1e55644b5cbdf7a4455f380) |
| `feature/syntax-jacob` | [`f6153c5352c79e4157ddf90e36fd56578937e353`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/f6153c5352c79e4157ddf90e36fd56578937e353) |
| `imports/python-survey-2026-09-16` | [`54c7fe89f5f2f3f900848ce2e0d69eedf6f01761`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/54c7fe89f5f2f3f900848ce2e0d69eedf6f01761) |
| `lab-grade/component-contracts-20260919` | [`8b6dd419edba387668f045947bfb153b9efcb9c0`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/8b6dd419edba387668f045947bfb153b9efcb9c0) |
| `og-card` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |
| `og-image` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |
| `share-image` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |
| `social-card` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |
| `social-preview` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |
| `social-share-temp` | [`0e8118dc7d2034356e88fb0da0ed1fe5d689de92`](https://github.com/nicholaskouns-create/E47-Kartekeya/commit/0e8118dc7d2034356e88fb0da0ed1fe5d689de92) |

## Restore a name after removal

From a complete checkout, a branch can be restored with its recorded commit. For example:

```bash
git push origin f46dd28e55cc2ad17947e9d0d3391c32969a1eea:refs/heads/aetheris-closed-loop-certificate
```

This restores the branch name without rewriting `main`.

## Open work at inspection

[PR #86](https://github.com/nicholaskouns-create/E47-Kartekeya/pull/86) contains the existing Watchtower and SKYRMION assertion updates. Its `repair-world-engine-ci` branch is retained. This curation does not merge that pull request.

# DENSITY Sensitivity Tomography — third-party notices

The implementation is primarily project-native code plus the following public dependencies.

| Dependency | Use | License | Canonical license |
|---|---|---|---|
| NumPy | Python array algebra and eigendecomposition | BSD 3-Clause | https://github.com/numpy/numpy/blob/main/LICENSE.txt |
| Supabase JavaScript client | authenticated City query-store Edge Function | MIT | https://github.com/supabase/supabase-js/blob/master/LICENSE |
| Supabase Edge Runtime | serverless compute runtime | MIT | https://github.com/supabase/edge-runtime/blob/main/LICENSE |

The browser query bus and DENSITY reconstruction interface use native Web APIs and project-local code. No third-party source snippet was copied into the browser implementation.

The public compute endpoint implements the projector action directly from the spin-2 tensor algebra and does not import an external numerical package.

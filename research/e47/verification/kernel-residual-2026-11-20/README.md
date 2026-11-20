# E47 kernel certificate and residual audit

This bundle uses the spin-2 triple carrier from [E47-Kartekeya](https://github.com/nicholaskouns-create/E47-Kartekeya/tree/44c85a2c0c8f2c357da79b638233e3e8339f8e91). The Lean certificate starts from packed quinary coordinates and checks the full 125 by 125 matrices. [Transfer.md](Transfer.md) proves the general residual and external implementation bounds, including nonnormal operators. [Benchmark.md](Benchmark.md) explains the paired software fault-injection experiment.

## Reproduce

Use Lean 4.19.0, Make, and for the benchmark Python 3.12 with the pinned dependencies and a C++17 compiler. The Lean proof has no Mathlib dependency. With an installed Lean toolchain and the files in this directory, run:

```sh
make verify
python -m pip install -r requirements.txt
make benchmark
```

The integer witnesses are included. Rebuilding them is optional: run `python generate.py`, then `make verify`. Python supplies candidate witnesses, and Lean checks them independently. Lean 4.19's `native_decide` trusts native evaluation through `Lean.ofReduceBool`. The exact matrix checks, kernel statements, and discrete energy theorem use this trust model. The real/complex interpretation and continuous-time consequences below are written mathematical deductions from the finite certificate. The benchmark executable is a separate implementation of the exact residual calculation.

## Kernel and contraction

For $d=0,\ldots,4$ put $m=d-2$. In the scaled native basis the single-site ladders act with coefficients $2-m$ and $2+m$. The metric weights are $(12,3,2,3,12)$. They satisfy $w_{d+1}/w_d=(d+1)/(4-d)$, so conjugating by the diagonal square roots of the weights gives the standard raising coefficient $\sqrt{(2-m)(3+m)}$ and the adjoint lowering coefficient. On the tensor basis the metric is the product of the three weights. The certificate checks the matrix formula $C=J_z^2+(J_+J_-+J_-J_+)/2$ for the total ladders and magnetization.

Lean checks $CW=WD$, $LW=WL=sI$, and $W^\mathsf{T}HW=\operatorname{diag}(g_j)$ for all entries. Here $D$ holds the Casimir eigenvalues, $H$ is the native metric, $s>0$ is an integer, and the Gram norms $g_j$ are positive. The integer identities extend unchanged under the canonical integer embedding into the complex numbers. Thus $W^{-1}=L/s$ over $\mathbb C$ and the columns of $W/\sqrt{g_j}$, interpreted columnwise, form an orthonormal eigenbasis for the physical inner product.

| Casimir eigenvalue | 0 | 2 | 6 | 12 | 20 | 30 | 42 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dimension | 1 | 9 | 25 | 28 | 27 | 22 | 13 |
| $K=(C-6I)(C-30I)$ eigenvalue | 180 | 112 | 0 | −108 | −140 | 0 | 432 |
| $K^2$ eigenvalue | 32400 | 12544 | 0 | 11664 | 19600 | 0 | 186624 |

The kernel is exactly the direct sum of the Casimir 6 and 30 eigenspaces. It has dimension 47 and an orthogonal complement of dimension 78. The orthogonal projector is $P=\prod_{u\in\{11664,12544,19600,32400,186624\}}(I-K^2/u)$. Each factor is the identity on the kernel, and one factor vanishes on each complementary eigenspace. The spectral table gives
$$
108\|(I-P)x\| \le \|Kx\| \le 432\|(I-P)x\|.
$$
The endpoints are attained on eigenvectors. Lean verifies the finite endpoints and proves the kernel criterion on native integer vectors with the left-inverse numerator as a decoder. It also checks that the scaled projector maps into the kernel, fixes the kernel up to scale, and is idempotent up to scale.

For the Richardson step $\Gamma=I-K^2/99144$, $99144=(11664+186624)/2$. The affine multiplier takes endpoint values $\pm15/17$ and lies between them on the complementary spectrum, while its value on the kernel is one. Consequently, for every integer $n\ge 0$,
$$
\|\Gamma^n-P\|_{2\to2}=(15/17)^n .
$$
Lean checks the optimal scalar factor, proves the exact native numerator action at every step, and proves the all-step weighted squared-energy bound with denominators cleared. The energy lemma applies to arbitrary nonnegative integer masses. Scaling extends it to rational masses and continuity of the finite sums extends it to real masses, including the squared magnitudes of arbitrary complex coefficients in the orthogonal basis. The endpoint mode gives equality. The signed step $I-hK$ with $h>0$ expands the Casimir 12 eigenspace and cannot furnish the claimed contraction.

For any $t\ge 0$,
$$
\|e^{-tK^2}-P\|_{2\to2}=e^{-11664t},
\qquad
\|K e^{-tK^2}x\|\le e^{-11664t}\|Kx\|.
$$
The exponential acts diagonally in the same basis, with multipliers $e^{-t u}$, and the largest complementary multiplier is attained at $u=11664$. The analogous stepped residual bound is $\|K\Gamma^n x\|\le(15/17)^n\|Kx\|$. For energy $\mathcal L(x)=\tfrac12\|Kx\|^2$, along $x'=-K^2x$ one has $\mathcal L'=-\|K^2x\|^2$. The alternative convex-mean step $B=P+(78/125)(I-P)$ satisfies $\|B^n-P\|=(78/125)^n$ by orthogonality and idempotence.

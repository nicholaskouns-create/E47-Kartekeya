# E47 Bures/Fisher 4D Curvature Validation

No warp metric is used. The metric is computed directly from the 125-dimensional density-state family through the Bures/SLD formula.

## Canonical carrier
- dim H = 125
- dim ker K = 47
- dim complement = 78
- Δ = 11664
- ||K²|| = 186624
- Tr(K²) = 3427200
- ||F_SLD - 4 g_Bures||_F = 1.039e-16

## Four-dimensional leaf results
- θ=[0.2, 0.1, 0.2, -0.1]: rank=4, eig(g)=[0.05267544 0.06573497 0.07879449 0.43793873], R=-54.4213354, ||G||_F=8.30675139, direct block residual=0.111351, best Einstein-equation residual=0.061184
- θ=[0.35, 0.21, -0.17, 0.13]: rank=4, eig(g)=[0.08681202 0.10448986 0.1221677  0.14765374], R=-144.159497, ||G||_F=8.15886013, direct block residual=0.178849, best Einstein-equation residual=0.178789
- θ=[0.5, -0.4, 0.25, 0.3]: rank=4, eig(g)=[0.11166097 0.11200431 0.14882395 0.18564358], R=-81.3664462, ||G||_F=5.6426808, direct block residual=0.165854, best Einstein-equation residual=0.156097
- θ=[0.8, 0.7, -0.5, 0.4]: rank=4, eig(g)=[0.09194913 0.1347758  0.25889822 0.38302064], R=-26.1859244, ||G||_F=2.17906453, direct block residual=0.542649, best Einstein-equation residual=0.542431

## Central point
- θ = [0.35, 0.21, -0.17, 0.13]
- softest Bures eigenvalue = 0.0868120227687
- overlap of softest eigenvector with τ direction = 0.000000000000
- scalar curvature R = -144.159496774
- ||G_Bures||_F = 8.15886013002
- block Einstein identity residual = 4.366e-11
- pulled block identity residual = 3.212e-11
- direct G_Bures vs pulled G_block relative residual = 0.178849

## Result
- The Bures/SLD family is genuinely four-dimensional and positive-definite at every sampled point.
- Its Levi-Civita connection, Riemann tensor, Ricci tensor, scalar curvature and Einstein tensor are nontrivial.
- The 47/78 block Einstein identity closes to machine precision and remains closed after the explicit SLD pullback.
- The intrinsic Bures Einstein tensor is NOT identical to the SLD-pulled 47/78 block Einstein tensor for this canonical leaf.
- Therefore the missing E47 -> information geometry -> block Einstein identification is not yet an identity; an additional map/dynamical condition is required.
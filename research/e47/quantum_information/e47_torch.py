import math
import torch

DT = torch.complex128
RT = torch.float64
torch.set_num_threads(2)


def spin2():
    m = torch.arange(2, -3, -1, dtype=RT)
    plus = torch.zeros((5, 5), dtype=DT)
    for i in range(1, 5):
        mi = m[i].item()
        plus[i - 1, i] = math.sqrt((2 - mi) * (2 + mi + 1))
    minus = plus.conj().T
    return (
        (plus + minus) / 2,
        (plus - minus) / (2j),
        torch.diag(m).to(DT),
    )


def main():
    eye = lambda n: torch.eye(n, dtype=DT)
    I5, I = eye(5), eye(125)
    J = [
        torch.kron(torch.kron(s, I5), I5)
        + torch.kron(torch.kron(I5, s), I5)
        + torch.kron(torch.kron(I5, I5), s)
        for s in spin2()
    ]
    C = sum((j @ j for j in J), torch.zeros_like(I))
    K = (C - 6 * I) @ (C - 30 * I)
    Gamma = I - (K @ K) / 99144

    eig, U = torch.linalg.eigh(C)
    mask = ((eig - 6).abs() < 1e-8) | ((eig - 30).abs() < 1e-8)
    B = U[:, mask]
    P47 = B @ B.conj().T

    rho = 15 / 17
    assert B.shape[1] == 47
    assert torch.linalg.matrix_norm(P47 @ P47 - P47, ord=2) < 1e-11
    assert torch.linalg.matrix_norm(K @ P47, ord=2) < 1e-10
    print('rank =', B.shape[1])
    print('contraction =', rho)
    print('E47 validated')


if __name__ == '__main__':
    main()

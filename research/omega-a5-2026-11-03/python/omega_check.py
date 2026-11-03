import sympy as s
import mpmath as mp
x=s.symbols('x')
d=[1,9,25,28,27,22,13]
u=[s.chebyshevu(2*j,x) for j in range(7)]
N=s.expand(25*u[2]**2+22*u[5]**2)
D=s.expand(sum(d[j]*u[j]**2 for j in range(7)))
assert N.subs(x,0)==47 and D.subs(x,0)==125
assert s.factor(47*D-125*N).has(x**2)
print('factorization:',s.factor(47*D-125*N))
print('squarefree:',s.gcd(D,s.diff(D,x))==1)
assert s.simplify((47*D-125*N).subs(x,s.sqrt(2)/2))==0
mp.mp.dps=40
eta=s.lambdify(x,N/D,'mpmath')
mean=mp.quad(lambda y:eta(y)*2/mp.pi*mp.sqrt(1-y*y),
  [-1,-mp.sqrt(2)/2,0,mp.sqrt(2)/2,1])
print('mean:',mp.nstr(mean,35))
print('omega:',mp.nstr(mp.mpf(47)/125-mean,35))

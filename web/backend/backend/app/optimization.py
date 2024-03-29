from scipy.optimize import milp, LinearConstraint, Bounds
import numpy as np

def set_cover(A):
    A = A.T
    c = np.ones_like(A[0])
    constraints = LinearConstraint(A, lb=np.ones_like(A[0]))
    bounds = Bounds(lb=0, ub=1)
    integrality = np.ones_like(A[0])
    cover = milp(c=c, constraints=constraints, bounds=bounds, integrality=integrality)

    result = np.where(cover.x > 0.5, 1, 0)
    return result

def test_function():
    N = 5
    A = np.random.randint(2, size=(N, N))
    print(A)
    res = set_cover(A)

    print(f"solution: {res.x}")
    print(res.success)

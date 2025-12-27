from __future__ import annotations
import math
import numpy as np

g = 9.80665  # m/s^2

def area_rectangular(y: float, b: float) -> float:
    return b * y

def perimeter_rectangular(y: float, b: float) -> float:
    return b + 2.0 * y

def hydraulic_radius_rectangular(y: float, b: float) -> float:
    a = area_rectangular(y, b)
    p = perimeter_rectangular(y, b)
    return a / p

def manning_velocity(n: float, R: float, S: float) -> float:
    return (1.0/n) * R**(2.0/3.0) * S**0.5

def discharge_rectangular(y: float, b: float, n: float, S: float) -> float:
    A = area_rectangular(y, b)
    R = hydraulic_radius_rectangular(y, b)
    V = manning_velocity(n, R, S)
    return A * V

def normal_depth_rectangular(Q: float, b: float, n: float, S0: float, y0: float | None = None, tol: float = 1e-9, itmax: int = 50) -> float:
    """Solve normal depth for a wide or narrow rectangular channel with Manning's equation."""
    if y0 is None:
        y0 = max(1e-3, (Q * n / (b * S0**0.5)) ** (3.0 / 5.0))  # heuristic
    y = y0
    for _ in range(itmax):
        A = b * y
        P = b + 2*y
        R = A / P
        f = (1/n) * A * R**(2/3) * S0**0.5 - Q
        # derivative df/dy via chain rule
        dA = b
        dP = 2.0
        dR = (dA*P - A*dP) / (P**2)
        df = (1/n) * (dA * R**(2/3) + A * (2/3) * R**(-1/3) * dR) * S0**0.5
        step = f/df
        y -= step
        if abs(step) < tol:
            return float(max(y, 1e-6))
    raise RuntimeError("normal_depth_rectangular did not converge")


def specific_energy_rectangular(y: float, Q: float, b: float) -> float:
    A = b*y
    V = Q/A
    return y + V**2/(2*g)

def froude_rectangular(y: float, Q: float, b: float) -> float:
    A = b*y
    T = b
    return Q / A / math.sqrt(g * A / T)

def gradually_varied_profile(Q: float, b: float, n: float, S0: float, z: np.ndarray, dx: float, y0: float) -> np.ndarray:
    """Very simple explicit M2-like backwater computation for a rectangular channel.
    Educational use only. Stable for mild slopes and small dx.
    """
    y = float(y0)
    ys = []
    for i in range(len(z)):
        # compute Sf with Manning using current depth
        A = b*y
        P = b + 2*y
        R = A/P
        V = (1.0/n) * R**(2.0/3.0) * S0**0.5  # use normal-velocity scaling for simplicity
        Qcalc = A*V
        Sf = (Qcalc / (A * (1.0/n) * R**(2.0/3.0)))**2  # rearranged; crude
        # dy/dx from GVF equation: dy/dx = (S0 - Sf)/(1 - Fr^2)
        Fr = froude_rectangular(y, Q, b)
        denom = max(1e-6, 1.0 - Fr**2)
        dydx = (S0 - Sf) / denom
        y = max(1e-4, y + dydx * dx)
        ys.append(y)
    return np.asarray(ys)

import numpy as np

# Let Dataset Alpha be the E47 model values from image_VeFBrx.png and image_Kna6vJ.png
# s12^2 = 15/49, s23^2 = 25/47, s13^2 = 1/47, delta = 16*pi/15 (192 deg)
s12_sq_A = 15.0 / 49.0
s23_sq_A = 25.0 / 47.0
s13_sq_A = 1.0 / 47.0
delta_A = 16.0 * np.pi / 15.0

# PDG / NuFIT 6.0 Normal Ordering (NO) values
# NuFIT 6.0 (with SK atmospheric):
# sin^2 theta_12 = 0.307 (or 0.303 - 0.311)
# sin^2 theta_23 = 0.572 (or 0.581, second octant favored in global NO)
# sin^2 theta_13 = 0.02203
# delta_CP = 197 deg (or 1.09 pi)

s12_sq_B = 0.307
s23_sq_B = 0.581
s13_sq_B = 0.02203
delta_B = 197.0 * np.pi / 180.0

def build_pmns(s12_sq, s23_sq, s13_sq, delta):
    s12 = np.sqrt(s12_sq)
    c12 = np.sqrt(1.0 - s12_sq)
    s23 = np.sqrt(s23_sq)
    c23 = np.sqrt(1.0 - s23_sq)
    s13 = np.sqrt(s13_sq)
    c13 = np.sqrt(1.0 - s13_sq)
    
    # Standard Chau-Keung / PDG parametrization:
    # U = [[c12*c13, s12*c13, s13*e^(-i*delta)],
    #      [-s12*c23 - c12*s23*s13*e^(i*delta), c12*c23 - s12*s23*s13*e^(i*delta), s23*c13],
    #      [s12*s23 - c12*c23*s13*e^(i*delta), -c12*s23 - s12*c23*s13*e^(i*delta), c23*c13]]
    
    U = np.zeros((3, 3), dtype=complex)
    U[0, 0] = c12 * c13
    U[0, 1] = s12 * c13
    U[0, 2] = s13 * np.exp(-1j * delta)
    
    U[1, 0] = -s12 * c23 - c12 * s23 * s13 * np.exp(1j * delta)
    U[1, 1] = c12 * c23 - s12 * s23 * s13 * np.exp(1j * delta)
    U[1, 2] = s23 * c13
    
    U[2, 0] = s12 * s23 - c12 * c23 * s13 * np.exp(1j * delta)
    U[2, 1] = -c12 * s23 - s12 * c23 * s13 * np.exp(1j * delta)
    U[2, 2] = c23 * c13
    
    return U

UA = build_pmns(s12_sq_A, s23_sq_A, s13_sq_A, delta_A)
UB = build_pmns(s12_sq_B, s23_sq_B, s13_sq_B, delta_B)

absUA = np.abs(UA)
absUB = np.abs(UB)

print("Dataset Alpha |U|:")
print(np.round(absUA, 3))
print("angles A (deg):", np.arcsin(np.sqrt([s12_sq_A, s23_sq_A, s13_sq_A]))*180/np.pi, delta_A*180/np.pi)

print("\nDataset Beta |U|:")
print(np.round(absUB, 3))
print("angles B (deg):", np.arcsin(np.sqrt([s12_sq_B, s23_sq_B, s13_sq_B]))*180/np.pi, delta_B*180/np.pi)

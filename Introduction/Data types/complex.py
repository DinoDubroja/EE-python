import cmath
import math

# 1. Literal definitions & basics
z1 = 3 + 4j               # rectangular form (3 + j4)
z2 = complex(5, -2)       # same via constructor
print(z1, z2)             # (3+4j) (5-2j)

# arithmetic
print(z1 + z2)            # addition → (8+2j)
print(z1 * z2)            # multiplication
print(z1 / z2)            # division
print(z1.conjugate())     # complex conjugate → (3-4j)


# 2. Parts, magnitude & phase
print(z1.real, z1.imag)   # 3.0 4.0
r, phi = cmath.polar(z1)  # returns (magnitude, angle in radians)
print(r, phi)             # 5.0, 0.9273…
print(f"{math.degrees(phi):.1f}°")  # convert to degrees → 53.1°

# back to rectangular
z_rect = cmath.rect(r, phi)
print(z_rect)             # (3+4j)


# 3. EE Use Case: Impedance of R, L, C at ω
f     = 1e3               # 1 kHz
ω     = 2 * math.pi * f
R     = 100               # 100 Ω resistor
L     = 1e-3              # 1 mH inductor
C     = 1e-6              # 1 µF capacitor

Z_R = R
Z_L = 1j * ω * L           # jωL
Z_C = 1 / (1j * ω * C)     # 1/(jωC)

Z_series   = Z_R + Z_L + Z_C
Z_parallel = 1 / (1/Z_R + 1/Z_L + 1/Z_C)

print("Series Z:", Z_series)
print("Parallel Z:", Z_parallel)


# 4. Phasor addition
V1 = 230 * cmath.exp(1j * math.radians(30))   # 230 V ∠30°
V2 = 230 * cmath.exp(1j * math.radians(-30))  # 230 V ∠-30°
Vtot = V1 + V2
print("Vtot:", abs(Vtot), f"{math.degrees(cmath.phase(Vtot)):.1f}°")


# 5. Complex power: S = V · I*
I  = 2 * cmath.exp(1j * math.radians(45))     # 2 A ∠45°
V  = 220 * cmath.exp(1j * 0)                  # 220 V ∠0°
S  = V * I.conjugate()                        # VA
P  = S.real                                   # active power (W)
Q  = S.imag                                   # reactive power (VAR)
print(f"S={S:.1f} VA, P={P:.1f} W, Q={Q:.1f} VAR")


# 6. Frequency response of a first-order RC low-pass: H(jω)=1/(1+jωRC)
H = 1 / (1 + 1j * ω * R * C)
print("H mag:", abs(H), "phase:", f"{math.degrees(cmath.phase(H)):.1f}°")


# 7. Edge Cases: zero and infinities
z_zero = 0 + 0j
print(z1 / z_zero)       # division by zero → raises ZeroDivisionError
print((1+0j) * (math.inf + 0j))  # inf+0j
print((1+0j) * (math.nan + 1j))  # nan complex result
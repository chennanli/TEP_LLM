# Tennessee Eastman Process (TEP) - Physical Properties & Thermodynamic Constants

## 📋 Overview

This document contains all physical properties, thermodynamic constants, and calculation methods used in the Tennessee Eastman Process (TEP) Fortran simulation. All constants are extracted from the `TEINIT` subroutine in `teprob.f`.

## 🧪 Component Identification

| Component | ID | Description | Type | Molecular Weight (kg/kmol) |
|-----------|----|-----------|----|---------------------------|
| **A** | 1 | Hydrogen-like | Light Gas | 2.0 |
| **B** | 2 | Intermediate | Gas | 25.4 |
| **C** | 3 | Nitrogen-like | Gas | 28.0 |
| **D** | 4 | Oxygen-like | Condensable | 32.0 |
| **E** | 5 | Heavy Reactant | Condensable | 46.0 |
| **F** | 6 | Byproduct | Condensable | 48.0 |
| **G** | 7 | Product 1 | Heavy Product | 62.0 |
| **H** | 8 | Product 2 | Heavy Product | 76.0 |

## 🌡️ Thermodynamic Property Calculations

### 1. Enthalpy Calculations (TESUB1)

#### Liquid Phase Enthalpy (ITY = 0):
```
H_liquid = Σ[Xi * MWi * T * (AHi + BHi*T/2 + CHi*T²/3) * 1.8]
```

#### Gas Phase Enthalpy (ITY = 1):
```
H_gas = Σ[Xi * MWi * (T*(AGi + BGi*T/2 + CGi*T²/3) + AVi) * 1.8]
```

#### Vapor Phase Enthalpy (ITY = 2):
```
H_vapor = H_gas - R*(T + 273.15)
where R = 3.57696×10⁻⁶
```

### 2. Temperature from Enthalpy (TESUB2)
Uses Newton-Raphson iteration to solve:
```
T_target = f⁻¹(H_target)
```
Algorithm:
```
T_new = T_old - (H_calculated - H_target) / (dH/dT)
```

### 3. Enthalpy Derivative (TESUB3)

#### Liquid Phase:
```
dH/dT = Σ[Xi * MWi * (AHi + BHi*T + CHi*T²) * 1.8]
```

#### Gas Phase:
```
dH/dT = Σ[Xi * MWi * (AGi + BGi*T + CGi*T²) * 1.8]
```

### 4. Liquid Density (TESUB4)
```
Specific Volume: V = Σ[Xi * MWi / (ADi + BDi*T + CDi*T²)]
Density: ρ = 1/V
```

### 5. Vapor Pressure (Antoine Equation)
```
ln(P_vapor) = AVPi + BVPi/(T + CVPi)
P_partial = P_vapor * X_liquid
```
*Note: Only applies to components 4-8 (condensable components)*

## 📊 Complete Physical Property Constants

### Molecular Weights
```fortran
XMW(1) = 2.0      ! Component A
XMW(2) = 25.4     ! Component B  
XMW(3) = 28.0     ! Component C
XMW(4) = 32.0     ! Component D
XMW(5) = 46.0     ! Component E
XMW(6) = 48.0     ! Component F
XMW(7) = 62.0     ! Component G
XMW(8) = 76.0     ! Component H
```

### Antoine Equation Constants (Vapor Pressure)
```fortran
! AVP Constants
AVP(1) = 0.0      ! Component A (non-condensable)
AVP(2) = 0.0      ! Component B (non-condensable)
AVP(3) = 0.0      ! Component C (non-condensable)
AVP(4) = 15.92    ! Component D
AVP(5) = 16.35    ! Component E
AVP(6) = 16.35    ! Component F
AVP(7) = 16.43    ! Component G
AVP(8) = 17.21    ! Component H

! BVP Constants  
BVP(1) = 0.0      ! Component A
BVP(2) = 0.0      ! Component B
BVP(3) = 0.0      ! Component C
BVP(4) = -1444.0  ! Component D
BVP(5) = -2114.0  ! Component E
BVP(6) = -2114.0  ! Component F
BVP(7) = -2748.0  ! Component G
BVP(8) = -3318.0  ! Component H

! CVP Constants
CVP(1) = 0.0      ! Component A
CVP(2) = 0.0      ! Component B
CVP(3) = 0.0      ! Component C
CVP(4) = 259.0    ! Component D
CVP(5) = 265.5    ! Component E
CVP(6) = 265.5    ! Component F
CVP(7) = 232.9    ! Component G
CVP(8) = 249.6    ! Component H
```

### Liquid Density Constants
```fortran
! AD Constants (Density intercept)
AD(1) = 1.0       ! Component A
AD(2) = 1.0       ! Component B
AD(3) = 1.0       ! Component C
AD(4) = 23.3      ! Component D
AD(5) = 33.9      ! Component E
AD(6) = 32.8      ! Component F
AD(7) = 49.9      ! Component G
AD(8) = 50.5      ! Component H

! BD Constants (Linear temperature coefficient)
BD(1) = 0.0       ! Component A
BD(2) = 0.0       ! Component B
BD(3) = 0.0       ! Component C
BD(4) = -0.0700   ! Component D
BD(5) = -0.0957   ! Component E
BD(6) = -0.0995   ! Component F
BD(7) = -0.0191   ! Component G
BD(8) = -0.0541   ! Component H

! CD Constants (Quadratic temperature coefficient)
CD(1) = 0.0       ! Component A
CD(2) = 0.0       ! Component B
CD(3) = 0.0       ! Component C
CD(4) = -0.0002   ! Component D
CD(5) = -0.000152 ! Component E
CD(6) = -0.000233 ! Component F
CD(7) = -0.000425 ! Component G
CD(8) = -0.000150 ! Component H
```

### Liquid Heat Capacity Constants
```fortran
! AH Constants (Intercept)
AH(1) = 1.0E-6    ! Component A
AH(2) = 1.0E-6    ! Component B
AH(3) = 1.0E-6    ! Component C
AH(4) = 0.960E-6  ! Component D
AH(5) = 0.573E-6  ! Component E
AH(6) = 0.652E-6  ! Component F
AH(7) = 0.515E-6  ! Component G
AH(8) = 0.471E-6  ! Component H

! BH Constants (Linear temperature coefficient)
BH(1) = 0.0       ! Component A
BH(2) = 0.0       ! Component B
BH(3) = 0.0       ! Component C
BH(4) = 8.70E-9   ! Component D
BH(5) = 2.41E-9   ! Component E
BH(6) = 2.18E-9   ! Component F
BH(7) = 5.65E-10  ! Component G
BH(8) = 8.70E-10  ! Component H

! CH Constants (Quadratic temperature coefficient)
CH(1) = 0.0       ! Component A
CH(2) = 0.0       ! Component B
CH(3) = 0.0       ! Component C
CH(4) = 4.81E-11  ! Component D
CH(5) = 1.82E-11  ! Component E
CH(6) = 1.94E-11  ! Component F
CH(7) = 3.82E-12  ! Component G
CH(8) = 2.62E-12  ! Component H
```

### Gas Heat Capacity Constants
```fortran
! AG Constants (Intercept)
AG(1) = 3.411E-6  ! Component A
AG(2) = 0.3799E-6 ! Component B
AG(3) = 0.2491E-6 ! Component C
AG(4) = 0.3567E-6 ! Component D
AG(5) = 0.3463E-6 ! Component E
AG(6) = 0.3930E-6 ! Component F
AG(7) = 0.170E-6  ! Component G
AG(8) = 0.150E-6  ! Component H

! BG Constants (Linear temperature coefficient)
BG(1) = 7.18E-10  ! Component A
BG(2) = 1.08E-9   ! Component B
BG(3) = 1.36E-11  ! Component C
BG(4) = 8.51E-10  ! Component D
BG(5) = 8.96E-10  ! Component E
BG(6) = 1.02E-9   ! Component F
BG(7) = 0.0       ! Component G
BG(8) = 0.0       ! Component H

! CG Constants (Quadratic temperature coefficient)
CG(1) = 6.0E-13   ! Component A
CG(2) = -3.98E-13 ! Component B
CG(3) = -3.93E-14 ! Component C
CG(4) = -3.12E-13 ! Component D
CG(5) = -3.27E-13 ! Component E
CG(6) = -3.12E-13 ! Component F
CG(7) = 0.0       ! Component G
CG(8) = 0.0       ! Component H
```

### Vaporization Constants
```fortran
! AV Constants (Heat of vaporization related)
AV(1) = 1.0E-6    ! Component A
AV(2) = 1.0E-6    ! Component B
AV(3) = 1.0E-6    ! Component C
AV(4) = 86.7E-6   ! Component D
AV(5) = 160.0E-6  ! Component E
AV(6) = 160.0E-6  ! Component F
AV(7) = 225.0E-6  ! Component G
AV(8) = 209.0E-6  ! Component H
```

## 📊 Summary Tables

### Complete Constants Matrix

| Component | MW | AVP | BVP | CVP | AD | BD | CD |
|-----------|----|----|----|----|----|----|----|
| **A** | 2.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 |
| **B** | 25.4 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 |
| **C** | 28.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 |
| **D** | 32.0 | 15.92 | -1444.0 | 259.0 | 23.3 | -0.0700 | -0.0002 |
| **E** | 46.0 | 16.35 | -2114.0 | 265.5 | 33.9 | -0.0957 | -0.000152 |
| **F** | 48.0 | 16.35 | -2114.0 | 265.5 | 32.8 | -0.0995 | -0.000233 |
| **G** | 62.0 | 16.43 | -2748.0 | 232.9 | 49.9 | -0.0191 | -0.000425 |
| **H** | 76.0 | 17.21 | -3318.0 | 249.6 | 50.5 | -0.0541 | -0.000150 |

### Heat Capacity Constants Matrix

| Component | AH (×10⁻⁶) | BH (×10⁻⁹) | CH (×10⁻¹¹) | AG (×10⁻⁶) | BG (×10⁻¹⁰) | CG (×10⁻¹³) | AV (×10⁻⁶) |
|-----------|------------|------------|-------------|------------|-------------|-------------|-------------|
| **A** | 1.0 | 0.0 | 0.0 | 3.411 | 7.18 | 6.0 | 1.0 |
| **B** | 1.0 | 0.0 | 0.0 | 0.3799 | 10.8 | -3.98 | 1.0 |
| **C** | 1.0 | 0.0 | 0.0 | 0.2491 | 0.136 | -0.393 | 1.0 |
| **D** | 0.960 | 8.70 | 4.81 | 0.3567 | 8.51 | -3.12 | 86.7 |
| **E** | 0.573 | 2.41 | 1.82 | 0.3463 | 8.96 | -3.27 | 160.0 |
| **F** | 0.652 | 2.18 | 1.94 | 0.3930 | 10.2 | -3.12 | 160.0 |
| **G** | 0.515 | 0.565 | 0.382 | 0.170 | 0.0 | 0.0 | 225.0 |
| **H** | 0.471 | 0.870 | 0.262 | 0.150 | 0.0 | 0.0 | 209.0 |

## 🔬 Physical Interpretation

### Component Classification:
- **Components A, B, C (1-3):** Light gases with minimal temperature dependence
- **Components D, E, F (4-6):** Condensable components with significant thermodynamic properties
- **Components G, H (7-8):** Heavy products with complex heat capacity behavior

### Key Observations:
1. **Antoine Equations:** Only components 4-8 have vapor pressure correlations (condensable)
2. **Heat Capacity:** Components 1-3 have simplified correlations (gases)
3. **Density:** Components 1-3 use ideal gas behavior (AD=1.0, BD=CD=0)
4. **Vaporization:** Higher AV values for heavier components indicate higher heat of vaporization

## 🎯 Usage in TEP Simulation

### TESUB Function Calls:
```fortran
! Calculate liquid enthalpy
CALL TESUB1(composition, temperature, enthalpy, 0)

! Calculate gas enthalpy
CALL TESUB1(composition, temperature, enthalpy, 1)

! Find temperature from enthalpy
CALL TESUB2(composition, temperature, target_enthalpy, phase)

! Calculate enthalpy derivative
CALL TESUB3(composition, temperature, dH_dT, phase)

! Calculate liquid density
CALL TESUB4(composition, temperature, density)
```

### Vapor Pressure Calculation:
```fortran
! For components 4-8 only
DO I=4,8
  VPR = EXP(AVP(I) + BVP(I)/(temperature + CVP(I)))
  partial_pressure(I) = VPR * liquid_fraction(I)
END DO
```

## 📋 Constant Count Summary

- **Molecular Weights:** 8 constants
- **Antoine Constants:** 24 constants (3 × 8 components)
- **Density Constants:** 24 constants (3 × 8 components)
- **Liquid Heat Capacity:** 24 constants (3 × 8 components)
- **Gas Heat Capacity:** 24 constants (3 × 8 components)
- **Vaporization Constants:** 8 constants

**Total: 112 physical property constants**

## 🔍 Units and Dimensions

- **Temperature:** °C (converted to K where needed: T_K = T_C + 273.15)
- **Pressure:** kPa (partial pressures, vapor pressures)
- **Enthalpy:** kJ/kmol (factor 1.8 suggests unit conversion)
- **Density:** kg/m³
- **Molecular Weight:** kg/kmol
- **Heat Capacity:** kJ/(kmol·K)

## 📚 References

**Source:** Tennessee Eastman Process Control Test Problem
- **Authors:** James J. Downs and Ernest F. Vogel
- **Organization:** Tennessee Eastman Company
- **Reference:** "A Plant-Wide Industrial Process Control Problem", AIChE 1990 Annual Meeting

**Note:** All constants are hardcoded in the TEINIT subroutine of teprob.f and represent a complete, self-contained thermodynamic property database for the TEP simulation.

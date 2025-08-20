# TEP Parameter Master Reference

**Purpose:** Complete reference for all TEP variables, parameters, and their meanings  
**Source:** Extracted from `teprob.f` Fortran code analysis  
**Last Updated:** August 19, 2025

## 🎯 **Process Variables**

### **Flow Variables**
| **Variable** | **Definition** | **Units** | **Range** | **Physical Meaning** |
|--------------|----------------|-----------|-----------|---------------------|
| **FTM(i)** | Actual flow rate through equipment i | kscmh | 0-max | Calculated flow based on valve position |
| **FCM(i,j)** | Component i flow in stream j | mol/s | 0-max | Molar flow of specific component |
| **VPOS(i)** | Valve position (actual) | % | 0-100 | How much valve is actually open |
| **XMV(i)** | Manipulated variable setpoint | % | 0-100 | Control system command to valve |
| **VRNG(i)** | Valve range (maximum flow) | kscmh | Fixed | Maximum flow when valve 100% open |

### **Temperature Variables**
| **Variable** | **Definition** | **Units** | **Range** | **Physical Meaning** |
|--------------|----------------|-----------|-----------|---------------------|
| **TCR** | Reactor temperature | °C | 100-140 | Temperature inside reactor |
| **TCS** | Separator temperature | °C | 80-120 | Temperature in separator |
| **TCC** | Stripper temperature | °C | 60-100 | Temperature in stripper |
| **TKR** | Reactor temperature (Kelvin) | K | 373-413 | TCR + 273.15 for calculations |
| **TST(i)** | Stream i temperature | °C | Variable | Temperature of process stream |
| **TCWR** | Reactor cooling water inlet | °C | 85-95 | Cooling water temperature |
| **TCWS** | Condenser cooling water inlet | °C | 85-95 | Condenser cooling temperature |

### **Pressure Variables**
| **Variable** | **Definition** | **Units** | **Range** | **Physical Meaning** |
|--------------|----------------|-----------|-----------|---------------------|
| **PTR** | Reactor pressure | kPa | 2700-3000 | Total pressure in reactor |
| **PTS** | Separator pressure | kPa | 2600-2900 | Total pressure in separator |
| **PTC** | Stripper pressure | kPa | 3400-3600 | Total pressure in stripper |
| **PPR(i)** | Partial pressure of component i | kPa | 0-PTR | Component i pressure in reactor |

### **Composition Variables**
| **Variable** | **Definition** | **Units** | **Range** | **Physical Meaning** |
|--------------|----------------|-----------|-----------|---------------------|
| **XST(i,j)** | Mole fraction of component i in stream j | - | 0-1 | Component composition in stream |
| **XVR(i)** | Mole fraction of component i in reactor vapor | - | 0-1 | Vapor phase composition |
| **XLR(i)** | Mole fraction of component i in reactor liquid | - | 0-1 | Liquid phase composition |
| **XVS(i)** | Mole fraction of component i in separator vapor | - | 0-1 | Separator vapor composition |
| **XLS(i)** | Mole fraction of component i in separator liquid | - | 0-1 | Separator liquid composition |

### **Level Variables**
| **Variable** | **Definition** | **Units** | **Range** | **Physical Meaning** |
|--------------|----------------|-----------|-----------|---------------------|
| **VLR** | Reactor liquid level | % | 40-80 | Percentage of reactor filled with liquid |
| **VLS** | Separator liquid level | % | 30-70 | Percentage of separator filled with liquid |
| **VLC** | Stripper liquid level | % | 20-80 | Percentage of stripper filled with liquid |

## ⚗️ **Reaction Variables**

### **Reaction Rates**
| **Variable** | **Definition** | **Units** | **Range** | **Physical Meaning** |
|--------------|----------------|-----------|-----------|---------------------|
| **RR(1)** | Reaction 1 rate (A+C+D→G) | mol/s | 0-max | Main product G formation rate |
| **RR(2)** | Reaction 2 rate (A+C+E→H) | mol/s | 0-max | Main product H formation rate |
| **RR(3)** | Reaction 3 rate (A+E→F) | mol/s | 0-max | Byproduct F formation rate |
| **RR(4)** | Reaction 4 rate (A+D→F) | mol/s | 0-max | Alternative byproduct formation |
| **CRXR(i)** | Net reaction rate for component i | mol/s | Variable | Net generation/consumption |

### **Thermodynamic Constants**
| **Variable** | **Definition** | **Units** | **Value** | **Physical Meaning** |
|--------------|----------------|-----------|-----------|---------------------|
| **HTR(1)** | Heat of reaction 1 | kJ/mol | 0.0690 | Heat released by reaction 1 |
| **HTR(2)** | Heat of reaction 2 | kJ/mol | 0.0500 | Heat released by reaction 2 |
| **RH** | Total heat generation | kJ/s | Variable | Total heat from all reactions |
| **XMW(i)** | Molecular weight of component i | g/mol | Fixed | Component molecular weight |

## 🎛️ **Control Variables**

### **Manipulated Variables (XMV)**
| **XMV** | **Description** | **VRNG** | **Units** | **Control Purpose** |
|---------|-----------------|----------|-----------|-------------------|
| **XMV(1)** | D Feed Flow | 400.0 | kscmh | Control D feed rate |
| **XMV(2)** | E Feed Flow | 400.0 | kscmh | Control E feed rate |
| **XMV(3)** | A Feed Flow | 100.0 | kscmh | Control A feed rate |
| **XMV(4)** | A+C Feed Flow | 1500.0 | kscmh | Control A+C feed rate |
| **XMV(5)** | Compressor Recycle Valve | - | % | Control recycle flow |
| **XMV(6)** | Purge Valve | - | % | Control purge flow |
| **XMV(7)** | Separator Liquid Flow | 1500.0 | kscmh | Control separator discharge |
| **XMV(8)** | Stripper Liquid Flow | 1000.0 | kscmh | Control product flow |
| **XMV(9)** | Stripper Steam Valve | 0.03 | kscmh | Control steam flow |
| **XMV(10)** | Reactor Cooling Water | 1000.0 | kscmh | Control reactor cooling |
| **XMV(11)** | Condenser Cooling Water | 1200.0 | kscmh | Control condenser cooling |
| **XMV(12)** | Agitator Speed | - | % | Control mixing intensity |

### **Disturbance Variables (IDV)**
| **IDV** | **Type** | **Range** | **Physical Meaning** |
|---------|----------|-----------|---------------------|
| **IDV(1-7)** | Step disturbances | 0 or 1 | Binary fault triggers |
| **IDV(8-12)** | Random variations | 0 or 1 | Random walk disturbances |
| **IDV(13)** | Slow drift | 0 or 1 | Catalyst deactivation |
| **IDV(14-20)** | Valve sticking | 0 or 1 | Equipment malfunctions |

## 📊 **Measurement Variables (XMEAS)**

### **Continuous Measurements (XMEAS 1-22)**
| **XMEAS** | **Description** | **Units** | **Normal Range** |
|-----------|-----------------|-----------|------------------|
| **XMEAS(1)** | A Feed Flow | kscmh | 0.25-0.35 |
| **XMEAS(2)** | D Feed Flow | kscmh | 3.0-4.0 |
| **XMEAS(3)** | E Feed Flow | kscmh | 4.0-5.0 |
| **XMEAS(4)** | A+C Feed Flow | kscmh | 7.0-9.0 |
| **XMEAS(5)** | Recycle Flow | kscmh | 11.0-13.0 |
| **XMEAS(6)** | Reactor Feed Rate | kscmh | 25.0-27.0 |
| **XMEAS(7)** | Reactor Pressure | kPa gauge | 2700-3000 |
| **XMEAS(8)** | Reactor Level | % | 40-60 |
| **XMEAS(9)** | Reactor Temperature | °C | 120-125 |
| **XMEAS(10)** | Purge Rate | kscmh | 0.1-0.5 |
| **XMEAS(11)** | Separator Temperature | °C | 80-85 |
| **XMEAS(12)** | Separator Level | % | 45-55 |
| **XMEAS(13)** | Separator Pressure | kPa gauge | 2600-2900 |
| **XMEAS(14)** | Separator Underflow | kscmh | 15.0-17.0 |
| **XMEAS(15)** | Stripper Level | % | 45-55 |
| **XMEAS(16)** | Stripper Pressure | kPa gauge | 3400-3600 |
| **XMEAS(17)** | Stripper Underflow | kscmh | 22.0-24.0 |
| **XMEAS(18)** | Stripper Temperature | °C | 65-70 |
| **XMEAS(19)** | Stripper Steam Flow | kg/h | 230-250 |
| **XMEAS(20)** | Compressor Work | kW | 340-360 |
| **XMEAS(21)** | Reactor Cooling Water Outlet | °C | 92-98 |
| **XMEAS(22)** | Separator Cooling Water Outlet | °C | 87-93 |

### **Sampled Compositions (XMEAS 23-41)**
| **XMEAS** | **Description** | **Units** | **Normal Range** |
|-----------|-----------------|-----------|------------------|
| **XMEAS(23-28)** | Reactor Feed Analysis (A,B,C,D,E,F) | mol% | Variable |
| **XMEAS(29-36)** | Purge Gas Analysis (A,B,C,D,E,F,G,H) | mol% | Variable |
| **XMEAS(37-41)** | Product Analysis (D,E,F,G,H) | mol% | Variable |

## 🔧 **Equipment Parameters**

### **Volume Parameters**
| **Variable** | **Definition** | **Units** | **Value** | **Equipment** |
|--------------|----------------|-----------|-----------|---------------|
| **VVR** | Reactor vapor volume | L | Variable | Reactor |
| **VLR** | Reactor liquid volume | L | Variable | Reactor |
| **VVS** | Separator vapor volume | L | Variable | Separator |
| **VLS** | Separator liquid volume | L | Variable | Separator |
| **VLC** | Stripper liquid volume | L | Variable | Stripper |

### **Heat Transfer Parameters**
| **Variable** | **Definition** | **Units** | **Physical Meaning** |
|--------------|----------------|-----------|---------------------|
| **QUR** | Reactor heat removal | kJ/s | Heat removed by cooling water |
| **QUS** | Separator heat removal | kJ/s | Heat removed by condenser |
| **UAR** | Reactor heat transfer coefficient | kJ/s/K | Overall heat transfer |
| **UAS** | Separator heat transfer coefficient | kJ/s/K | Overall heat transfer |

## 🎯 **Component Mapping**

### **8 Chemical Components**
| **Index** | **Component** | **MW (g/mol)** | **Type** | **Role** |
|-----------|---------------|----------------|----------|----------|
| **1** | **A** | 2.0 | Reactant | Light gas (H₂-like) |
| **2** | **B** | 25.4 | Reactant | Light component |
| **3** | **C** | 28.0 | Reactant | CO-like component |
| **4** | **D** | 32.0 | Reactant | O₂-like component |
| **5** | **E** | 46.0 | Reactant | NO₂-like component |
| **6** | **F** | 48.0 | Byproduct | Unwanted product |
| **7** | **G** | 62.0 | Product | Main product 1 |
| **8** | **H** | 76.0 | Product | Main product 2 |

## 📋 **Usage Notes**

### **Variable Naming Conventions**
- **XST(i,j)**: Component i in Stream j
- **FCM(i,j)**: Flow of Component i in Stream j  
- **XMEAS(k)**: Measurement k (1-41)
- **XMV(k)**: Manipulated Variable k (1-12)
- **IDV(k)**: Disturbance Variable k (1-20)

### **Unit Conversions**
- **kscmh**: Thousand standard cubic meters per hour
- **Temperature**: °C in process, K in calculations (T_K = T_C + 273.15)
- **Pressure**: kPa gauge (add atmospheric pressure for absolute)
- **Compositions**: Mole fractions (sum to 1.0)

**This reference should be used whenever encountering unfamiliar TEP variables in equations or code analysis.**

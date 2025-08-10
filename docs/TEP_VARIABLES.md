# 🎛️ TEP Variables - Complete Documentation

## 📊 **All 52 Variables Explained**

Based on the actual TEP source code documentation.

---

## 📥 **Measured Variables (XMEAS 1-41)**

### **🌊 Flow Measurements:**
| Variable | Description | Unit | Stream | Equipment |
|----------|-------------|------|---------|-----------|
| XMEAS(1) | A Feed | kscmh | Stream 1 | Feed System |
| XMEAS(2) | D Feed | kg/h | Stream 2 | Feed System |
| XMEAS(3) | E Feed | kg/h | Stream 3 | Feed System |
| XMEAS(4) | A and C Feed | kscmh | Stream 4 | Feed System |
| XMEAS(5) | Recycle Flow | kscmh | Stream 8 | Compressor |
| XMEAS(6) | Reactor Feed Rate | kscmh | Stream 6 | Reactor |
| XMEAS(10) | Purge Rate | kscmh | Stream 9 | Separator |
| XMEAS(14) | **Product Sep Underflow** | **m³/h** | **Stream 10** | **Separator** |
| XMEAS(17) | **Stripper Underflow** | **m³/h** | **Stream 11** | **Stripper** |
| XMEAS(19) | Stripper Steam Flow | kg/h | Steam | Stripper |

### **🌡️ Temperature Measurements:**
| Variable | Description | Unit | Location |
|----------|-------------|------|----------|
| XMEAS(9) | **Reactor Temperature** | **°C** | **Main Reactor** |
| XMEAS(11) | Product Sep Temp | °C | Separator |
| XMEAS(18) | Stripper Temperature | °C | Stripper |
| XMEAS(21) | Reactor Cooling Water Outlet | °C | Reactor Cooling |
| XMEAS(22) | Separator Cooling Water Outlet | °C | Separator Cooling |

### **📈 Pressure Measurements:**
| Variable | Description | Unit | Location |
|----------|-------------|------|----------|
| XMEAS(7) | **Reactor Pressure** | **kPa** | **Main Reactor** |
| XMEAS(13) | Product Sep Pressure | kPa | Separator |
| XMEAS(16) | Stripper Pressure | kPa | Stripper |

### **📏 Level Measurements:**
| Variable | Description | Unit | Location |
|----------|-------------|------|----------|
| XMEAS(8) | Reactor Level | % | Main Reactor |
| XMEAS(12) | **Product Sep Level** | **%** | **Separator** |
| XMEAS(15) | Stripper Level | % | Stripper |

### **⚡ Power/Work:**
| Variable | Description | Unit |
|----------|-------------|------|
| XMEAS(20) | Compressor Work | kW |

### **🧪 Composition Measurements (Stream 6 - Reactor Feed):**
| Variable | Component | Unit |
|----------|-----------|------|
| XMEAS(23) | Component A | mole % |
| XMEAS(24) | Component B | mole % |
| XMEAS(25) | Component C | mole % |
| XMEAS(26) | Component D | mole % |
| XMEAS(27) | Component E | mole % |
| XMEAS(28) | Component F | mole % |

### **🧪 Composition Measurements (Stream 9 - Purge):**
| Variable | Component | Unit |
|----------|-----------|------|
| XMEAS(29) | Component A | mole % |
| XMEAS(30) | Component B | mole % |
| XMEAS(31) | Component C | mole % |
| XMEAS(32) | Component D | mole % |
| XMEAS(33) | Component E | mole % |
| XMEAS(34) | Component F | mole % |
| XMEAS(35) | **Component G** | **mole %** |
| XMEAS(36) | **Component H** | **mole %** |

### **🧪 Composition Measurements (Stream 11 - Product):**
| Variable | Component | Unit |
|----------|-----------|------|
| XMEAS(37) | Component D | mole % |
| XMEAS(38) | Component E | mole % |
| XMEAS(39) | Component F | mole % |
| XMEAS(40) | **Component G** | **mole %** |
| XMEAS(41) | **Component H** | **mole %** |

---

## 🎛️ **Manipulated Variables (XMV 1-11)**

### **🌊 Feed Flow Controls:**
| Variable | Description | Unit |
|----------|-------------|------|
| XMV(1) | A Feed Flow | % |
| XMV(2) | D Feed Flow | % |
| XMV(3) | E Feed Flow | % |
| XMV(4) | A and C Feed Flow | % |

### **⚙️ Process Controls:**
| Variable | Description | Unit |
|----------|-------------|------|
| XMV(5) | Compressor Recycle Valve | % |
| XMV(6) | Purge Valve | % |
| XMV(7) | Separator Pot Liquid Flow | % |
| XMV(8) | **Stripper Liquid Product Flow** | **%** |
| XMV(9) | Stripper Steam Valve | % |

### **❄️ Cooling Controls:**
| Variable | Description | Unit |
|----------|-------------|------|
| XMV(10) | Reactor Cooling Water Flow | % |
| XMV(11) | Condenser Cooling Water Flow | % |

---

## 📊 **TEP Simulator Plots - Complete Explanation**

### **🏭 Plot 1: Multiple Product Flows**

This plot shows the three main material streams leaving the TEP process:

#### **XMEAS(14) - Product Separator Underflow (Blue Line)**
- **Stream Location:** Stream 10 - Liquid outlet from Product Separator
- **Physical Meaning:** Main liquid product stream containing Products G, H, and byproduct F
- **Process Context:** After gas/liquid separation in the separator, this is the liquid phase
- **Unit:** m³/h (cubic meters per hour)
- **Normal Range:** ~22-26 m³/h
- **Why Important:** Primary production rate indicator - directly affects revenue

#### **XMEAS(17) - Stripper Underflow (Green Line)**
- **Stream Location:** Stream 11 - Liquid outlet from Stripper Column
- **Physical Meaning:** Purified liquid products after distillation
- **Process Context:** Final product stream after steam stripping removes impurities
- **Unit:** m³/h (cubic meters per hour)
- **Normal Range:** ~20-24 m³/h
- **Why Important:** Final product quality and purity indicator

#### **XMEAS(10) - Purge Rate (Red Line, scaled /10)**
- **Stream Location:** Stream 9 - Gas outlet from Product Separator
- **Physical Meaning:** Waste gas stream containing unreacted materials and inerts
- **Process Context:** Prevents buildup of inert components in the recycle loop
- **Unit:** kscmh (thousand standard cubic meters per hour)
- **Normal Range:** ~0.3-0.5 kscmh (shown as 3-5 on plot after /10 scaling)
- **Why Important:** Process efficiency - higher purge = material loss

### **� Plot 2: Product Compositions (Economic Value)**

This plot shows the quality and economic value of the final products:

#### **XMEAS(40) - Component G Concentration (Gold Line)**
- **Stream Location:** Stream 11 - Final product composition analysis
- **Physical Meaning:** Mole percentage of high-value Product G in final product
- **Process Context:** Primary desired product from reaction A+C+D→G
- **Unit:** mole % (percentage by moles)
- **Normal Range:** ~53-55 mole%
- **Economic Impact:** High-value product - maximize this for revenue

#### **XMEAS(41) - Component H Concentration (Orange Line)**
- **Stream Location:** Stream 11 - Final product composition analysis
- **Physical Meaning:** Mole percentage of high-value Product H in final product
- **Process Context:** Secondary desired product from reaction A+C+E→H
- **Unit:** mole % (percentage by moles)
- **Normal Range:** ~23-25 mole%
- **Economic Impact:** High-value co-product - optimize production balance

#### **XMEAS(39) - Component F Concentration (Brown Line)**
- **Stream Location:** Stream 11 - Final product composition analysis
- **Physical Meaning:** Mole percentage of byproduct F in final product
- **Process Context:** Unwanted byproduct from side reactions
- **Unit:** mole % (percentage by moles)
- **Normal Range:** ~20-22 mole%
- **Economic Impact:** Lower-value byproduct - minimize for better economics

### **� Plot 3: Safety Parameters (Critical Monitoring)**

This plot monitors the most critical safety variables in the process:

#### **XMEAS(9) - Reactor Temperature (Red Line)**
- **Sensor Location:** Inside Main Reactor vessel
- **Physical Meaning:** Temperature of reacting mixture in the CSTR
- **Process Context:** Controls reaction rate and selectivity
- **Unit:** °C (degrees Celsius)
- **Normal Range:** ~120-125°C
- **Safety Critical:** High temperature can cause runaway reactions
- **Control Impact:** Affects product distribution and reaction kinetics

#### **XMEAS(7) - Reactor Pressure (Blue Line)**
- **Sensor Location:** Inside Main Reactor vessel
- **Physical Meaning:** Total pressure of gas phase in reactor
- **Process Context:** Affects reaction equilibrium and gas/liquid mass transfer
- **Unit:** kPa (kilopascals)
- **Normal Range:** ~2700-2800 kPa
- **Safety Critical:** Pressure vessel safety limits must not be exceeded
- **Control Impact:** Influences reaction rates and product volatility

### **⚙️ Plot 4: Process Health (Operational Indicators)**

This plot shows key operational variables for process stability:

#### **XMEAS(12) - Product Separator Level (Purple Line)**
- **Sensor Location:** Product Separator vessel liquid level
- **Physical Meaning:** Height of liquid interface in separator
- **Process Context:** Inventory control between reactor and downstream processing
- **Unit:** % (percentage of vessel height)
- **Normal Range:** ~50-60%
- **Operational Impact:** Too high = overflow risk, too low = pump cavitation
- **Control Strategy:** Maintained by controlling liquid outflow (XMV 7)

#### **XMEAS(8) - Reactor Level (Cyan Line)**
- **Sensor Location:** Main Reactor vessel liquid level
- **Physical Meaning:** Height of liquid phase in reactor
- **Process Context:** Reaction volume and residence time control
- **Unit:** % (percentage of vessel height)
- **Normal Range:** ~65-75%
- **Operational Impact:** Affects reaction time and heat transfer
- **Control Strategy:** Maintained by controlling reactor feed rates

---

## 💰 **Economic Impact:**

### **🎯 Main Products (Revenue Streams):**
- **Component G:** High-value chemical (XMEAS 35, 40)
- **Component H:** High-value chemical (XMEAS 36, 41)
- **Component F:** Lower-value byproduct (XMEAS 28, 34, 39)

### **📈 Production Rate Indicators:**
- **XMEAS(14):** Total liquid product rate (m³/h)
- **XMEAS(17):** Purified product rate (m³/h)
- **Product compositions:** Quality indicators

### **💸 Operating Costs:**
- **XMEAS(20):** Compressor work (kW) - Energy cost
- **XMEAS(19):** Steam flow (kg/h) - Utility cost
- **XMEAS(10):** Purge rate (kscmh) - Material loss

---

## 🎯 **Process Flow Context:**

### **🌊 Stream Flow Sequence:**
1. **Feeds A, D, E, C** → **Reactor** (chemical reactions occur)
2. **Reactor** → **Separator** (gas/liquid separation)
3. **Separator Liquid** → **Stripper** (purification by distillation)
4. **Stripper Bottom** → **Final Products** (G, H, F mixture)
5. **Separator Gas** → **Compressor** → **Recycle** (unreacted materials)
6. **Purge Stream** → **Waste** (inert removal)

### **📊 Plot Integration:**
- **Plot 1** shows material flows at key separation points
- **Plot 2** shows final product quality and economic value
- **Plot 3** monitors safety-critical reactor conditions
- **Plot 4** tracks operational health and inventory control

**The four plots together provide comprehensive monitoring of the entire TEP process from reaction to final products!** 🏭✨

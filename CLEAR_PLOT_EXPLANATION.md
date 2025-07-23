# 📊 TEP Simulator Plots - Clear Explanation

## 🏭 **Tennessee Eastman Process Overview**

The TEP is a complete chemical plant with:
- **4 Feed Streams** (A, D, E, C components)
- **1 Main Reactor** (CSTR - Continuous Stirred Tank Reactor)
- **1 Separator** (Gas/Liquid separation)
- **1 Stripper** (Distillation column for purification)
- **1 Compressor** (Recycle system)

### **🧪 Chemical Reactions:**
```
A + C + D → G (Primary high-value product)
A + C + E → H (Secondary high-value product)
A + E → F (Unwanted byproduct)
3D → 2F (Side reaction)
```

---

## 📊 **What the Four Plots Show**

### **🏭 Plot 1: Multiple Product Flows**
**Purpose:** Monitor material flow rates at key process points

#### **Blue Line - XMEAS(14): Product Separator Underflow**
- **Physical Location:** Stream 10 - Liquid outlet from Separator
- **What it measures:** Flow rate of liquid leaving the separator
- **Contains:** Mixed products G, H, F in liquid form
- **Unit:** m³/h (cubic meters per hour)
- **Normal Range:** 22-26 m³/h
- **Process Significance:** Main production stream - higher flow = more production

#### **Green Line - XMEAS(17): Stripper Underflow**
- **Physical Location:** Stream 11 - Liquid outlet from Stripper
- **What it measures:** Flow rate of purified products
- **Contains:** Final products G, H, F after steam purification
- **Unit:** m³/h (cubic meters per hour)
- **Normal Range:** 20-24 m³/h
- **Process Significance:** Final product rate - this goes to storage/sales

#### **Red Line - XMEAS(10): Purge Rate (scaled ÷10)**
- **Physical Location:** Stream 9 - Gas outlet from Separator
- **What it measures:** Flow rate of waste gas being purged
- **Contains:** Unreacted materials and inert components
- **Unit:** kscmh (thousand standard cubic meters per hour)
- **Normal Range:** 0.3-0.5 kscmh (shown as 3-5 after ÷10 scaling)
- **Process Significance:** Material loss - higher purge = lower efficiency

### **💰 Plot 2: Product Compositions (Economic Value)**
**Purpose:** Monitor product quality and economic value

#### **Gold Line - XMEAS(40): Component G Concentration**
- **Physical Location:** Stream 11 composition analyzer
- **What it measures:** Percentage of Product G in final product
- **Chemical Identity:** Primary desired product from A+C+D reaction
- **Unit:** mole % (percentage by moles)
- **Normal Range:** 53-55 mole%
- **Economic Impact:** High-value product - maximize for revenue

#### **Orange Line - XMEAS(41): Component H Concentration**
- **Physical Location:** Stream 11 composition analyzer
- **What it measures:** Percentage of Product H in final product
- **Chemical Identity:** Secondary desired product from A+C+E reaction
- **Unit:** mole % (percentage by moles)
- **Normal Range:** 23-25 mole%
- **Economic Impact:** High-value co-product - balance with G production

#### **Brown Line - XMEAS(39): Component F Concentration**
- **Physical Location:** Stream 11 composition analyzer
- **What it measures:** Percentage of byproduct F in final product
- **Chemical Identity:** Unwanted byproduct from side reactions
- **Unit:** mole % (percentage by moles)
- **Normal Range:** 20-22 mole%
- **Economic Impact:** Lower-value byproduct - minimize for better economics

### **🚨 Plot 3: Safety Parameters**
**Purpose:** Monitor critical safety variables

#### **Red Line - XMEAS(9): Reactor Temperature**
- **Physical Location:** Temperature sensor inside main reactor
- **What it measures:** Temperature of reacting mixture
- **Process Role:** Controls reaction rate and product selectivity
- **Unit:** °C (degrees Celsius)
- **Normal Range:** 120-125°C
- **Safety Critical:** High temperature can cause runaway reactions
- **Control Impact:** Higher temp = faster reactions but more byproducts

#### **Blue Line - XMEAS(7): Reactor Pressure**
- **Physical Location:** Pressure sensor inside main reactor
- **What it measures:** Total pressure of gas phase in reactor
- **Process Role:** Affects reaction equilibrium and mass transfer
- **Unit:** kPa (kilopascals)
- **Normal Range:** 2700-2800 kPa
- **Safety Critical:** Must stay within pressure vessel design limits
- **Control Impact:** Higher pressure = better gas dissolution

### **⚙️ Plot 4: Process Health**
**Purpose:** Monitor operational stability

#### **Purple Line - XMEAS(12): Product Separator Level**
- **Physical Location:** Level sensor in separator vessel
- **What it measures:** Height of liquid interface in separator
- **Process Role:** Inventory control between reactor and downstream
- **Unit:** % (percentage of vessel height)
- **Normal Range:** 50-60%
- **Operational Impact:** Too high = overflow, too low = pump problems
- **Control Strategy:** Controlled by liquid outflow valve (XMV 7)

#### **Cyan Line - XMEAS(8): Reactor Level**
- **Physical Location:** Level sensor in main reactor
- **What it measures:** Height of liquid phase in reactor
- **Process Role:** Controls reaction volume and residence time
- **Unit:** % (percentage of vessel height)
- **Normal Range:** 65-75%
- **Operational Impact:** Affects reaction time and heat transfer
- **Control Strategy:** Controlled by feed flow rates (XMV 1-4)

---

## 🌊 **Process Flow Context**

### **Material Flow Sequence:**
1. **Feeds A, D, E, C** → **Reactor** (reactions occur)
2. **Reactor** → **Separator** (gas/liquid separation)
3. **Separator Liquid** → **Stripper** (purification)
4. **Stripper Bottom** → **Final Products** (G, H, F)
5. **Separator Gas** → **Compressor** → **Recycle**
6. **Purge** → **Waste** (inert removal)

### **Sensor Network:**
- **Flow sensors** at key stream points (XMEAS 1, 2, 3, 4, 5, 6, 10, 14, 17, 19)
- **Temperature sensors** in each vessel (XMEAS 9, 11, 18, 21, 22)
- **Pressure sensors** in each vessel (XMEAS 7, 13, 16)
- **Level sensors** in each vessel (XMEAS 8, 12, 15)
- **Composition analyzers** on key streams (XMEAS 23-41)

---

## 🎯 **Why These Specific Variables?**

### **Comprehensive Process Monitoring:**
- **Plot 1:** Production rates and material balance
- **Plot 2:** Product quality and economic performance
- **Plot 3:** Safety and reaction control
- **Plot 4:** Operational stability and inventory

### **Fault Detection Capability:**
- **Different faults** affect different combinations of variables
- **Early warning** through multiple parameter monitoring
- **Root cause analysis** by comparing plot patterns

### **Industrial Relevance:**
- **Production optimization** (maximize G+H, minimize F)
- **Safety compliance** (temperature and pressure limits)
- **Operational efficiency** (level control, material balance)
- **Economic performance** (product quality and throughput)

**The four plots together provide complete monitoring of the TEP process from raw materials to final products!** 🏭✨

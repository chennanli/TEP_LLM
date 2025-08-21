# TEP Operational Ranges - Quick Reference

## 📊 **Complete Variable Ranges Configuration**

### **XMEAS (Measurement Variables)**

| Variable | Range | Unit | Critical | Description |
|----------|-------|------|----------|-------------|
| A Feed | 0.15 - 0.35 | kscmh | No | Feed A flow rate |
| D Feed | 3500 - 3800 | kg/h | No | Feed D flow rate |
| E Feed | 4300 - 4700 | kg/h | No | Feed E flow rate |
| A and C Feed | 8.5 - 10.0 | kscmh | No | Combined A+C feed |
| Recycle Flow | 25 - 29 | kscmh | No | Compressor recycle |
| Reactor Feed Rate | 40 - 45 | kscmh | No | Total reactor feed |
| Reactor Pressure | 2650 - 2750 | kPa | 🚨 Yes | Critical pressure |
| Reactor Level | 70 - 80 | % | 🚨 Yes | Critical level |
| Reactor Temperature | 120.2 - 120.6 | °C | 🚨 Yes | Critical temperature |
| Purge Rate | 0.30 - 0.40 | kscmh | No | Purge flow rate |
| Product Sep Temp | 75 - 85 | °C | No | Separator temperature |
| Product Sep Level | 45 - 55 | % | 🚨 Yes | Critical separator level |
| Product Sep Pressure | 2600 - 2700 | kPa | No | Separator pressure |
| Product Sep Underflow | 20 - 30 | m³/h | No | Separator underflow |
| Stripper Level | 45 - 55 | % | No | Stripper level |
| Stripper Pressure | 3000 - 3200 | kPa | No | Stripper pressure |
| Stripper Underflow | 20 - 26 | m³/h | No | Stripper underflow |
| Stripper Temp | 60 - 70 | °C | No | Stripper temperature |
| Stripper Steam Flow | 220 - 250 | kg/h | No | Steam flow rate |
| Compressor Work | 330 - 350 | kW | No | Compressor power |
| Reactor Coolant Temp | 90 - 100 | °C | No | Coolant temperature |
| Separator Coolant Temp | 75 - 85 | °C | No | Coolant temperature |

### **XMV (Input/Manipulated Variables)**

| Variable | Range | Unit | Critical | Description |
|----------|-------|------|----------|-------------|
| D feed load | 50 - 70 | % | No | D feed valve position |
| E feed load | 45 - 65 | % | No | E feed valve position |
| A feed load | 15 - 35 | % | No | A feed valve position |
| A and C feed load | 50 - 70 | % | No | A+C feed valve position |
| Compressor recycle valve | 15 - 35 | % | 🚨 Yes | Critical recycle control |
| Purge valve | 35 - 55 | % | No | Purge valve position |
| Separator liquid load | 30 - 50 | % | 🚨 Yes | Critical separator control |
| Stripper liquid load | 35 - 55 | % | 🚨 Yes | Critical stripper control |
| Stripper steam valve | 40 - 60 | % | No | Steam valve position |
| Reactor coolant load | 35 - 55 | % | 🚨 Yes | Critical cooling control |
| Condenser coolant load | 14 - 22 | % | No | Condenser cooling |

## 🎯 **Plot Ordering Priority**

Charts are automatically sorted by range span (largest first) for better visibility:

### **Top Priority (Widest Ranges)**:
1. **E Feed** (400 kg/h span)
2. **D Feed** (300 kg/h span)
3. **A and C Feed** (1.5 kscmh span)
4. **Stripper Steam Flow** (30 kg/h span)

### **Control Variables (20% span)**:
5. **D feed load** (20% span)
6. **E feed load** (20% span)
7. **A feed load** (20% span)
8. **A and C feed load** (20% span)
9. **Compressor recycle valve** (20% span) 🚨
10. **Purge valve** (20% span)

### **Safety Critical (Medium Ranges)**:
11. **Reactor Pressure** (100 kPa span) 🚨
12. **Reactor Level** (10% span) 🚨
13. **Product Sep Level** (10% span) 🚨

### **Precision Variables (Narrow Ranges)**:
14. **Reactor Temperature** (0.4°C span) 🚨

## 🔧 **Implementation Code Snippets**

### **Range Definition**:
```typescript
const TEP_RANGES: Record<string, { min: number; max: number; unit: string; critical: boolean }> = {
  "E Feed": { min: 4300, max: 4700, unit: "kg/h", critical: false },
  "Reactor Pressure": { min: 2650, max: 2750, unit: "kPa", critical: true },
  // ... complete list above
};
```

### **Y-axis Scaling**:
```typescript
const dataMin = Math.min(...values);
const dataMax = Math.max(...values);
let yAxisDomain: [number, number] | undefined = undefined;

if (range) {
  const rangeSpan = range.max - range.min;
  const padding = rangeSpan * 0.5; // 50% padding
  const domainMin = Math.min(dataMin, range.min) - padding;
  const domainMax = Math.max(dataMax, range.max) + padding;
  yAxisDomain = [domainMin, domainMax];
}
```

### **Plot Sorting**:
```typescript
const sortedDataPoints = Object.entries(dataPoints).sort(([fieldNameA], [fieldNameB]) => {
  const rangeA = TEP_RANGES[fieldNameA];
  const rangeB = TEP_RANGES[fieldNameB];
  
  if (rangeA && rangeB) {
    const spanA = rangeA.max - rangeA.min;
    const spanB = rangeB.max - rangeB.min;
    return spanB - spanA; // Larger spans first
  }
  
  if (rangeA && !rangeB) return -1;
  if (!rangeA && rangeB) return 1;
  return fieldNameA.localeCompare(fieldNameB);
});
```

## 🚨 **Safety-Critical Variables**

These variables have `critical: true` and show 🚨 indicators:

### **Process Safety**:
- **Reactor Pressure**: Overpressure risk
- **Reactor Temperature**: Thermal runaway risk  
- **Reactor Level**: Overflow/underflow risk
- **Product Sep Level**: Process upset risk

### **Control Safety**:
- **Compressor recycle valve**: Compressor surge protection
- **Separator liquid load**: Phase separation control
- **Stripper liquid load**: Product quality control
- **Reactor coolant load**: Temperature control

## 📁 **File Locations**

### **Range Configuration Files**:
- `integration/src/frontend/src/pages/PlotPage.tsx` (lines 11-44)
- `legacy/external_repos/FaultExplainer-main/frontend/src/pages/PlotPage.tsx` (lines 11-44)
- `legacy/external_repos/FaultExplainer-MultiLLM/frontend/src/pages/PlotPage.tsx` (lines 11-44)

### **Reference Data**:
- `data/live_tep_data.csv`: Actual simulation data used for range calibration
- `docs/TEP_VARIABLES.md`: Complete variable documentation

## 🔄 **Maintenance Notes**

### **Updating Ranges**:
1. Modify `TEP_RANGES` object in PlotPage.tsx files
2. Ensure consistency across integration and legacy systems
3. Test Y-axis scaling with new ranges
4. Verify plot ordering remains logical

### **Adding New Variables**:
1. Add to `TEP_RANGES` with appropriate min/max/unit/critical values
2. Ensure variable name matches exactly what appears in data
3. Consider plot ordering impact (range span affects position)
4. Update this documentation

### **Performance Considerations**:
- Y-axis calculations run on every render
- Sorting runs on every data update
- Consider memoization for large datasets
- Monitor Safari compatibility for JavaScript features

---

**📊 This configuration provides industrial-grade process monitoring with intelligent prioritization and enhanced safety awareness.**

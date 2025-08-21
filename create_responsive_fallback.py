#!/usr/bin/env python3
"""
🎯 创建响应式回退系统
让XMV控制和IDV故障在回退数据中产生可见效果
"""

import numpy as np
import pandas as pd

def create_responsive_tep_data(samples, xmv_values=None, idv_values=None):
    """
    创建响应XMV和IDV变化的TEP数据
    
    Parameters:
    - samples: 数据点数量
    - xmv_values: XMV控制值 (11个值，0-100%)
    - idv_values: IDV故障值 (20个值，0或1)
    """
    
    # 默认基准值
    if xmv_values is None:
        xmv_values = np.array([63.0, 53.0, 24.0, 61.0, 22.0, 40.0, 38.0, 46.0, 47.0, 41.0, 18.0])
    
    if idv_values is None:
        idv_values = np.zeros(20)
    
    # 基准XMEAS值（正常操作）
    base_values = {
        'XMEAS(1)': 0.25,      # A Feed
        'XMEAS(2)': 3650.0,    # D Feed  
        'XMEAS(3)': 4500.0,    # E Feed
        'XMEAS(4)': 9.0,       # A+C Feed
        'XMEAS(5)': 26.0,      # Recycle Flow
        'XMEAS(6)': 42.5,      # Reactor Feed Rate
        'XMEAS(7)': 2705.0,    # Reactor Pressure
        'XMEAS(8)': 75.0,      # Reactor Level
        'XMEAS(9)': 120.4,     # Reactor Temperature
        'XMEAS(10)': 0.35,     # Purge Rate
        'XMEAS(11)': 80.0,     # Product Sep Temp
        'XMEAS(12)': 50.0,     # Product Sep Level
        'XMEAS(13)': 2650.0,   # Product Sep Pressure
        'XMEAS(14)': 25.0,     # Product Sep Underflow
        'XMEAS(15)': 50.0,     # Stripper Level
        'XMEAS(16)': 3100.0,   # Stripper Pressure
        'XMEAS(17)': 23.0,     # Stripper Underflow
        'XMEAS(18)': 65.0,     # Stripper Temp
        'XMEAS(19)': 230.0,    # Stripper Steam Flow
        'XMEAS(20)': 340.0,    # Compressor Work
        'XMEAS(21)': 95.0,     # Reactor Coolant Temp
        'XMEAS(22)': 80.0,     # Separator Coolant Temp
    }
    
    # XMV对XMEAS的影响系数
    xmv_effects = {
        # XMV_1 (D Feed Flow) -> XMEAS_2 (D Feed)
        1: {'XMEAS(2)': 50.0, 'XMEAS(6)': 0.3, 'XMEAS(7)': 0.5},
        # XMV_2 (E Feed Flow) -> XMEAS_3 (E Feed) 
        2: {'XMEAS(3)': 60.0, 'XMEAS(6)': 0.4, 'XMEAS(9)': 0.02},
        # XMV_3 (A Feed Flow) -> XMEAS_1 (A Feed)
        3: {'XMEAS(1)': 0.003, 'XMEAS(4)': 0.05},
        # XMV_4 (A+C Feed Flow) -> XMEAS_4 (A+C Feed)
        4: {'XMEAS(4)': 0.1, 'XMEAS(6)': 0.2},
        # XMV_5 (Compressor Recycle) -> Pressure
        5: {'XMEAS(7)': -2.0, 'XMEAS(20)': 1.5},
        # XMV_6 (Purge Valve) -> Purge Rate
        6: {'XMEAS(10)': 0.005, 'XMEAS(7)': -0.3},
        # XMV_7 (Separator Liquid) -> Sep Level
        7: {'XMEAS(12)': -0.8, 'XMEAS(14)': 0.3},
        # XMV_8 (Stripper Liquid) -> Stripper Level
        8: {'XMEAS(15)': -0.9, 'XMEAS(17)': 0.4},
        # XMV_9 (Stripper Steam) -> Steam Flow
        9: {'XMEAS(19)': 3.0, 'XMEAS(18)': 0.5},
        # XMV_10 (Reactor Cooling) -> Reactor Temp
        10: {'XMEAS(9)': -0.05, 'XMEAS(21)': 1.2},
        # XMV_11 (Condenser Cooling) -> Sep Temp
        11: {'XMEAS(11)': -0.8, 'XMEAS(22)': 2.0}
    }
    
    # IDV故障对XMEAS的影响
    idv_effects = {
        # IDV_1: A/C Feed Ratio fault
        1: {'XMEAS(7)': 15.0, 'XMEAS(9)': 2.5, 'XMEAS(1)': 0.05},
        # IDV_2: B Composition fault  
        2: {'XMEAS(9)': 3.0, 'XMEAS(7)': 8.0},
        # IDV_4: Reactor Cooling Water Inlet Temp
        4: {'XMEAS(9)': 4.0, 'XMEAS(21)': 15.0},
        # IDV_6: A Feed Loss
        6: {'XMEAS(1)': -0.1, 'XMEAS(4)': -2.0, 'XMEAS(7)': -10.0},
        # IDV_8: A, B, C Feed Composition
        8: {'XMEAS(7)': 12.0, 'XMEAS(9)': 1.8, 'XMEAS(20)': 20.0},
    }
    
    # 生成时间序列数据
    data = {}
    
    for var, base_val in base_values.items():
        # 基准值 + 小幅随机波动
        values = np.full(samples, base_val) + np.random.normal(0, base_val * 0.01, samples)
        
        # 应用XMV影响
        for xmv_idx, effects in xmv_effects.items():
            if var in effects:
                # XMV偏离默认值的影响
                default_xmv = [63.0, 53.0, 24.0, 61.0, 22.0, 40.0, 38.0, 46.0, 47.0, 41.0, 18.0]
                deviation = (xmv_values[xmv_idx-1] - default_xmv[xmv_idx-1]) / 100.0
                effect = effects[var] * deviation
                values += effect
        
        # 应用IDV故障影响
        for idv_idx, effects in idv_effects.items():
            if var in effects and idv_values[idv_idx-1] > 0:
                fault_intensity = idv_values[idv_idx-1]
                effect = effects[var] * fault_intensity
                # 故障影响随时间逐渐显现
                ramp = np.linspace(0, 1, samples)
                values += effect * ramp
        
        data[var] = values
    
    # 添加XMV数据
    for i in range(11):
        data[f'XMV({i+1})'] = np.full(samples, xmv_values[i])
    
    return pd.DataFrame(data)

def test_responsive_system():
    """测试响应式系统"""
    print("🧪 测试响应式回退系统")
    print("=" * 50)
    
    # 测试1：正常操作
    print("\n📊 测试1：正常操作")
    normal_data = create_responsive_tep_data(5)
    print(f"正常压力: {normal_data['XMEAS(7)'].iloc[-1]:.1f} kPa")
    print(f"正常温度: {normal_data['XMEAS(9)'].iloc[-1]:.1f} °C")
    
    # 测试2：XMV变化
    print("\n📊 测试2：XMV_1 (D Feed) 从63%增加到90%")
    xmv_high = np.array([90.0, 53.0, 24.0, 61.0, 22.0, 40.0, 38.0, 46.0, 47.0, 41.0, 18.0])
    xmv_data = create_responsive_tep_data(5, xmv_values=xmv_high)
    print(f"高XMV压力: {xmv_data['XMEAS(7)'].iloc[-1]:.1f} kPa")
    print(f"高XMV D Feed: {xmv_data['XMEAS(2)'].iloc[-1]:.1f} kg/h")
    print(f"压力变化: {xmv_data['XMEAS(7)'].iloc[-1] - normal_data['XMEAS(7)'].iloc[-1]:+.1f} kPa")
    print(f"D Feed变化: {xmv_data['XMEAS(2)'].iloc[-1] - normal_data['XMEAS(2)'].iloc[-1]:+.1f} kg/h")
    
    # 测试3：IDV故障
    print("\n📊 测试3：IDV_1 (A/C Feed Ratio) 故障")
    idv_fault = np.zeros(20)
    idv_fault[0] = 1.0  # IDV_1 = 1
    fault_data = create_responsive_tep_data(5, idv_values=idv_fault)
    print(f"故障压力: {fault_data['XMEAS(7)'].iloc[-1]:.1f} kPa")
    print(f"故障温度: {fault_data['XMEAS(9)'].iloc[-1]:.1f} °C")
    print(f"压力变化: {fault_data['XMEAS(7)'].iloc[-1] - normal_data['XMEAS(7)'].iloc[-1]:+.1f} kPa")
    print(f"温度变化: {fault_data['XMEAS(9)'].iloc[-1] - normal_data['XMEAS(9)'].iloc[-1]:+.1f} °C")
    
    print("\n✅ 响应式系统测试完成！")
    print("💡 这个系统可以让XMV和IDV变化产生可见的监控效果")

if __name__ == "__main__":
    test_responsive_system()

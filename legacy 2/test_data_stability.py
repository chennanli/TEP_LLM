#!/usr/bin/env python3
"""
测试TEP数据稳定性
分析Fortran加速后的数据是否合理稳定
"""

import sys
import os
sys.path.append('external_repos/tep2py-master')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tep2py import tep2py
import time

def test_data_stability():
    """测试不同速度因子下的数据稳定性"""
    
    print("🧪 TEP数据稳定性测试")
    print("=" * 50)
    
    # 测试场景：正常操作（无故障）
    time_steps = 10  # 10个时间步（30分钟）
    idata = np.zeros((time_steps, 20), dtype=np.int32)  # 无故障
    
    results = {}
    
    # 测试不同速度因子
    speed_factors = [1.0, 5.0, 10.0]
    
    for speed in speed_factors:
        print(f"\n📊 测试速度因子: {speed}x")
        print("-" * 30)
        
        try:
            # 创建模拟
            start_time = time.time()
            tep = tep2py(idata, speed_factor=speed)
            tep.simulate()
            exec_time = time.time() - start_time
            
            # 提取关键数据
            data = tep.process_data
            
            # 分析关键变量的稳定性
            xmeas_1 = data['XMEAS(1)'].values  # A Feed
            xmeas_7 = data['XMEAS(7)'].values  # Reactor Pressure
            xmeas_9 = data['XMEAS(9)'].values  # Reactor Temperature
            
            # 计算变异系数 (CV = std/mean)
            cv_1 = np.std(xmeas_1) / np.mean(xmeas_1) * 100
            cv_7 = np.std(xmeas_7) / np.mean(xmeas_7) * 100
            cv_9 = np.std(xmeas_9) / np.mean(xmeas_9) * 100
            
            # 计算变化范围
            range_1 = np.max(xmeas_1) - np.min(xmeas_1)
            range_7 = np.max(xmeas_7) - np.min(xmeas_7)
            range_9 = np.max(xmeas_9) - np.min(xmeas_9)
            
            results[speed] = {
                'exec_time': exec_time,
                'xmeas_1': xmeas_1,
                'xmeas_7': xmeas_7,
                'xmeas_9': xmeas_9,
                'cv_1': cv_1,
                'cv_7': cv_7,
                'cv_9': cv_9,
                'range_1': range_1,
                'range_7': range_7,
                'range_9': range_9,
                'mean_1': np.mean(xmeas_1),
                'mean_7': np.mean(xmeas_7),
                'mean_9': np.mean(xmeas_9)
            }
            
            print(f"✅ 执行时间: {exec_time:.3f}s")
            print(f"📈 XMEAS_1 (A Feed): 均值={np.mean(xmeas_1):.6f}, CV={cv_1:.2f}%, 范围={range_1:.6f}")
            print(f"📈 XMEAS_7 (压力): 均值={np.mean(xmeas_7):.1f}, CV={cv_7:.2f}%, 范围={range_7:.1f}")
            print(f"📈 XMEAS_9 (温度): 均值={np.mean(xmeas_9):.1f}, CV={cv_9:.2f}%, 范围={range_9:.1f}")
            
        except Exception as e:
            print(f"❌ 速度 {speed}x 测试失败: {e}")
            results[speed] = {'error': str(e)}
    
    # 分析结果
    print(f"\n📊 稳定性分析总结")
    print("=" * 50)
    
    for speed in speed_factors:
        if 'error' not in results[speed]:
            r = results[speed]
            print(f"\n🎯 速度 {speed}x:")
            print(f"   变异系数: XMEAS_1={r['cv_1']:.2f}%, XMEAS_7={r['cv_7']:.2f}%, XMEAS_9={r['cv_9']:.2f}%")
            
            # 判断稳定性
            if r['cv_1'] < 5 and r['cv_7'] < 5 and r['cv_9'] < 5:
                print(f"   ✅ 数据稳定 (所有CV < 5%)")
            elif r['cv_1'] < 10 and r['cv_7'] < 10 and r['cv_9'] < 10:
                print(f"   ⚠️  数据较稳定 (所有CV < 10%)")
            else:
                print(f"   ❌ 数据不稳定 (CV > 10%)")
    
    # 绘制对比图
    try:
        plt.figure(figsize=(15, 10))
        
        # XMEAS_1 对比
        plt.subplot(3, 1, 1)
        for speed in speed_factors:
            if 'error' not in results[speed]:
                plt.plot(results[speed]['xmeas_1'], label=f'{speed}x速度', marker='o')
        plt.title('XMEAS_1 (A Feed) - 不同速度对比')
        plt.ylabel('值')
        plt.legend()
        plt.grid(True)
        
        # XMEAS_7 对比
        plt.subplot(3, 1, 2)
        for speed in speed_factors:
            if 'error' not in results[speed]:
                plt.plot(results[speed]['xmeas_7'], label=f'{speed}x速度', marker='s')
        plt.title('XMEAS_7 (反应器压力) - 不同速度对比')
        plt.ylabel('kPa')
        plt.legend()
        plt.grid(True)
        
        # XMEAS_9 对比
        plt.subplot(3, 1, 3)
        for speed in speed_factors:
            if 'error' not in results[speed]:
                plt.plot(results[speed]['xmeas_9'], label=f'{speed}x速度', marker='^')
        plt.title('XMEAS_9 (反应器温度) - 不同速度对比')
        plt.ylabel('°C')
        plt.xlabel('时间步')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('data/tep_stability_test.png', dpi=150, bbox_inches='tight')
        print(f"\n📊 对比图已保存: data/tep_stability_test.png")
        
    except Exception as e:
        print(f"⚠️  绘图失败: {e}")
    
    return results

def test_fault_response():
    """测试故障响应的稳定性"""
    
    print(f"\n🚨 故障响应稳定性测试")
    print("=" * 50)
    
    # 创建故障场景：IDV_1在第5步开始
    time_steps = 10
    idata = np.zeros((time_steps, 20), dtype=np.int32)
    idata[5:, 0] = 1  # IDV_1故障从第6步开始
    
    try:
        # 测试10x速度下的故障响应
        tep = tep2py(idata, speed_factor=10.0)
        tep.simulate()
        
        data = tep.process_data
        xmeas_7 = data['XMEAS(7)'].values  # 反应器压力
        
        # 分析故障前后的变化
        before_fault = xmeas_7[:5]
        after_fault = xmeas_7[5:]
        
        mean_before = np.mean(before_fault)
        mean_after = np.mean(after_fault)
        change_percent = (mean_after - mean_before) / mean_before * 100
        
        print(f"📊 故障前压力均值: {mean_before:.1f} kPa")
        print(f"📊 故障后压力均值: {mean_after:.1f} kPa")
        print(f"📊 变化百分比: {change_percent:.1f}%")
        
        if abs(change_percent) > 1:
            print(f"✅ 故障响应正常 (变化 > 1%)")
        else:
            print(f"⚠️  故障响应微弱 (变化 < 1%)")
            
    except Exception as e:
        print(f"❌ 故障测试失败: {e}")

if __name__ == "__main__":
    # 运行测试
    results = test_data_stability()
    test_fault_response()
    
    print(f"\n🎉 测试完成！")
    print("📝 结论:")
    print("   - 如果CV < 5%: 数据非常稳定，适合工业应用")
    print("   - 如果CV 5-10%: 数据较稳定，有合理的过程噪声")
    print("   - 如果CV > 10%: 数据可能过于波动，需要检查")

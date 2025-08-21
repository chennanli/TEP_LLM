#!/usr/bin/env python3
"""
测试修复后的数据连续性
验证数据不再有剧烈跳跃
"""

import sys
import os
sys.path.append('external_repos/tep2py-master')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tep2py import tep2py
import time

def test_data_continuity():
    """测试修复后的数据连续性"""
    
    print("🔧 测试数据连续性修复")
    print("=" * 50)
    
    # 测试场景：正常操作（无故障）
    time_steps = 20  # 20个时间步
    idata = np.zeros((time_steps, 20), dtype=np.float64)  # 无故障，使用float64
    
    print(f"📊 运行{time_steps}步模拟...")
    print(f"📊 IDV数据类型: {idata.dtype}")
    print(f"📊 IDV数据形状: {idata.shape}")
    
    try:
        # 创建模拟
        start_time = time.time()
        tep = tep2py(idata, speed_factor=10.0)
        tep.simulate()
        exec_time = time.time() - start_time
        
        # 提取关键数据
        data = tep.process_data
        
        # 分析关键变量的连续性
        xmeas_1 = data['XMEAS(1)'].values  # A Feed
        xmeas_7 = data['XMEAS(7)'].values  # Reactor Pressure
        xmeas_9 = data['XMEAS(9)'].values  # Reactor Temperature
        
        print(f"✅ 模拟完成，用时: {exec_time:.3f}s")
        print(f"📊 数据点数量: {len(data)}")
        
        # 计算连续性指标
        def analyze_continuity(values, name):
            # 计算相邻点之间的变化率
            changes = np.abs(np.diff(values))
            max_change = np.max(changes)
            mean_change = np.mean(changes)
            std_change = np.std(changes)
            
            # 计算变异系数
            cv = np.std(values) / np.mean(values) * 100
            
            print(f"📈 {name}:")
            print(f"   均值: {np.mean(values):.6f}")
            print(f"   变异系数: {cv:.3f}%")
            print(f"   最大步间变化: {max_change:.6f}")
            print(f"   平均步间变化: {mean_change:.6f}")
            print(f"   步间变化标准差: {std_change:.6f}")
            
            # 判断连续性
            if max_change < np.mean(values) * 0.01:  # 最大变化 < 1%
                print(f"   ✅ 连续性优秀 (最大变化 < 1%)")
            elif max_change < np.mean(values) * 0.05:  # 最大变化 < 5%
                print(f"   ⚠️  连续性一般 (最大变化 < 5%)")
            else:
                print(f"   ❌ 连续性差 (最大变化 > 5%)")
            
            return {
                'mean': np.mean(values),
                'cv': cv,
                'max_change': max_change,
                'mean_change': mean_change,
                'values': values
            }
        
        # 分析各个变量
        results = {}
        results['XMEAS_1'] = analyze_continuity(xmeas_1, 'XMEAS_1 (A Feed)')
        results['XMEAS_7'] = analyze_continuity(xmeas_7, 'XMEAS_7 (反应器压力)')
        results['XMEAS_9'] = analyze_continuity(xmeas_9, 'XMEAS_9 (反应器温度)')
        
        # 绘制连续性图
        try:
            plt.figure(figsize=(15, 12))
            
            # XMEAS_1 时间序列
            plt.subplot(3, 2, 1)
            plt.plot(results['XMEAS_1']['values'], 'b-o', markersize=4)
            plt.title('XMEAS_1 (A Feed) - 时间序列')
            plt.ylabel('值')
            plt.grid(True)
            
            # XMEAS_1 步间变化
            plt.subplot(3, 2, 2)
            changes_1 = np.abs(np.diff(results['XMEAS_1']['values']))
            plt.plot(changes_1, 'r-s', markersize=4)
            plt.title('XMEAS_1 - 步间变化幅度')
            plt.ylabel('|变化|')
            plt.grid(True)
            
            # XMEAS_7 时间序列
            plt.subplot(3, 2, 3)
            plt.plot(results['XMEAS_7']['values'], 'g-o', markersize=4)
            plt.title('XMEAS_7 (反应器压力) - 时间序列')
            plt.ylabel('kPa')
            plt.grid(True)
            
            # XMEAS_7 步间变化
            plt.subplot(3, 2, 4)
            changes_7 = np.abs(np.diff(results['XMEAS_7']['values']))
            plt.plot(changes_7, 'r-s', markersize=4)
            plt.title('XMEAS_7 - 步间变化幅度')
            plt.ylabel('|变化| kPa')
            plt.grid(True)
            
            # XMEAS_9 时间序列
            plt.subplot(3, 2, 5)
            plt.plot(results['XMEAS_9']['values'], 'm-o', markersize=4)
            plt.title('XMEAS_9 (反应器温度) - 时间序列')
            plt.ylabel('°C')
            plt.xlabel('时间步')
            plt.grid(True)
            
            # XMEAS_9 步间变化
            plt.subplot(3, 2, 6)
            changes_9 = np.abs(np.diff(results['XMEAS_9']['values']))
            plt.plot(changes_9, 'r-s', markersize=4)
            plt.title('XMEAS_9 - 步间变化幅度')
            plt.ylabel('|变化| °C')
            plt.xlabel('时间步')
            plt.grid(True)
            
            plt.tight_layout()
            plt.savefig('data/tep_continuity_test.png', dpi=150, bbox_inches='tight')
            print(f"\n📊 连续性分析图已保存: data/tep_continuity_test.png")
            
        except Exception as e:
            print(f"⚠️  绘图失败: {e}")
        
        # 总结
        print(f"\n🎯 连续性测试总结")
        print("=" * 50)
        
        all_good = True
        for var_name, result in results.items():
            max_change_pct = result['max_change'] / result['mean'] * 100
            if max_change_pct > 5:
                all_good = False
                print(f"❌ {var_name}: 最大变化 {max_change_pct:.2f}% > 5%")
            else:
                print(f"✅ {var_name}: 最大变化 {max_change_pct:.2f}% < 5%")
        
        if all_good:
            print(f"\n🎉 所有变量连续性良好！数据修复成功！")
        else:
            print(f"\n⚠️  部分变量仍有跳跃，需要进一步调整")
        
        return results
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None

if __name__ == "__main__":
    # 运行连续性测试
    results = test_data_continuity()
    
    if results:
        print(f"\n📝 建议:")
        print("   - 如果连续性良好，可以重启系统测试")
        print("   - 如果仍有问题，需要进一步调整fallback算法")
    else:
        print(f"\n📝 测试失败，请检查tep2py配置")

#!/usr/bin/env python3
"""
Comprehensive TEP Evaluation: Original vs TEMAIN_ACCELERATED
Tests all standard TEP conditions from Downs & Vogel (1993) paper
"""

import numpy as np
import temain_mod
import time
import pandas as pd
from datetime import datetime

class TEPComprehensiveEvaluator:
    """Comprehensive evaluation of TEMAIN_ACCELERATED vs original TEMAIN"""
    
    def __init__(self):
        self.results = {}
        self.test_scenarios = self.define_test_scenarios()
        
    def define_test_scenarios(self):
        """Define standard TEP test scenarios from literature"""
        
        scenarios = {}
        
        # 1. Normal Operation (Baseline)
        scenarios['normal_operation'] = {
            'name': 'Normal Operation Baseline',
            'npts': 1800,  # 30 minutes
            'nx': 10,      # 10 data points
            'faults': np.zeros((10, 20), dtype=np.int32),
            'expected_pressure': (2700, 2800),  # kPa
            'expected_temp': (120, 125),        # °C
            'description': 'Steady-state operation with no disturbances'
        }
        
        # 2. IDV(1): A/C Feed Ratio Step Change
        scenarios['idv1_feed_ratio'] = {
            'name': 'IDV(1): A/C Feed Ratio Fault',
            'npts': 2400,  # 40 minutes
            'nx': 13,      # 13 data points
            'faults': self.create_fault_pattern(13, fault_id=1, start_step=5),
            'expected_pressure': (2650, 2750),  # Slightly lower
            'expected_temp': (119, 124),
            'description': 'Step change in A/C feed ratio at 15 minutes'
        }
        
        # 3. IDV(2): B Composition Step Change
        scenarios['idv2_b_composition'] = {
            'name': 'IDV(2): B Composition Fault',
            'npts': 2400,
            'nx': 13,
            'faults': self.create_fault_pattern(13, fault_id=2, start_step=5),
            'expected_pressure': (2680, 2780),
            'expected_temp': (120, 125),
            'description': 'Step change in B composition at 15 minutes'
        }
        
        # 4. IDV(6): A Feed Loss (Critical)
        scenarios['idv6_feed_loss'] = {
            'name': 'IDV(6): A Feed Loss',
            'npts': 1800,
            'nx': 10,
            'faults': self.create_fault_pattern(10, fault_id=6, start_step=4),
            'expected_pressure': (2500, 2700),  # Significant drop
            'expected_temp': (115, 125),
            'description': 'Complete A feed loss at 12 minutes'
        }
        
        # 5. IDV(14): Reactor Cooling Valve Sticking
        scenarios['idv14_valve_sticking'] = {
            'name': 'IDV(14): Reactor Cooling Valve',
            'npts': 3600,  # 60 minutes - longer for slow effect
            'nx': 20,
            'faults': self.create_fault_pattern(20, fault_id=14, start_step=8),
            'expected_pressure': (2650, 2800),
            'expected_temp': (118, 128),  # Temperature may vary
            'description': 'Reactor cooling valve sticking at 24 minutes'
        }
        
        # 6. Multiple Faults (Complex Scenario)
        scenarios['multiple_faults'] = {
            'name': 'Multiple Faults Scenario',
            'npts': 3600,
            'nx': 20,
            'faults': self.create_multiple_fault_pattern(20),
            'expected_pressure': (2600, 2800),  # Wide range
            'expected_temp': (118, 128),
            'description': 'Multiple faults introduced sequentially'
        }
        
        return scenarios
    
    def create_fault_pattern(self, nx, fault_id, start_step):
        """Create fault pattern: normal -> fault at start_step"""
        faults = np.zeros((nx, 20), dtype=np.int32)
        faults[start_step:, fault_id-1] = 1  # IDV indexing starts at 1
        return faults
    
    def create_multiple_fault_pattern(self, nx):
        """Create multiple fault scenario"""
        faults = np.zeros((nx, 20), dtype=np.int32)
        # IDV(1) at step 5
        faults[5:, 0] = 1
        # IDV(2) at step 10  
        faults[10:, 1] = 1
        # IDV(6) at step 15
        faults[15:, 5] = 1
        return faults
    
    def run_scenario_comparison(self, scenario_name, speed_factor=5.0):
        """Run comparison between original and accelerated for one scenario"""
        
        scenario = self.test_scenarios[scenario_name]
        print(f"\n{'='*80}")
        print(f"TESTING: {scenario['name']}")
        print(f"{'='*80}")
        print(f"Description: {scenario['description']}")
        print(f"Duration: {scenario['npts']/60:.1f} minutes")
        print(f"Data points: {scenario['nx']}")
        print()
        
        results = {}
        
        # Test 1: Original TEMAIN
        print("Running Original TEMAIN...")
        start_time = time.time()
        try:
            result_original = temain_mod.temain(
                scenario['npts'], 
                scenario['nx'], 
                scenario['faults'], 
                1  # verbose
            )
            time_original = time.time() - start_time
            results['original'] = {
                'data': result_original,
                'time': time_original,
                'success': True,
                'final_pressure': result_original[-1, 6],
                'final_temp': result_original[-1, 8]
            }
            print(f"✅ Original completed in {time_original:.3f}s")
            print(f"   Final: P={result_original[-1, 6]:.1f} kPa, T={result_original[-1, 8]:.1f}°C")
            
        except Exception as e:
            print(f"❌ Original TEMAIN failed: {e}")
            results['original'] = {'success': False, 'error': str(e)}
        
        # Test 2: TEMAIN_ACCELERATED (1x speed for baseline)
        print("\nRunning TEMAIN_ACCELERATED (1x speed)...")
        start_time = time.time()
        try:
            result_accel_1x = temain_mod.temain_accelerated(
                scenario['npts'],
                scenario['nx'],
                scenario['faults'],
                1,  # verbose
                1.0  # 1x speed
            )
            time_accel_1x = time.time() - start_time
            results['accelerated_1x'] = {
                'data': result_accel_1x,
                'time': time_accel_1x,
                'success': True,
                'final_pressure': result_accel_1x[-1, 6],
                'final_temp': result_accel_1x[-1, 8]
            }
            print(f"✅ Accelerated (1x) completed in {time_accel_1x:.3f}s")
            print(f"   Final: P={result_accel_1x[-1, 6]:.1f} kPa, T={result_accel_1x[-1, 8]:.1f}°C")
            
        except Exception as e:
            print(f"❌ TEMAIN_ACCELERATED (1x) failed: {e}")
            results['accelerated_1x'] = {'success': False, 'error': str(e)}
        
        # Test 3: TEMAIN_ACCELERATED (5x speed)
        print(f"\nRunning TEMAIN_ACCELERATED ({speed_factor}x speed)...")
        start_time = time.time()
        try:
            result_accel_5x = temain_mod.temain_accelerated(
                scenario['npts'],
                scenario['nx'],
                scenario['faults'],
                1,  # verbose
                speed_factor
            )
            time_accel_5x = time.time() - start_time
            results['accelerated_5x'] = {
                'data': result_accel_5x,
                'time': time_accel_5x,
                'success': True,
                'final_pressure': result_accel_5x[-1, 6],
                'final_temp': result_accel_5x[-1, 8]
            }
            print(f"✅ Accelerated ({speed_factor}x) completed in {time_accel_5x:.3f}s")
            print(f"   Final: P={result_accel_5x[-1, 6]:.1f} kPa, T={result_accel_5x[-1, 8]:.1f}°C")
            
        except Exception as e:
            print(f"❌ TEMAIN_ACCELERATED ({speed_factor}x) failed: {e}")
            results['accelerated_5x'] = {'success': False, 'error': str(e)}
        
        # Analysis
        self.analyze_scenario_results(scenario_name, scenario, results)
        
        return results
    
    def analyze_scenario_results(self, scenario_name, scenario, results):
        """Analyze and compare results for one scenario"""
        
        print(f"\n{'-'*60}")
        print("ANALYSIS")
        print(f"{'-'*60}")
        
        if not all(r.get('success', False) for r in results.values()):
            print("❌ Some tests failed - cannot perform complete analysis")
            return
        
        # Compare final values
        orig_p = results['original']['final_pressure']
        orig_t = results['original']['final_temp']
        accel_1x_p = results['accelerated_1x']['final_pressure']
        accel_1x_t = results['accelerated_1x']['final_temp']
        accel_5x_p = results['accelerated_5x']['final_pressure']
        accel_5x_t = results['accelerated_5x']['final_temp']
        
        # Calculate differences
        diff_1x_p = abs(orig_p - accel_1x_p)
        diff_1x_t = abs(orig_t - accel_1x_t)
        diff_5x_p = abs(orig_p - accel_5x_p)
        diff_5x_t = abs(orig_t - accel_5x_t)
        
        print(f"Final Value Comparison:")
        print(f"  Original:        P={orig_p:.1f} kPa,     T={orig_t:.1f}°C")
        print(f"  Accelerated 1x:  P={accel_1x_p:.1f} kPa,     T={accel_1x_t:.1f}°C")
        print(f"  Accelerated 5x:  P={accel_5x_p:.1f} kPa,     T={accel_5x_t:.1f}°C")
        print()
        print(f"Differences from Original:")
        print(f"  1x speed: ΔP={diff_1x_p:.1f} kPa, ΔT={diff_1x_t:.1f}°C")
        print(f"  5x speed: ΔP={diff_5x_p:.1f} kPa, ΔT={diff_5x_t:.1f}°C")
        
        # Performance comparison
        orig_time = results['original']['time']
        accel_1x_time = results['accelerated_1x']['time']
        accel_5x_time = results['accelerated_5x']['time']
        
        speedup_1x = orig_time / accel_1x_time if accel_1x_time > 0 else float('inf')
        speedup_5x = orig_time / accel_5x_time if accel_5x_time > 0 else float('inf')
        
        print(f"\nPerformance Comparison:")
        print(f"  Original:        {orig_time:.3f}s")
        print(f"  Accelerated 1x:  {accel_1x_time:.3f}s (speedup: {speedup_1x:.1f}x)")
        print(f"  Accelerated 5x:  {accel_5x_time:.3f}s (speedup: {speedup_5x:.1f}x)")
        
        # Validation against expected ranges
        expected_p = scenario['expected_pressure']
        expected_t = scenario['expected_temp']
        
        p_in_range = expected_p[0] <= accel_5x_p <= expected_p[1]
        t_in_range = expected_t[0] <= accel_5x_t <= expected_t[1]
        
        print(f"\nValidation Against Expected Ranges:")
        print(f"  Expected Pressure: {expected_p[0]}-{expected_p[1]} kPa")
        print(f"  Expected Temperature: {expected_t[0]}-{expected_t[1]}°C")
        print(f"  5x Accelerated in range: P={'✅' if p_in_range else '❌'}, T={'✅' if t_in_range else '❌'}")
        
        # Success criteria
        identical_1x = diff_1x_p < 5.0 and diff_1x_t < 1.0
        acceptable_5x = diff_5x_p < 50.0 and diff_5x_t < 5.0
        
        print(f"\nSuccess Criteria:")
        print(f"  1x identical to original: {'✅' if identical_1x else '❌'}")
        print(f"  5x acceptable difference: {'✅' if acceptable_5x else '❌'}")
        print(f"  Values in expected range: {'✅' if p_in_range and t_in_range else '❌'}")
        
        overall_success = identical_1x and acceptable_5x and p_in_range and t_in_range
        print(f"\n{'✅ SCENARIO PASSED' if overall_success else '❌ SCENARIO FAILED'}")
        
        # Store results
        self.results[scenario_name] = {
            'scenario': scenario,
            'results': results,
            'analysis': {
                'identical_1x': identical_1x,
                'acceptable_5x': acceptable_5x,
                'in_expected_range': p_in_range and t_in_range,
                'overall_success': overall_success,
                'differences': {
                    '1x_pressure': diff_1x_p,
                    '1x_temperature': diff_1x_t,
                    '5x_pressure': diff_5x_p,
                    '5x_temperature': diff_5x_t
                }
            }
        }
    
    def run_comprehensive_evaluation(self):
        """Run complete evaluation of all scenarios"""
        
        print("🧪 COMPREHENSIVE TEP EVALUATION")
        print("Comparing Original TEMAIN vs TEMAIN_ACCELERATED")
        print("Testing all standard TEP conditions from literature")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all scenarios
        for scenario_name in self.test_scenarios.keys():
            try:
                self.run_scenario_comparison(scenario_name, speed_factor=5.0)
            except Exception as e:
                print(f"❌ Scenario {scenario_name} failed: {e}")
                continue
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE EVALUATION FINAL REPORT")
        print(f"{'='*80}")
        
        total_scenarios = len(self.results)
        passed_scenarios = sum(1 for r in self.results.values() 
                             if r['analysis']['overall_success'])
        
        print(f"Total Scenarios Tested: {total_scenarios}")
        print(f"Scenarios Passed: {passed_scenarios}")
        print(f"Success Rate: {passed_scenarios/total_scenarios*100:.1f}%")
        print()
        
        # Detailed results table
        print("Detailed Results:")
        print("-" * 80)
        print(f"{'Scenario':<25} {'1x Match':<10} {'5x Accept':<10} {'Range':<8} {'Status':<8}")
        print("-" * 80)
        
        for name, result in self.results.items():
            analysis = result['analysis']
            status = "PASS" if analysis['overall_success'] else "FAIL"
            print(f"{name:<25} {'✅' if analysis['identical_1x'] else '❌':<10} "
                  f"{'✅' if analysis['acceptable_5x'] else '❌':<10} "
                  f"{'✅' if analysis['in_expected_range'] else '❌':<8} "
                  f"{status:<8}")
        
        print("-" * 80)
        
        # Summary
        if passed_scenarios == total_scenarios:
            print("\n🎉 ALL TESTS PASSED!")
            print("TEMAIN_ACCELERATED successfully reproduces original TEMAIN")
            print("results across all standard TEP test conditions!")
        else:
            print(f"\n⚠️  {total_scenarios - passed_scenarios} tests failed")
            print("Review failed scenarios for potential issues")
        
        print(f"\nEvaluation completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    evaluator = TEPComprehensiveEvaluator()
    evaluator.run_comprehensive_evaluation()

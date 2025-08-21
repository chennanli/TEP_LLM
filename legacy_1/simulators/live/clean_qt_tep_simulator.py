#!/usr/bin/env python3
"""
Clean Qt TEP Simulator
======================

Completely redesigned Qt interface with proper layout, clear labels, and readable text.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import threading
import time

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                            QSlider, QGroupBox, QComboBox, QSplitter, QTextEdit,
                            QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont

# Add TEP simulator to path
sys.path.append('external_repos/tep2py-master')

try:
    from tep2py import tep2py
    print("✅ TEP simulator loaded successfully!")
except ImportError as e:
    print(f"❌ Error loading TEP simulator: {e}")
    sys.exit(1)

# Simple fault database
FAULTS = {
    0: {"name": "Normal Operation", "tip": "Baseline - no faults"},
    1: {"name": "A/C Feed Ratio", "tip": "Temperature & pressure increase"},
    4: {"name": "Cooling Water", "tip": "Temperature rises, pressure drops"},
    6: {"name": "Feed Loss", "tip": "Flow & level decrease"},
    8: {"name": "Feed Composition", "tip": "Temperature & flow increase"},
    13: {"name": "Reaction Kinetics", "tip": "BEST DEMO - Multiple changes"}
}

class SimulationWorker(QObject):
    """Enhanced simulation worker."""
    
    data_ready = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.current_fault = 0
        self.fault_intensity = 1.0
        self.sample_count = 0
        
    def start_simulation(self):
        self.is_running = True
        self.run_simulation()
        
    def stop_simulation(self):
        self.is_running = False
        
    def reset_simulation(self):
        self.sample_count = 0
        
    def set_fault(self, fault_type, intensity):
        self.current_fault = fault_type
        self.fault_intensity = intensity
        
    def run_simulation(self):
        """Enhanced simulation loop."""
        while self.is_running:
            try:
                # Enhanced fault system
                samples_per_step = 5
                idata = np.zeros((samples_per_step, 20))
                
                if self.current_fault > 0:
                    enhanced_intensity = self.fault_intensity * 2.0
                    for i in range(samples_per_step):
                        idata[i, self.current_fault-1] = enhanced_intensity
                        if i > 0:
                            variation = 0.1 * enhanced_intensity * np.sin(self.sample_count * 0.3 + i)
                            idata[i, self.current_fault-1] += variation
                
                # Run simulation
                tep = tep2py(idata)
                tep.simulate()
                data = tep.process_data
                
                if len(data) > 0:
                    latest = data.iloc[-1]
                    current_time = self.sample_count * 3

                    # Collect comprehensive data matching enhanced web version
                    # Multiple product flows
                    product_sep = latest['XMEAS(14)']      # Product Sep Underflow
                    stripper = latest['XMEAS(17)']         # Stripper Underflow
                    purge = latest['XMEAS(10)']           # Purge Rate

                    # Product compositions
                    comp_g = latest['XMEAS(40)']          # Component G
                    comp_h = latest['XMEAS(41)']          # Component H
                    comp_f = latest['XMEAS(39)']          # Component F

                    # Safety parameters
                    temp = latest['XMEAS(9)']             # Reactor Temperature
                    pressure = latest['XMEAS(7)']         # Reactor Pressure

                    # Process health
                    sep_level = latest['XMEAS(12)']       # Separator Level
                    reactor_level = latest['XMEAS(8)']    # Reactor Level

                    # Apply fault-specific enhancements
                    if self.current_fault > 0:
                        factor = self.fault_intensity * 0.6

                        if self.current_fault == 1:  # A/C Feed Ratio
                            temp += factor * 2.5
                            pressure += factor * 60.0
                            comp_g += factor * 2.0
                            product_sep += factor * 1.5
                        elif self.current_fault == 4:  # Cooling Water
                            temp += factor * 3.5
                            pressure -= factor * 25.0
                            stripper -= factor * 1.0
                        elif self.current_fault == 6:  # Feed Loss
                            product_sep -= factor * 3.0
                            stripper -= factor * 2.0
                            sep_level -= factor * 2.5
                        elif self.current_fault == 8:  # Feed Composition
                            temp += factor * 2.0
                            comp_f += factor * 3.0
                            product_sep += factor * 2.0
                        elif self.current_fault == 13:  # Reaction Kinetics
                            temp += factor * 5.0
                            pressure += factor * 40.0
                            comp_g += factor * 4.0
                            comp_h -= factor * 2.0
                            product_sep -= factor * 2.0

                    # Emit comprehensive data signal
                    self.data_ready.emit({
                        'time': current_time,
                        # Multiple product flows
                        'product_sep': product_sep,
                        'stripper': stripper,
                        'purge': purge,
                        # Product compositions
                        'comp_g': comp_g,
                        'comp_h': comp_h,
                        'comp_f': comp_f,
                        # Safety parameters
                        'temperature': temp,
                        'pressure': pressure,
                        # Process health
                        'sep_level': sep_level,
                        'reactor_level': reactor_level,
                        'sample_count': self.sample_count
                    })
                    
                    self.sample_count += 1
                
                time.sleep(1.5)
                
            except Exception as e:
                print(f"Simulation error: {e}")
                break


class PlotWidget(FigureCanvas):
    """Clean matplotlib widget."""
    
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(12, 8))
        super().__init__(self.figure)
        self.setParent(parent)
        
        # Data storage - comprehensive like enhanced web version
        self.time_data = []
        # Multiple product flows
        self.product_sep_data = []      # XMEAS(14)
        self.stripper_data = []         # XMEAS(17)
        self.purge_data = []           # XMEAS(10)
        # Product compositions
        self.comp_g_data = []          # XMEAS(40)
        self.comp_h_data = []          # XMEAS(41)
        self.comp_f_data = []          # XMEAS(39)
        # Safety parameters
        self.temp_data = []            # XMEAS(9)
        self.pressure_data = []        # XMEAS(7)
        # Process health
        self.sep_level_data = []       # XMEAS(12)
        self.reactor_level_data = []   # XMEAS(8)
        self.max_points = 50
        
        self.setup_plots()
        
    def setup_plots(self):
        """Setup comprehensive subplot layout matching enhanced web version."""
        self.figure.clear()
        self.axes = self.figure.subplots(2, 2)

        self.figure.suptitle('TEP Process Monitor - Comprehensive Analysis', fontsize=16, fontweight='bold')

        # Plot 1: Multiple Product Flows (TOP LEFT)
        self.product_sep_line, = self.axes[0,0].plot([], [], 'b-', linewidth=2, label='Product Sep (m³/h)')
        self.stripper_line, = self.axes[0,0].plot([], [], 'g-', linewidth=2, label='Stripper (m³/h)')
        self.purge_line, = self.axes[0,0].plot([], [], 'r-', linewidth=2, label='Purge/10 (kscmh)')
        self.axes[0,0].set_title('🏭 Multiple Product Flows', fontweight='bold')
        self.axes[0,0].set_ylabel('Flow Rate')
        self.axes[0,0].legend(fontsize=8)
        self.axes[0,0].grid(True, alpha=0.3)

        # Plot 2: Product Compositions (TOP RIGHT)
        self.comp_g_line, = self.axes[0,1].plot([], [], 'gold', linewidth=2, label='Component G')
        self.comp_h_line, = self.axes[0,1].plot([], [], 'orange', linewidth=2, label='Component H')
        self.comp_f_line, = self.axes[0,1].plot([], [], 'brown', linewidth=2, label='Component F')
        self.axes[0,1].set_title('💰 Product Quality', fontweight='bold')
        self.axes[0,1].set_ylabel('Composition (mole %)')
        self.axes[0,1].legend(fontsize=8)
        self.axes[0,1].grid(True, alpha=0.3)

        # Plot 3: Safety Parameters (BOTTOM LEFT)
        self.temp_line, = self.axes[1,0].plot([], [], 'r-', linewidth=2, label='Temperature (°C)')
        self.axes[1,0].set_title('🚨 Safety Parameters', fontweight='bold')
        self.axes[1,0].set_ylabel('Temperature (°C)', color='r')
        self.axes[1,0].set_xlabel('Time (minutes)')
        self.axes[1,0].grid(True, alpha=0.3)

        # Create second y-axis for pressure
        self.pressure_ax = self.axes[1,0].twinx()
        self.pressure_line, = self.pressure_ax.plot([], [], 'b-', linewidth=2, label='Pressure (kPa)')
        self.pressure_ax.set_ylabel('Pressure (kPa)', color='b')

        # Combined legend for safety plot
        lines1, labels1 = self.axes[1,0].get_legend_handles_labels()
        lines2, labels2 = self.pressure_ax.get_legend_handles_labels()
        self.axes[1,0].legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)

        # Plot 4: Process Health (BOTTOM RIGHT)
        self.sep_level_line, = self.axes[1,1].plot([], [], 'm-', linewidth=2, label='Separator Level')
        self.reactor_level_line, = self.axes[1,1].plot([], [], 'c-', linewidth=2, label='Reactor Level')
        self.axes[1,1].set_title('⚙️ Process Health', fontweight='bold')
        self.axes[1,1].set_ylabel('Level (%)')
        self.axes[1,1].set_xlabel('Time (minutes)')
        self.axes[1,1].legend(fontsize=8)
        self.axes[1,1].grid(True, alpha=0.3)

        self.figure.tight_layout()
        self.draw()
        
    def update_data(self, data_point):
        """Update plots with comprehensive data matching enhanced web version."""
        # Add new data
        self.time_data.append(data_point['time'])
        # Multiple product flows
        self.product_sep_data.append(data_point['product_sep'])
        self.stripper_data.append(data_point['stripper'])
        self.purge_data.append(data_point['purge'] / 10)  # Scale for visibility
        # Product compositions
        self.comp_g_data.append(data_point['comp_g'])
        self.comp_h_data.append(data_point['comp_h'])
        self.comp_f_data.append(data_point['comp_f'])
        # Safety parameters
        self.temp_data.append(data_point['temperature'])
        self.pressure_data.append(data_point['pressure'])
        # Process health
        self.sep_level_data.append(data_point['sep_level'])
        self.reactor_level_data.append(data_point['reactor_level'])

        # Keep only recent data
        if len(self.time_data) > self.max_points:
            self.time_data.pop(0)
            self.product_sep_data.pop(0)
            self.stripper_data.pop(0)
            self.purge_data.pop(0)
            self.comp_g_data.pop(0)
            self.comp_h_data.pop(0)
            self.comp_f_data.pop(0)
            self.temp_data.pop(0)
            self.pressure_data.pop(0)
            self.sep_level_data.pop(0)
            self.reactor_level_data.pop(0)

        # Update plot lines
        # Plot 1: Multiple Product Flows
        self.product_sep_line.set_data(self.time_data, self.product_sep_data)
        self.stripper_line.set_data(self.time_data, self.stripper_data)
        self.purge_line.set_data(self.time_data, self.purge_data)

        # Plot 2: Product Compositions
        self.comp_g_line.set_data(self.time_data, self.comp_g_data)
        self.comp_h_line.set_data(self.time_data, self.comp_h_data)
        self.comp_f_line.set_data(self.time_data, self.comp_f_data)

        # Plot 3: Safety Parameters
        self.temp_line.set_data(self.time_data, self.temp_data)
        self.pressure_line.set_data(self.time_data, self.pressure_data)

        # Plot 4: Process Health
        self.sep_level_line.set_data(self.time_data, self.sep_level_data)
        self.reactor_level_line.set_data(self.time_data, self.reactor_level_data)

        # Auto-scale axes
        for ax in self.axes.flat:
            ax.relim()
            ax.autoscale_view()

        # Also scale pressure axis
        self.pressure_ax.relim()
        self.pressure_ax.autoscale_view()

        self.draw()
        
    def clear_data(self):
        """Clear all plot data."""
        self.time_data.clear()
        self.product_sep_data.clear()
        self.stripper_data.clear()
        self.purge_data.clear()
        self.comp_g_data.clear()
        self.comp_h_data.clear()
        self.comp_f_data.clear()
        self.temp_data.clear()
        self.pressure_data.clear()
        self.sep_level_data.clear()
        self.reactor_level_data.clear()
        self.setup_plots()


class CleanTEPSimulator(QMainWindow):
    """Clean, well-designed Qt application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEP Process Simulator")
        self.setGeometry(100, 100, 1400, 900)
        
        # Simulation components
        self.worker = SimulationWorker()
        self.worker_thread = None
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        # Status
        self.is_running = False
        
    def setup_ui(self):
        """Create clean, well-organized interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left sidebar (fixed width)
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Right plot area (expandable)
        self.plot_widget = PlotWidget()
        main_layout.addWidget(self.plot_widget, 1)  # stretch factor 1
        
        # Set proportions: 300px sidebar, rest for plot
        main_layout.setContentsMargins(10, 10, 10, 10)
        
    def create_sidebar(self):
        """Create clean, organized sidebar."""
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("TEP Simulator Controls")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333; margin-bottom: 10px; border: none;")
        layout.addWidget(title)
        
        # Control buttons
        controls_group = self.create_controls_section()
        layout.addWidget(controls_group)
        
        # Fault settings
        fault_group = self.create_fault_section()
        layout.addWidget(fault_group)
        
        # Status
        status_group = self.create_status_section()
        layout.addWidget(status_group)
        
        # Demo guide
        demo_group = self.create_demo_section()
        layout.addWidget(demo_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return sidebar
        
    def create_controls_section(self):
        """Create control buttons section."""
        group = QGroupBox("Controls")
        group.setFont(QFont("Arial", 12, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4CAF50;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Start/Stop button
        self.start_button = QPushButton("▶ Start Simulation")
        self.start_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_button.clicked.connect(self.toggle_simulation)
        layout.addWidget(self.start_button)
        
        # Reset button
        reset_button = QPushButton("🔄 Reset")
        reset_button.setFont(QFont("Arial", 11))
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        reset_button.clicked.connect(self.reset_simulation)
        layout.addWidget(reset_button)
        
        return group
        
    def create_fault_section(self):
        """Create fault configuration section."""
        group = QGroupBox("Fault Configuration")
        group.setFont(QFont("Arial", 12, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2196F3;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2196F3;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Fault type
        fault_label = QLabel("Fault Type:")
        fault_label.setFont(QFont("Arial", 10, QFont.Bold))
        fault_label.setStyleSheet("color: #333; border: none;")
        layout.addWidget(fault_label)
        
        self.fault_combo = QComboBox()
        self.fault_combo.setFont(QFont("Arial", 10))
        self.fault_combo.addItems([
            "0 - Normal Operation",
            "1 - A/C Feed Ratio",
            "4 - Cooling Water",
            "6 - Feed Loss",
            "8 - Feed Composition",
            "13 - Reaction Kinetics ⭐"
        ])
        self.fault_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #333;
            }
            QComboBox:focus {
                border-color: #2196F3;
            }
        """)
        self.fault_combo.currentTextChanged.connect(self.update_fault_selection)
        layout.addWidget(self.fault_combo)
        
        # Intensity
        intensity_label = QLabel("Fault Intensity:")
        intensity_label.setFont(QFont("Arial", 10, QFont.Bold))
        intensity_label.setStyleSheet("color: #333; border: none;")
        layout.addWidget(intensity_label)
        
        # Intensity slider with value
        intensity_layout = QHBoxLayout()
        
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(5, 20)  # 0.5 to 2.0
        self.intensity_slider.setValue(10)
        self.intensity_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)
        self.intensity_slider.valueChanged.connect(self.update_intensity)
        intensity_layout.addWidget(self.intensity_slider)
        
        self.intensity_label = QLabel("1.0")
        self.intensity_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.intensity_label.setStyleSheet("color: #333; border: none; min-width: 30px;")
        intensity_layout.addWidget(self.intensity_label)
        
        layout.addLayout(intensity_layout)
        
        return group
        
    def create_status_section(self):
        """Create status display section."""
        group = QGroupBox("Status")
        group.setFont(QFont("Arial", 12, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #FF9800;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        self.status_label = QLabel("Ready to start simulation")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                color: #333;
            }
        """)
        layout.addWidget(self.status_label)
        
        return group
        
    def create_demo_section(self):
        """Create demo guide section."""
        group = QGroupBox("Demo Guide")
        group.setFont(QFont("Arial", 12, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9C27B0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #9C27B0;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        demo_text = QLabel("""
<b>Best for Demos:</b><br>
• Fault 13 - Most dramatic<br>
• Intensity: 1.5-2.0<br>
• Changes in 30 seconds<br><br>
<b>Quick Steps:</b><br>
1. Start with Normal<br>
2. Select Fault 13<br>
3. Set intensity 1.8<br>
4. Watch changes!
        """)
        demo_text.setFont(QFont("Arial", 9))
        demo_text.setWordWrap(True)
        demo_text.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                color: #333;
            }
        """)
        layout.addWidget(demo_text)
        
        return group
        
    def setup_connections(self):
        """Setup signal connections."""
        self.worker.data_ready.connect(self.plot_widget.update_data)
        self.worker.data_ready.connect(self.update_status)
        
    def update_fault_selection(self):
        """Update fault selection."""
        text = self.fault_combo.currentText()
        fault_num = int(text.split(' - ')[0])
        
        # Update worker
        intensity = self.intensity_slider.value() / 10.0
        self.worker.set_fault(fault_num, intensity)
        
    def update_intensity(self):
        """Update fault intensity."""
        intensity = self.intensity_slider.value() / 10.0
        self.intensity_label.setText(f"{intensity:.1f}")
        
        # Update worker
        text = self.fault_combo.currentText()
        fault_num = int(text.split(' - ')[0])
        self.worker.set_fault(fault_num, intensity)
        
    def toggle_simulation(self):
        """Start or stop simulation."""
        if not self.is_running:
            self.start_simulation()
        else:
            self.stop_simulation()
            
    def start_simulation(self):
        """Start the simulation."""
        self.is_running = True
        self.start_button.setText("⏹ Stop Simulation")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self.worker.start_simulation, daemon=True)
        self.worker_thread.start()
        
    def stop_simulation(self):
        """Stop the simulation."""
        self.is_running = False
        self.worker.stop_simulation()
        self.start_button.setText("▶ Start Simulation")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
    def reset_simulation(self):
        """Reset the simulation."""
        self.stop_simulation()
        self.worker.reset_simulation()
        self.plot_widget.clear_data()
        self.status_label.setText("Reset complete - Ready for new simulation")
        
    def update_status(self, data_point):
        """Update status display."""
        if self.is_running:
            sample_count = data_point['sample_count']
            text = self.fault_combo.currentText()
            fault_name = text.split(' - ')[1] if ' - ' in text else 'Normal'
            
            if 'Normal' not in fault_name:
                self.status_label.setText(f"🚨 FAULT: {fault_name}\nSamples: {sample_count}\nTime: {data_point['time']:.0f} min")
                self.status_label.setStyleSheet("""
                    QLabel {
                        background-color: #ffebee;
                        border: 1px solid #f44336;
                        border-radius: 4px;
                        padding: 10px;
                        color: #333;
                    }
                """)
            else:
                self.status_label.setText(f"✅ Normal Operation\nSamples: {sample_count}\nTime: {data_point['time']:.0f} min")
                self.status_label.setStyleSheet("""
                    QLabel {
                        background-color: #e8f5e8;
                        border: 1px solid #4CAF50;
                        border-radius: 4px;
                        padding: 10px;
                        color: #333;
                    }
                """)


def main():
    """Main function."""
    print("🎛️ Clean Qt TEP Simulator")
    print("="*40)
    print("✅ Completely redesigned interface")
    print("✅ Clear labels and readable text")
    print("✅ Proper layout and proportions")
    print("✅ Professional appearance")
    
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = CleanTEPSimulator()
    window.show()
    
    print("\n🚀 Clean Qt application started!")
    print("   • Fixed layout and proportions")
    print("   • Clear labels for all controls")
    print("   • Readable text with proper colors")
    print("   • Professional, organized design")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

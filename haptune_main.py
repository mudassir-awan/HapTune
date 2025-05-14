"""
HapTune: An Open-Source Visual Tool for Designing User-Defined Haptic Signals

This script launches the HapTune application.
It provides a GUI for creating, editing, and exporting both low-frequency haptic signals
and high-frequency vibration patterns, intended for use in haptic feedback, robotic control,
and virtual texture rendering systems.

Developed by: Mudassir Ibrahim Awan
License: Apache 2.0 — see LICENSE file for details
Project URL: https://github.com/mudassir-awan/HapTune

Note: This open-source software is freely available for academic research, student use, and non-commercial projects.
Actively seeking contributors and suggestions to improve functionality and usability.
"""



import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QAction, QGroupBox, QMessageBox,QDoubleSpinBox, QInputDialog, QDialog, QCheckBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.interpolate import UnivariateSpline
from matplotlib.ticker import MultipleLocator

import pandas as pd

# Import qtmodern
import qtmodern.styles
import qtmodern.windows

xmax = 20
xmin = -20

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=2, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        self.setFixedSize(1200, 500)

        self.points = []  # List to hold points
        self.history = []  # History for undo functionality
        self.original_points = []  # Initialize this before calling plot_initial()

        # Initialize bounds BEFORE plot_initial
        self.left_bound = 0
        self.right_bound = 1000

        # Initialize the plot with default or initial points
        self.plot_initial()



    def plot_initial(self):
        # Set the x and y axis limits explicitly
        self.left_bound = 0
        self.right_bound = 1000
        self.bottom_bound = -20
        self.top_bound = 20

        self.margin_left = 0
        self.margin_right = 1050

        # Print current limits to verify
        # print(f"X-limits: {self.axes.get_xlim()}")
        # print(f"Y-limits: {self.axes.get_ylim()}")

        self.axes.grid(True, linestyle='--', alpha=0.5)
        self.axes.set_xlabel("No.of Samples", fontweight='bold')
        self.axes.set_ylabel("Amplitude", fontweight='bold')
        self.fig.subplots_adjust(left=0.1, right=0.93, top=0.95, bottom=0.1)

        # Add vertical dotted line at x=62 with yellow color
        self.axes.axvline(x=self.margin_left, color='green', linestyle='--', linewidth=0.5)
        self.axes.axvline(x=self.margin_right, color='green', linestyle='--', linewidth=0.5)

        # # Add horizontal dotted lines at y=-30 and y=50
        # self.axes.axhline(y=-30, color='green', linestyle='--', linewidth=0.5)
        # self.axes.axhline(y=50, color='green', linestyle='--', linewidth=0.5)




        # Force the canvas to update and reflect the lines
        self.draw()

        # Set initial points if no data is loaded
        if not self.original_points:  # Check if no file was loaded
            self.points = [(0, 0)]  # Default points
            self.original_points = [(0, 0)]

        self.update_plot()  # Plot the initial or default points
        self.draw()

    def add_point(self, x, y):
        self.record_history()
        self.points.append((x, y))
        self.update_plot()

    def delete_point(self, point):
        self.record_history()
        if point in self.points:
            self.points.remove(point)
            self.update_plot()

    def move_point(self, old_point, new_point):
        self.record_history()
        if old_point in self.points:
            self.points.remove(old_point)
            self.points.append(new_point)
            self.update_plot()

    def record_history(self):
        self.history.append(list(self.points))

    def undo(self):
        if self.history:
            self.points = self.history.pop()
            self.update_plot()

    def update_plot(self):
        self.points.sort()
        self.plot_curve()



    def set_tick_intervals(self, x_interval, y_interval):
        self.axes.xaxis.set_major_locator(MultipleLocator(x_interval))
        self.axes.yaxis.set_major_locator(MultipleLocator(y_interval))
        self.draw()

    def set_axis_limits(self, x_min, x_max, y_min, y_max):
        self.left_bound = x_min
        self.right_bound = x_max
        self.bottom_bound = y_min
        self.top_bound = y_max

        # Save margin positions
        self.margin_left = x_min
        self.margin_right = x_max

        # Add extra margin space for display
        x_margin = (x_max - x_min) * 0.05  # 5% margin
        y_margin = (y_max - y_min) * 0.05  # 5% margin

        self.axes.set_xlim(x_min - x_margin, x_max + x_margin)
        self.axes.set_ylim(y_min - y_margin, y_max + y_margin)

        self.fig.subplots_adjust(left=0.1, right=0.93, top=0.95, bottom=0.1)
        self.update_plot()

    def mouseDoubleClickEvent(self, event):
        # Get mouse click position in pixels
        x_click = event.x()
        y_click = event.y()

        # Convert mouse position to figure-relative coordinates
        x_fig = x_click / self.width()
        y_fig = 1 - (y_click / self.height())

        # Debug if needed
        # print(f"Clicked at figure coords: ({x_fig:.2f}, {y_fig:.2f})")

        # Define rough clickable areas
        if 0.35 < x_fig < 0.65 and y_fig < 0.1:  # Near X-axis label
            self.change_axis_label(axis='x')
        elif x_fig < 0.1 and 0.35 < y_fig < 0.65:  # Near Y-axis label
            self.change_axis_label(axis='y')


    def change_axis_label(self, axis):
        if axis == 'x':
            current_label = self.axes.get_xlabel()
            new_label, ok = QInputDialog.getText(self, 'X-Axis Label', 'Enter new X-axis label:',
                                                 text=current_label)
            if ok and new_label:
                self.axes.set_xlabel(new_label, fontweight='bold')
        elif axis == 'y':
            current_label = self.axes.get_ylabel()
            new_label, ok = QInputDialog.getText(self, 'Y-Axis Label', 'Enter new Y-axis label:',
                                                 text=current_label)
            if ok and new_label:
                self.axes.set_ylabel(new_label, fontweight='bold')

        self.draw()

    def plot_curve(self, highlight=None):
        self.axes.clear()

        # ✅ First restore main limits
        self.axes.set_xlim(self.left_bound - (self.right_bound - self.left_bound) * 0.05,
                           self.right_bound + (self.right_bound - self.left_bound) * 0.05)
        self.axes.set_ylim(self.bottom_bound - (self.top_bound - self.bottom_bound) * 0.05,
                           self.top_bound + (self.top_bound - self.bottom_bound) * 0.05)

        # ✅ Then plot margin lines at exact positions
        self.axes.axvline(x=self.margin_left, color='green', linestyle='--', linewidth=1.0)
        self.axes.axvline(x=self.margin_right, color='green', linestyle='--', linewidth=1.0)

        self.axes.axhline(y=self.bottom_bound, color='green', linestyle='--', linewidth=1.0)
        self.axes.axhline(y=self.top_bound, color='green', linestyle='--', linewidth=1.0)

        # ✅ Now add the rest
        self.axes.grid(True, linestyle='--', alpha=0.5)
        # self.axes.set_xlabel("Angle (deg)", fontweight='bold')
        # self.axes.set_ylabel("Force Amplitude (N)", fontweight='bold')

        self.axes.set_xlabel("No.of Samples", fontweight='bold')
        self.axes.set_ylabel("Amplitude", fontweight='bold')

        # # 👇 Add these two lines here to force ticks at min and max
        # self.axes.set_xticks(list(self.axes.get_xticks()) + [self.margin_left, self.margin_right])
        # self.axes.set_yticks(list(self.axes.get_yticks()) + [self.bottom_bound, self.top_bound])


        if self.points:
            x_pts, y_pts = zip(*self.points)
            self.axes.plot(x_pts, y_pts, 'ro')

            if len(self.points) > 1:
                try:
                    if len(self.points) >= 4 and all(np.diff(x_pts) > 0):
                        spline = UnivariateSpline(x_pts, y_pts, k=3,
                                                  s=self.smoothing_factor if hasattr(self, 'smoothing_factor') else 0)
                        x_new = np.linspace(min(x_pts), max(x_pts), 500)
                        y_new = spline(x_new)
                        self.axes.plot(x_new, y_new, '-b')
                    else:
                        x_new = np.linspace(min(x_pts), max(x_pts), 500)
                        y_new = np.interp(x_new, x_pts, y_pts)
                        self.axes.plot(x_new, y_new, '--g', label='Linear Interpolation')
                except Exception as e:
                    print(f"Spline interpolation error: {e}")

        if highlight:
            self.axes.plot(highlight[0], highlight[1], 'yo')

        # Center lines
        self.axes.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        self.axes.axvline(x=0, color='black', linestyle='-', linewidth=0.5)

        self.fig.subplots_adjust(left=0.1, right=0.93, top=0.95, bottom=0.1)
        self.draw()




    def highlight_issues(self, x_pts, y_pts):
        # Example check for duplicate or very close X-coordinates
        tolerance = 0.01  # Define a tolerance for how close points can be
        for i in range(len(x_pts)):
            for j in range(i + 1, len(x_pts)):
                if abs(x_pts[i] - x_pts[j]) < tolerance:
                    self.axes.plot(x_pts[i], y_pts[i], 'mo')  # Highlight in magenta
                    self.axes.plot(x_pts[j], y_pts[j], 'mo')  # Highlight in magenta


    def highlight_point(self, point):
        self.plot_curve(highlight=point)


    def apply_smoothing(self, smoothing_factor):
        self.smoothing_factor = smoothing_factor
        if len(self.points) > 1:
            x_pts, y_pts = zip(*self.points)
            self.smoothing_spline = UnivariateSpline(x_pts, y_pts, k=3, s=smoothing_factor)
        self.update_plot()

    def interpolate_points(self, points_per_degree):
        # Decide which set of points to use for interpolation
        if self.points:  # If there are manually added points
            interp_points = self.points
        elif self.original_points:  # If there are only original points
            interp_points = self.original_points
        else:
            return  # Exit if there are no points

        x_pts, y_pts = zip(*interp_points)
        min_x, max_x = min(x_pts), max(x_pts)

        # Calculate total number of points based on degrees and points per degree
        total_points = int((max_x - min_x) * points_per_degree)
        total_points = max(total_points, 2)  # Ensure at least two points

        if hasattr(self, 'smoothing_spline'):
            spline_function = self.smoothing_spline
        else:
            spline_function = UnivariateSpline(x_pts, y_pts, k=3, s=0)

        x_new = np.linspace(min_x, max_x, total_points)
        y_new = spline_function(x_new)
        self.interpolated_points = list(zip(x_new, y_new))
        self.plot_curve_with_interpolation()


    # def downsample_points(self, downsample_factor):
    #     if self.original_points:
    #         # Ensure the downsample factor is not less than the number of points
    #         downsample_factor = min(downsample_factor, len(self.original_points))
    #
    #         # Select points at regular intervals based on the downsample factor
    #         downsampled_points = self.original_points[::downsample_factor]
    #
    #         # Update the points and the plot
    #         self.points = downsampled_points
    #         self.update_plot()

    def downsample_points(self, downsample_factor):
        try:
            if self.original_points:
                # Ensure the downsample factor is not less than the number of points
                if downsample_factor >= len(self.original_points):
                    raise ValueError("Downsample factor is too large. Not enough points to downsample.")

                # Select points at regular intervals based on the downsample factor
                downsampled_points = self.original_points[::downsample_factor]

                # Check if the downsampled points are valid
                if len(downsampled_points) < 2:
                    raise ValueError("Not enough points after downsampling.")

                # Update the points and the plot
                self.points = downsampled_points
                self.update_plot()

            else:
                raise ValueError("No original points available to downsample.")

        except ValueError as e:
            print(f"Error during downsampling: {e}")  # Print error to the console for debugging
            QMessageBox.warning(self, 'Downsampling Error', str(e))  # Show a warning message to the user

    def plot_curve_with_interpolation(self):
        self.plot_curve()  # Plot the original points and curve
        if hasattr(self, 'interpolated_points'):
            x_int, y_int = zip(*self.interpolated_points)
            self.axes.plot(x_int, y_int, 'gx', label='Interpolated Points')  # Green 'x' for interpolated points
            self.axes.legend()  # Display the legend
            self.draw()

class AxisSettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Edit Axis Range and Ticks")
        self.setGeometry(100, 100, 400, 200)
        self.parent = parent

        layout = QVBoxLayout()

        # Get current axis limits and tick spacing
        canvas = self.parent.plot_canvas
        current_xmin = canvas.left_bound
        current_xmax = canvas.right_bound
        current_ymin = canvas.bottom_bound
        current_ymax = canvas.top_bound

        xticks = canvas.axes.get_xticks()
        yticks = canvas.axes.get_yticks()
        x_tick = round(xticks[1] - xticks[0], 2) if len(xticks) > 1 else 1
        y_tick = round(yticks[1] - yticks[0], 2) if len(yticks) > 1 else 1

        # --- X Settings ---
        x_layout = QHBoxLayout()

        self.xmin_input = QDoubleSpinBox()
        self.xmin_input.setRange(-10000, 10000)
        self.xmin_input.setValue(current_xmin)
        self.xmin_input.setPrefix('Xmin: ')
        x_layout.addWidget(self.xmin_input)

        self.xmax_input = QDoubleSpinBox()
        self.xmax_input.setRange(-10000, 10000)
        self.xmax_input.setValue(current_xmax)
        self.xmax_input.setPrefix('Xmax: ')
        x_layout.addWidget(self.xmax_input)

        self.x_tick_input = QDoubleSpinBox()
        self.x_tick_input.setRange(0.01, 1000)
        self.x_tick_input.setValue(x_tick)
        self.x_tick_input.setPrefix('Tick: ')
        x_layout.addWidget(self.x_tick_input)

        layout.addLayout(x_layout)

        # --- Y Settings ---
        y_layout = QHBoxLayout()

        self.ymin_input = QDoubleSpinBox()
        self.ymin_input.setRange(-10000, 10000)
        self.ymin_input.setValue(current_ymin)
        self.ymin_input.setPrefix('Ymin: ')
        y_layout.addWidget(self.ymin_input)

        self.ymax_input = QDoubleSpinBox()
        self.ymax_input.setRange(-10000, 10000)
        self.ymax_input.setValue(current_ymax)
        self.ymax_input.setPrefix('Ymax: ')
        y_layout.addWidget(self.ymax_input)

        self.y_tick_input = QDoubleSpinBox()
        self.y_tick_input.setRange(0.01, 1000)
        self.y_tick_input.setValue(y_tick)
        self.y_tick_input.setPrefix('Tick: ')
        y_layout.addWidget(self.y_tick_input)

        layout.addLayout(y_layout)

        # --- Apply Button ---
        apply_button = QPushButton("Apply", self)
        apply_button.clicked.connect(self.apply_changes)
        layout.addWidget(apply_button)

        self.setLayout(layout)

    def apply_changes(self):
        x_min = self.xmin_input.value()
        x_max = self.xmax_input.value()
        y_min = self.ymin_input.value()
        y_max = self.ymax_input.value()
        x_tick = self.x_tick_input.value()
        y_tick = self.y_tick_input.value()

        self.parent.plot_canvas.set_axis_limits(x_min, x_max, y_min, y_max)
        self.parent.plot_canvas.set_tick_intervals(x_tick, y_tick)


from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QGroupBox, QPushButton,
                             QCheckBox, QScrollArea, QWidget)

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QGroupBox, QPushButton,
                             QCheckBox, QScrollArea, QWidget)

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QDoubleSpinBox, QSpinBox, QLabel,
                             QGroupBox, QScrollArea, QWidget, QCheckBox)
from PyQt5.QtCore import Qt

# Only the updated VibrationSettingsWindow class part
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QDoubleSpinBox, QDialog, QGroupBox, QCheckBox, QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class VibrationSettingsWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Vibration Signal Settings")
        self.setGeometry(200, 200, 600, 800)
        self.parent = parent

        layout = QVBoxLayout()

        # Top Settings (Sampling Rate and Global Amplitude)
        top_layout = QHBoxLayout()
        self.sampling_input = QSpinBox()
        self.sampling_input.setRange(1, 50000)
        self.sampling_input.setValue(1000)
        self.sampling_input.setPrefix("Sampling: ")
        top_layout.addWidget(self.sampling_input)

        self.global_amp_input = QDoubleSpinBox()
        self.global_amp_input.setRange(0.0, 10.0)
        self.global_amp_input.setSingleStep(0.1)
        self.global_amp_input.setValue(1.0)
        self.global_amp_input.setPrefix("Global Amp: ")
        top_layout.addWidget(self.global_amp_input)

        layout.addLayout(top_layout)

        # Frequencies Group with Fixed Size Scroll Area
        freq_group = QGroupBox("Frequencies")
        freq_layout = QVBoxLayout()

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.frequency_rows = []  # store all rows
        for _ in range(3):  # ✅ initially add 4 rows
            self.add_frequency_row(100, 1.0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setFixedHeight(150)  # ✅ fixed space for 4 rows
        freq_layout.addWidget(self.scroll_area)

        # Add Frequency Button
        self.add_freq_button = QPushButton("Add Frequency")
        self.add_freq_button.clicked.connect(self.add_frequency_row)
        self.add_freq_button.setFixedHeight(30)
        freq_layout.addWidget(self.add_freq_button)

        freq_group.setLayout(freq_layout)
        layout.addWidget(freq_group)


        # --- Action Buttons Group ---
        action_group = QGroupBox("Actions")
        action_main_layout = QVBoxLayout()  # Main vertical layout

        # --- First Row ---
        action_row1 = QHBoxLayout()
        self.vibration_button = QPushButton("Generate Vibration")
        self.vibration_button.setFixedHeight(30)
        self.vibration_button.clicked.connect(self.toggle_vibration)

        self.clear_vibration_button = QPushButton("Clear Vibration")
        self.clear_vibration_button.setFixedHeight(30)
        self.clear_vibration_button.clicked.connect(self.clear_vibration)

        self.save_vibration_button = QPushButton("Save Vibration")
        self.save_vibration_button.setFixedHeight(30)
        self.save_vibration_button.clicked.connect(self.save_vibration_waveform)

        action_row1.addWidget(self.vibration_button)
        action_row1.addWidget(self.clear_vibration_button)
        action_row1.addWidget(self.save_vibration_button)

        # --- Second Row ---
        action_row2 = QHBoxLayout()
        self.envelope_button = QPushButton("Generate Envelope")
        self.envelope_button.setFixedHeight(30)
        self.envelope_button.clicked.connect(self.generate_envelope)

        self.clear_envelope_button = QPushButton("Clear Envelope")
        self.clear_envelope_button.setFixedHeight(30)
        self.clear_envelope_button.clicked.connect(self.clear_envelope)

        # Add an empty label to fill the third space
        empty_label = QLabel()

        action_row2.addWidget(self.envelope_button)
        action_row2.addWidget(self.clear_envelope_button)
        action_row2.addWidget(empty_label)

        # --- Add both rows to main layout ---
        action_main_layout.addLayout(action_row1)
        action_main_layout.addLayout(action_row2)

        action_group.setLayout(action_main_layout)
        layout.addWidget(action_group)

        # --- Graph Area: Vibration + DFT ---
        self.graph_group = QGroupBox()
        graph_layout = QVBoxLayout()

        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        self.fig = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.fig)

        graph_layout.addWidget(self.canvas)
        self.graph_group.setLayout(graph_layout)
        layout.addWidget(self.graph_group)

        self.setLayout(layout)

    def add_frequency_row(self, default_freq=100, default_amp=1.0):
        row_layout = QHBoxLayout()
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        freq_spin = QSpinBox()
        freq_spin.setRange(1, 10000)
        freq_spin.setValue(default_freq)
        amp_spin = QDoubleSpinBox()
        amp_spin.setRange(0.0, 10.0)
        amp_spin.setSingleStep(0.1)
        amp_spin.setValue(default_amp)

        row_layout.addWidget(checkbox)
        row_layout.addWidget(QLabel("Freq (Hz):"))
        row_layout.addWidget(freq_spin)
        row_layout.addWidget(QLabel("Amp:"))
        row_layout.addWidget(amp_spin)

        container = QWidget()
        container.setLayout(row_layout)
        self.scroll_layout.addWidget(container)

        self.frequency_rows.append((checkbox, freq_spin, amp_spin))

    def collect_enabled_frequencies(self):
        frequencies = []
        for checkbox, freq_spin, amp_spin in self.frequency_rows:
            if checkbox.isChecked():
                frequencies.append((freq_spin.value(), amp_spin.value()))
        return frequencies

    def clear_vibration(self):
        try:
            if hasattr(self.parent.plot_canvas, 'vibration_signal'):
                del self.parent.plot_canvas.vibration_signal
                self.parent.plot_canvas.update_plot()
                print("Vibration signal cleared.")
        except Exception as e:
            print(f"Error clearing vibration: {e}")

    def toggle_vibration(self):
        try:
            self.parent.sampling_rate = self.sampling_input.value()
            self.parent.amplitude_scale = self.global_amp_input.value()
            self.parent.multi_frequencies = self.collect_enabled_frequencies()

            if hasattr(self.parent, 'generate_multi_frequency_vibration'):
                self.parent.generate_multi_frequency_vibration()

            self.plot_vibration_and_dft()

        except Exception as e:
            print(f"Error during vibration generation: {e}")

    def generate_envelope(self):
        try:
            self.parent.show_envelope = True
            if hasattr(self.parent, 'plot_envelope'):
                self.parent.plot_envelope()
        except Exception as e:
            print(f"Error generating envelope: {e}")

    def clear_envelope(self):
        try:
            if hasattr(self.parent.plot_canvas, 'envelope_lines'):
                for line in self.parent.plot_canvas.envelope_lines:
                    line.remove()
                del self.parent.plot_canvas.envelope_lines
                self.parent.plot_canvas.axes.legend()
                self.parent.plot_canvas.draw()
                print("Envelope cleared.")
        except Exception as e:
            print(f"Error clearing envelope: {e}")

    def toggle_envelope(self):
        try:
            if self.envelope_button.isChecked():
                # Enable envelope
                self.parent.show_envelope = True
                self.parent.plot_envelope()
            else:
                # Disable envelope
                self.parent.show_envelope = False
                if hasattr(self.parent.plot_canvas, 'envelope_lines'):
                    for line in self.parent.plot_canvas.envelope_lines:
                        line.remove()
                    del self.parent.plot_canvas.envelope_lines
                self.parent.plot_canvas.axes.legend()
                self.parent.plot_canvas.draw()
        except Exception as e:
            print(f"Error during envelope toggle: {e}")

    def save_vibration_waveform(self):
        if hasattr(self.parent, 'vibration_window_save'):
            self.parent.vibration_window_save()

    def plot_vibration_and_dft(self):
        """Plot vibration waveform and DFT."""
        if not hasattr(self.parent.plot_canvas, 'vibration_signal'):
            return

        vibration_data = np.array(self.parent.plot_canvas.vibration_signal)
        x = vibration_data[:, 0]
        y = vibration_data[:, 1]

        # Compute FFT
        N = len(y)
        T = 1.0 / self.sampling_input.value()
        yf = np.fft.fft(y)
        xf = np.fft.fftfreq(N, T)[:N//2]

        mag = 2.0/N * np.abs(yf[:N//2])

        self.fig.clear()
        ax1 = self.fig.add_subplot(211)
        ax2 = self.fig.add_subplot(212)

        # Plot vibration
        ax1.plot(x, y, 'b-')
        ax1.set_title('Vibration Signal')
        ax1.set_ylabel('Amplitude')
        ax1.grid(True, linestyle='--', alpha=0.6)

        # Plot DFT
        ax2.plot(xf, mag, 'g-')
        ax2.set_title('DFT of Vibration')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Magnitude')
        ax2.grid(True, linestyle='--', alpha=0.6)
        ax2.set_xlim(0, self.sampling_input.value() / 2)  # Nyquist limit

        self.fig.tight_layout()
        self.canvas.draw()





from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLineEdit, QSpinBox, QFileDialog, QLabel
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Haptune'
        self.left = 10
        self.top = 10
        self.width = 1400
        self.height = 800
        self.selected_point = None

        self.vibration_frequency = 100
        self.amplitude_scale = 1.0
        self.sampling_rate = 1000
        self.show_envelope = True  # By default show envelope

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        button_height = 30

        # Data Load Section
        data_load_group = QGroupBox("Data Load")
        data_load_layout = QHBoxLayout()

        self.load_excel_button = QPushButton(' Load Profile ( Excel )', self)
        self.load_excel_button.setFixedHeight(button_height)  # Use the common button height
        self.load_excel_button.clicked.connect(self.on_load_clicked)

        self.load_csv_button = QPushButton(' Load Profile ( CSV )', self)
        self.load_csv_button.setFixedHeight(button_height)  # Use the common button height
        self.load_csv_button.clicked.connect(self.on_load_csv_clicked)

        self.loaded_file_line_edit = QLineEdit("No file loaded", self)
        self.loaded_file_line_edit.setReadOnly(True)

        self.reset_button = QPushButton(' Reset Editing', self)
        self.reset_button.setFixedHeight(button_height)  # Use the common button height
        self.reset_button.clicked.connect(self.reset_plot)

        self.overall_reset_button = QPushButton(' Unload Profile and Reset', self)
        self.overall_reset_button.setFixedHeight(button_height)  # Use the common button height
        self.overall_reset_button.clicked.connect(self.overall_reset)

        data_load_layout.addWidget(self.load_excel_button)
        data_load_layout.addWidget(self.load_csv_button)
        data_load_layout.addWidget(self.loaded_file_line_edit)
        data_load_layout.addWidget(self.overall_reset_button)
        data_load_layout.addWidget(self.reset_button)

        data_load_group.setLayout(data_load_layout)
        main_layout.addWidget(data_load_group)

        # Plot Canvas and Toolbar
        self.plot_canvas = PlotCanvas(self, width=5, height=4)
        self.plot_canvas.mpl_connect('button_press_event', self.on_click)
        self.plot_canvas.mpl_connect('motion_notify_event', self.on_move)
        self.plot_canvas.mpl_connect('button_release_event', self.on_release)
        plot_canvas_widget = QWidget()
        plot_canvas_layout = QVBoxLayout(plot_canvas_widget)
        plot_canvas_layout.addWidget(self.plot_canvas)
        plot_canvas_layout.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(plot_canvas_widget)
        self.toolbar = NavigationToolbar(self.plot_canvas, self)
        main_layout.addWidget(self.toolbar)

        #Menu Bar
        self.create_menu_bar()

        # Bottom Layout with Controls and Instructions
        bottom_layout = QHBoxLayout()

        instruction_panel = QLabel(
            "Instructions:\n"
            "\n"
            "• This interactive tool lets you create, edit, and export signal profiles such as force, vibration, or acceleration waveforms.\n"
            "• Load an existing profile from Excel/CSV, or create one from scratch. For dense signals, use downsampling first.\n"
            "• Axis limits and tick intervals can be adjusted via the Control Panel or Edit menu. Axis labels can be renamed by double-clicking near them.\n"
            "\n"
            "Editing:\n"
            "• Add Points: Ctrl + Left Click | Move: Drag | Delete: Select + Delete key | Undo: Ctrl + Z\n"
            "\n"
            "Signal Processing:\n"
            "• Apply spline smoothing for cleaner shapes, interpolate to increase resolution (e.g., 10 points/unit), or downsample for simpler editing.\n"
            "\n"
            "Vibration Generation:\n"
            "• Use 'Generate Vibration' to define a base envelope curve and synthesize high-frequency signals using multiple sine components.\n"
            "• Adjust sampling rate, amplitude scaling, and preview both the waveform and its DFT. Envelope-only mode is also available.\n"
            "\n"
            "Saving:\n"
            "• Save edited or interpolated profiles to Excel or CSV. Ensure interpolation is applied and profile length is sufficient before saving.\n"
        )


        instruction_panel.setStyleSheet("font-size: 12px; padding: 10px; background-color: lightyellow;")
        instruction_panel.setWordWrap(True)
        instruction_panel.setFixedWidth(1000)

        controls_group = QGroupBox("Control Panel")
        controls_layout = QVBoxLayout()
        self.setup_controls(controls_layout)
        controls_group.setLayout(controls_layout)
        controls_group.setFixedWidth(400)

        bottom_layout.addWidget(instruction_panel)
        bottom_layout.addWidget(controls_group)

        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def open_axis_settings_dialog(self):
        self.axis_settings_dialog = AxisSettingsDialog(self)
        self.axis_settings_dialog.show()

    def update_tick_intervals(self):
        x_tick_interval = self.x_tick_interval_input.value()
        y_tick_interval = self.y_tick_interval_input.value()
        self.plot_canvas.set_tick_intervals(x_tick_interval, y_tick_interval)

    def open_vibration_settings_window(self):
        self.vibration_window = VibrationSettingsWindow(self)
        self.vibration_window.show()

    def generate_vibration_signal(self):
        try:
            frequency = self.vibration_frequency
            amplitude_scale = self.amplitude_scale
            sampling_rate = self.sampling_rate

            if hasattr(self.plot_canvas, 'interpolated_points') and self.plot_canvas.interpolated_points:
                base_points = self.plot_canvas.interpolated_points
            else:
                base_points = self.plot_canvas.points

            if not base_points or len(base_points) < 2:
                raise ValueError("Need at least two points to generate vibration.")

            x_pts, y_pts = zip(*base_points)
            x_pts = np.array(x_pts)
            y_pts = np.array(y_pts)

            # Resample signal based on sampling rate
            x_dense = np.linspace(x_pts.min(), x_pts.max(), int((x_pts.max() - x_pts.min()) * sampling_rate / 1000))
            if len(x_pts) >= 4 and all(np.diff(x_pts) > 0):
                spline = UnivariateSpline(x_pts, y_pts, k=3, s=0)
                y_dense = spline(x_dense)
            else:
                y_dense = np.interp(x_dense, x_pts, y_pts)

            self.plot_canvas.envelope_x = x_dense
            self.plot_canvas.envelope_y = y_dense

            # Generate sine vibration
            vibration = np.sin(2 * np.pi * frequency * x_dense / sampling_rate)

            # Modulate sine with envelope
            final_signal = y_dense * vibration * amplitude_scale

            # Save for plotting
            self.plot_canvas.vibration_signal = list(zip(x_dense, final_signal))

            # Instead of clearing plot, now replot everything
            self.plot_canvas.update_plot()  # Redraw base curve
            if self.show_envelope:
                self.plot_envelope()  # Draw envelope if needed
            self.plot_vibration_only()  # Draw vibration

        except Exception as e:
            print(f"Error generating vibration: {e}")
            QMessageBox.warning(self, "Vibration Generation Error", str(e))

    def update_axis_ranges(self):
        x_min = self.xmin_input.value()
        x_max = self.xmax_input.value()
        y_min = self.ymin_input.value()
        y_max = self.ymax_input.value()

        self.plot_canvas.set_axis_limits(x_min, x_max, y_min, y_max)

    def plot_vibration_only(self):
        if hasattr(self.plot_canvas, 'vibration_signal'):
            x_vib, y_vib = zip(*self.plot_canvas.vibration_signal)

            # Plot vibration signal without clearing
            self.plot_canvas.axes.plot(x_vib, y_vib, 'b-', label='Vibration Signal')
            self.plot_canvas.axes.legend()
            self.plot_canvas.draw()
            QApplication.processEvents()

    def setup_controls(self, controls_layout):
        # Smoothing controls
        smoothing_layout = QHBoxLayout()
        self.smoothing_input = QSpinBox(self)
        self.smoothing_input.setRange(0, 100)
        self.smoothing_input.setValue(3)
        smoothing_layout.addWidget(self.smoothing_input)

        self.smoothing_button = QPushButton('Smoothing', self)
        self.smoothing_button.clicked.connect(lambda: self.apply_smoothing(True))
        self.smoothing_button.setFixedHeight(30)
        smoothing_layout.addWidget(self.smoothing_button)

        self.no_smoothing_button = QPushButton('No Smoothing', self)
        self.no_smoothing_button.clicked.connect(lambda: self.apply_smoothing(False))
        self.no_smoothing_button.setFixedHeight(30)
        smoothing_layout.addWidget(self.no_smoothing_button)

        controls_layout.addLayout(smoothing_layout)

        # Interpolation controls
        interpolation_layout = QHBoxLayout()
        self.interpolation_factor_input = QSpinBox(self)
        self.interpolation_factor_input.setRange(1, 100)
        self.interpolation_factor_input.setValue(10)
        interpolation_layout.addWidget(self.interpolation_factor_input)

        self.interpolate_button = QPushButton('Interpolate', self)
        self.interpolate_button.clicked.connect(self.perform_interpolation)
        self.interpolate_button.setFixedHeight(30)
        interpolation_layout.addWidget(self.interpolate_button)

        self.no_interpolate_button = QPushButton('No Interpolate', self)
        self.no_interpolate_button.clicked.connect(self.clear_interpolation)
        self.no_interpolate_button.setFixedHeight(30)
        interpolation_layout.addWidget(self.no_interpolate_button)

        controls_layout.addLayout(interpolation_layout)

        # Downsampling controls
        downsampling_layout = QHBoxLayout()
        self.downsampling_factor_input = QSpinBox(self)
        self.downsampling_factor_input.setRange(1, 100)
        self.downsampling_factor_input.setValue(20)
        downsampling_layout.addWidget(self.downsampling_factor_input)

        self.downsample_button = QPushButton('Downsample', self)
        self.downsample_button.clicked.connect(self.perform_downsampling)
        self.downsample_button.setFixedHeight(30)
        downsampling_layout.addWidget(self.downsample_button)

        controls_layout.addLayout(downsampling_layout)

        # Buttons for Axis Range and Vibration
        button_layout = QVBoxLayout()

        self.update_range_button = QPushButton( 'Set Axis Limits', self)
        self.update_range_button.clicked.connect(self.open_axis_settings_dialog)
        self.update_range_button.setFixedHeight(30)
        button_layout.addWidget(self.update_range_button)

        self.generate_vibration_button = QPushButton('Vibration Design Mode', self)
        self.generate_vibration_button.clicked.connect(self.open_vibration_settings_window)
        self.generate_vibration_button.setFixedHeight(30)
        button_layout.addWidget(self.generate_vibration_button)

        controls_layout.addLayout(button_layout)

        # Save Buttons in the same row
        save_layout = QHBoxLayout()
        self.save_button = QPushButton('Save to Excel', self)
        self.save_button.clicked.connect(self.on_save_excel_clicked)
        self.save_button.setFixedHeight(30)
        save_layout.addWidget(self.save_button)

        self.save_csv_button = QPushButton('Save to CSV', self)
        self.save_csv_button.clicked.connect(self.on_save_csv_clicked)
        self.save_csv_button.setFixedHeight(30)
        save_layout.addWidget(self.save_csv_button)

        controls_layout.addLayout(save_layout)

    def on_smoothing_clicked(self):
        if self.smoothing_button.isChecked():
            smoothing_factor = self.smoothing_input.value()
            self.plot_canvas.apply_smoothing(smoothing_factor)
            self.smoothing_button.setText("Disable Smoothing")
        else:
            self.plot_canvas.apply_smoothing(0)  # 0 smoothing factor to disable
            self.smoothing_button.setText("Enable Smoothing")

    def plot_vibration_signal(self):
        if hasattr(self.plot_canvas, 'vibration_signal'):
            x_vib, y_vib = zip(*self.plot_canvas.vibration_signal)

            # Clear the plot
            self.plot_canvas.axes.clear()

            # Plot vibration signal
            self.plot_canvas.axes.plot(x_vib, y_vib, 'b-', label='Vibration Signal')

            # Labels
            self.plot_canvas.axes.set_xlabel('Samples', fontweight='bold')
            self.plot_canvas.axes.set_ylabel('Amplitude', fontweight='bold')
            self.plot_canvas.axes.grid(True)
            self.plot_canvas.axes.legend()
            self.plot_canvas.draw()

    def prepare_envelope_only(self):
        """Generate smooth spline envelope without vibration."""
        if hasattr(self.plot_canvas, 'interpolated_points') and self.plot_canvas.interpolated_points:
            base_points = self.plot_canvas.interpolated_points
        else:
            base_points = self.plot_canvas.points

        if base_points and len(base_points) >= 2:
            x_pts, y_pts = zip(*base_points)
            x_pts = np.array(x_pts)
            y_pts = np.array(y_pts)

            x_dense = np.linspace(x_pts.min(), x_pts.max(), 1000)  # 1000 smooth points
            if len(x_pts) >= 4 and all(np.diff(x_pts) > 0):
                spline = UnivariateSpline(x_pts, y_pts, k=3, s=0)
                y_dense = spline(x_dense)
            else:
                y_dense = np.interp(x_dense, x_pts, y_pts)

            self.plot_canvas.envelope_x = x_dense
            self.plot_canvas.envelope_y = y_dense

    def clear_envelope(self):
        if hasattr(self.plot_canvas, 'envelope_x'):
            del self.plot_canvas.envelope_x
        if hasattr(self.plot_canvas, 'envelope_y'):
            del self.plot_canvas.envelope_y

    def plot_envelope(self):
        if not self.show_envelope:
            return  # Exit if not enabled

        # Remove previously drawn envelope lines if exist
        if hasattr(self.plot_canvas, 'envelope_lines'):
            for line in self.plot_canvas.envelope_lines:
                line.remove()
            del self.plot_canvas.envelope_lines

        if hasattr(self.plot_canvas, 'envelope_x') and hasattr(self.plot_canvas, 'envelope_y'):
            x_final = self.plot_canvas.envelope_x
            y_final = self.plot_canvas.envelope_y
        else:
            if hasattr(self.plot_canvas, 'interpolated_points') and self.plot_canvas.interpolated_points:
                base_points = self.plot_canvas.interpolated_points
            elif hasattr(self.plot_canvas, 'smoothing_spline'):
                x_pts, y_pts = zip(*self.plot_canvas.points)
                spline = self.plot_canvas.smoothing_spline
                x_dense = np.linspace(x_pts[0], x_pts[-1], 500)
                y_dense = spline(x_dense)
                base_points = list(zip(x_dense, y_dense))
            else:
                base_points = self.plot_canvas.points

            if base_points:
                x_final, y_final = zip(*base_points)
            else:
                return

        # Draw envelope and save lines for future clearing
        upper_line, = self.plot_canvas.axes.plot(x_final, y_final, 'r--', label='Envelope Upper')
        lower_line, = self.plot_canvas.axes.plot(x_final, -np.array(y_final), 'b--', label='Envelope Lower')

        # Save the lines so we can delete them next time
        self.plot_canvas.envelope_lines = [upper_line, lower_line]

        # Update legend
        self.plot_canvas.axes.legend()
        self.plot_canvas.draw()

    def vibration_window_save(self):
        if hasattr(self.plot_canvas, 'vibration_signal'):
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Vibration Waveform", "",
                                                       "Excel Files (*.xlsx);;All Files (*)",
                                                       options=QFileDialog.Options())
            if file_path:
                if not file_path.endswith(".xlsx"):
                    file_path += ".xlsx"

                try:
                    x_vib, y_vib = zip(*self.plot_canvas.vibration_signal)
                    df_vibration = pd.DataFrame({
                        'Sample': np.round(x_vib, 2),
                        'Amplitude': np.round(y_vib, 2)
                    })

                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        df_vibration.to_excel(writer, sheet_name='Vibration', index=False)

                    print(f"Vibration waveform saved successfully to {file_path}")

                except Exception as e:
                    print(f"Error saving vibration waveform: {e}")
                    QMessageBox.warning(self, "Save Error", str(e))
        else:
            QMessageBox.warning(self, "No Vibration Signal", "No vibration waveform to save. Please generate it first.")

    def generate_multi_frequency_vibration(self):
        try:
            sampling_rate = self.sampling_rate
            global_amp = self.amplitude_scale
            freqs_and_amps = self.multi_frequencies

            if not freqs_and_amps:
                raise ValueError("No frequencies selected for vibration.")

            if hasattr(self.plot_canvas, 'interpolated_points') and self.plot_canvas.interpolated_points:
                base_points = self.plot_canvas.interpolated_points
            else:
                base_points = self.plot_canvas.points

            if not base_points or len(base_points) < 2:
                raise ValueError("Need at least two points to generate vibration.")

            x_pts, y_pts = zip(*base_points)
            x_pts = np.array(x_pts)
            y_pts = np.array(y_pts)

            x_dense = np.linspace(x_pts.min(), x_pts.max(), int((x_pts.max() - x_pts.min()) * sampling_rate / 1000))

            if len(x_pts) >= 4 and all(np.diff(x_pts) > 0):
                spline = UnivariateSpline(x_pts, y_pts, k=3, s=0)
                y_dense = spline(x_dense)
            else:
                y_dense = np.interp(x_dense, x_pts, y_pts)

            self.plot_canvas.envelope_x = x_dense
            self.plot_canvas.envelope_y = y_dense

            # vibration = np.zeros_like(x_dense)
            # for freq, amp in freqs_and_amps:
            #     vibration += amp * np.sin(2 * np.pi * freq * x_dense / sampling_rate)

            vibration = np.zeros_like(x_dense)
            for freq, amp in freqs_and_amps:
                vibration += amp * np.sin(2 * np.pi * freq * x_dense / sampling_rate)

            # Normalize vibration between -1 and 1
            max_vib = np.max(np.abs(vibration))
            if max_vib > 0:
                vibration = vibration / max_vib

            final_signal = y_dense * vibration * global_amp

            self.plot_canvas.vibration_signal = list(zip(x_dense, final_signal))

            self.plot_canvas.update_plot()
            if self.show_envelope:
                self.plot_envelope()
            self.plot_vibration_only()

        except Exception as e:
            print(f"Error generating multi-frequency vibration: {e}")
            QMessageBox.warning(self, "Vibration Generation Error", str(e))

    def perform_no_sampling(self):
        try:
            self.plot_canvas.no_sampling()  # Restore the original points, removing any downsampling
        except Exception as e:
            print(f"Error during no sampling: {e}")

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu('File')

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close_application)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu('Edit')

        edit_axis_action = QAction('Edit Axis Range/Ticks', self)
        edit_axis_action.triggered.connect(self.open_axis_settings_dialog)
        edit_menu.addAction(edit_axis_action)

        vibration_settings_action = QAction('Vibration Signal Settings', self)
        vibration_settings_action.triggered.connect(self.open_vibration_settings_window)
        edit_menu.addAction(vibration_settings_action)

        reset_action = QAction('Overall Reset', self)
        reset_action.setShortcut('Ctrl+R')
        reset_action.triggered.connect(self.overall_reset)
        edit_menu.addAction(reset_action)

    # Define the close_application method
    def close_application(self):
        self.close()


    def load_data_from_csv(self, file_path):
        try:
            # Read CSV file with custom formatting
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Process the angle line, extracting the part between the curly braces
            angle_line = lines[0].strip().split('=')[-1].strip().replace("{", "").replace("}", "")
            angle = np.array(list(map(float, angle_line.split(","))))

            # Process the amplitude line, extracting the part between the curly braces
            amplitude_line = lines[1].strip().split('=')[-1].strip().replace("{", "").replace("}", "")
            amplitude = np.array(list(map(float, amplitude_line.split(","))))

            return list(zip(angle, amplitude))

        except Exception as e:
            print(f"Error loading from CSV: {e}")
            return None

    def on_load_csv_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            points = self.load_data_from_csv(file_name)
            if points:
                # Set both points and original points to the loaded CSV data
                self.plot_canvas.points = points
                self.plot_canvas.original_points = points
                self.plot_canvas.update_plot()

                # Display the loaded CSV file's name in the QLineEdit
                self.loaded_file_line_edit.setText(file_name)


    # def perform_interpolation(self):
    #     points_per_degree = self.interpolation_factor_input.value()
    #     self.plot_canvas.interpolate_points(points_per_degree)

    def perform_interpolation(self):
        try:
            points_per_degree = self.interpolation_factor_input.value()

            # Ensure there are enough points for interpolation (at least 4 for cubic spline)
            if len(self.plot_canvas.points) < 4:
                raise ValueError("Not enough points for interpolation. At least 4 points are required.")

            # Perform the interpolation
            self.plot_canvas.interpolate_points(points_per_degree)

        except ValueError as e:
            print(f"Error during interpolation: {e}")  # Print the error message for debugging
            QMessageBox.warning(self, 'Interpolation Error', str(e))  # Show a warning to the user

    def clear_interpolation(self):
        # Clear the interpolated points and update the plot
        self.plot_canvas.interpolated_points = []  # Reset interpolated points to an empty list
        self.plot_canvas.update_plot()

    def save_data_to_excel(self, file_path):
        try:
            # Check if there are points to analyze
            if not self.plot_canvas.points:
                QMessageBox.warning(self, 'No Data', 'No data points available to save.')
                return

            # Extract angles and find the maximum angle
            angles = [p[0] for p in self.plot_canvas.points]
            max_angle = max(angles, default=0)

            # # Check if the maximum angle is less than 62 degrees
            # if max_angle < self.plot_canvas.right_bound:
            #     QMessageBox.warning(self, 'Angle Requirement', 'Please make sure to go beyond 62 degrees.')
            #     return

            # Debugging: Print the length of the interpolated points
            if hasattr(self.plot_canvas, 'interpolated_points'):
                print(f"Length of interpolated points before saving: {len(self.plot_canvas.interpolated_points)}")
            else:
                print("No interpolated points attribute found.")

            # # Check if interpolation has been done and if the interpolated points array size is large enough
            # if (not hasattr(self.plot_canvas, 'interpolated_points') or
            #         not self.plot_canvas.interpolated_points or
            #         len(self.plot_canvas.interpolated_points) < 620):  # Ensure interpolation has at least 620 points
            #     QMessageBox.warning(self, 'Interpolation Required',
            #                         'Please interpolate sufficiently before saving the data.')
            #     return

            # Initialize csv_file_path at the beginning to ensure it's always defined
            csv_file_path = file_path.replace('.xlsx', '_csv.csv')  # Assume .csv extension if saving fails

            # Create a Pandas Excel writer using openpyxl as the engine.
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Save interpolated points first to make it Sheet 1
                if hasattr(self.plot_canvas, 'interpolated_points') and self.plot_canvas.interpolated_points:
                    interpolated_data = {
                        'sample': [round(p[0], 2) for p in self.plot_canvas.interpolated_points],
                        'amplitude': [round(p[1], 2) for p in self.plot_canvas.interpolated_points]
                    }
                    df_interpolated = pd.DataFrame(interpolated_data)
                    df_interpolated.to_excel(writer, sheet_name='Interpolated Points', index=False)
                else:
                    print("No interpolated data found. Skipping that sheet.")

                # Save original points next, rounded to 2 decimal points
                original_data = {
                    'sample': [round(p[0], 2) for p in self.plot_canvas.points],
                    'amplitude': [round(p[1], 2) for p in self.plot_canvas.points]
                }
                df_original = pd.DataFrame(original_data)
                df_original.to_excel(writer, sheet_name='Original Points', index=False)

            #print(f"Data saved successfully to {file_path} and {csv_file_path}")
            print(f"Data saved successfully to {file_path}")
        except Exception as e:
            print(f"Error saving to Excel or CSV: {e}")

    def auto_adjust_axes(self):
        if not self.plot_canvas.points:
            return

        x_vals, y_vals = zip(*self.plot_canvas.points)
        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)

        # Add 5% margin
        x_margin = (x_max - x_min) * 0.05 if x_max != x_min else 1
        y_margin = (y_max - y_min) * 0.05 if y_max != y_min else 1
        x_min -= x_margin
        x_max += x_margin
        y_min -= y_margin
        y_max += y_margin

        # Round axis limits to nearest nice values
        x_min = round(x_min, 2)
        x_max = round(x_max, 2)
        y_min = round(y_min, 2)
        y_max = round(y_max, 2)

        # Compute rounded tick intervals (max 10 ticks)
        def compute_tick_interval(min_val, max_val):
            range_val = max_val - min_val
            raw_tick = range_val / 10
            magnitude = 10 ** np.floor(np.log10(raw_tick))
            tick = round(raw_tick / magnitude) * magnitude
            return round(tick, 2)

        x_tick = compute_tick_interval(x_min, x_max)
        y_tick = compute_tick_interval(y_min, y_max)

        self.plot_canvas.set_axis_limits(x_min, x_max, y_min, y_max)
        self.plot_canvas.set_tick_intervals(x_tick, y_tick)

    def save_data_to_csv(self, file_path):
        try:
            # Check if there are points to analyze
            if not self.plot_canvas.points:
                QMessageBox.warning(self, 'No Data', 'No data points available to save.')
                return

            # Extract angles and find the maximum angle
            angles = [p[0] for p in self.plot_canvas.points]
            max_angle = max(angles, default=0)

            # # Check if the maximum angle is less than 62 degrees
            # if max_angle < self.plot_canvas.right_bound:
            #     QMessageBox.warning(self, 'Angle Requirement',
            #                         'Please make sure the profile extends beyond 62 degrees.')
            #     return

            # Debugging: Print the length of the interpolated points
            if hasattr(self.plot_canvas, 'interpolated_points'):
                print(f"Length of interpolated points before saving: {len(self.plot_canvas.interpolated_points)}")
            else:
                print("No interpolated points attribute found.")

            # # Check if interpolation has been done and if the interpolated points array size is large enough
            # if (not hasattr(self.plot_canvas, 'interpolated_points') or
            #         not self.plot_canvas.interpolated_points or
            #         len(self.plot_canvas.interpolated_points) < 620):  # Ensure interpolation has at least 620 points
            #     QMessageBox.warning(self, 'Interpolation Required',
            #                         'Please perform sufficient interpolation before saving the data.')
            #     return

            # Prepare data for custom CSV format, rounded to 2 decimal points
            if hasattr(self.plot_canvas, 'interpolated_points') and self.plot_canvas.interpolated_points:
                angle_values = [round(p[0], 2) for p in self.plot_canvas.interpolated_points]
                amplitude_values = [round(p[1], 2) for p in self.plot_canvas.interpolated_points]
            else:
                angle_values = [round(p[0], 2) for p in self.plot_canvas.points]
                amplitude_values = [round(p[1], 2) for p in self.plot_canvas.points]

            # Construct CSV content manually with curly brackets
            csv_content = f"angle [] = {{{', '.join(map(str, angle_values))}}}\n"
            csv_content += f"amplitude [] = {{{', '.join(map(str, amplitude_values))}}}\n"

            # Save the custom CSV content to a file
            with open(file_path, 'w') as csv_file:
                csv_file.write(csv_content)

            # Print success message
            print(f"Data saved successfully to {file_path}")

        except Exception as e:
            print(f"Error saving to CSV: {e}")

    def on_save_csv_clicked(self):
        # First, check if there are points to analyze
        if not self.plot_canvas.points:
            QMessageBox.warning(self, 'No Data', 'No data points available to save.')
            return

        # Extract angles and find the maximum angle
        angles = [p[0] for p in self.plot_canvas.points]
        max_angle = max(angles, default=0)

        # # Check if the maximum angle is less than 62 degrees
        # if max_angle < self.plot_canvas.right_bound:
        #     QMessageBox.warning(self, 'Angle Requirement', 'Please make sure the profile extends beyond 62 degrees.')
        #     return

        # Check if interpolation has been done and if there are sufficient interpolated points
        # if not hasattr(self.plot_canvas, 'interpolated_points') or not self.plot_canvas.interpolated_points:
        #     QMessageBox.warning(self, 'Interpolation Required', 'Please perform interpolation before saving the data.')
        #     return

        # # Check if interpolation points are sufficient
        # if len(self.plot_canvas.interpolated_points) < 620:
        #     QMessageBox.warning(self, 'Insufficient Interpolation', 'Interpolation must generate at least 620 points.')
        #     return

        # Only show the save file dialog if all conditions above are satisfied
        fileName, _ = QFileDialog.getSaveFileName(self, "Save to CSV", "",
                                                  "CSV Files (*.csv);;All Files (*)",
                                                  options=QFileDialog.Options())
        if fileName:
            self.save_data_to_csv(fileName)

    def on_save_excel_clicked(self):
        # First, check if there are points to analyze
        if not self.plot_canvas.points:
            QMessageBox.warning(self, 'No Data', 'No data points available to save.')
            return

        # Extract angles and find the maximum angle
        angles = [p[0] for p in self.plot_canvas.points]
        max_angle = max(angles, default=0)

        # # Check if the maximum angle is less than 62 degrees
        # if max_angle < self.plot_canvas.right_bound:
        #     QMessageBox.warning(self, 'Angle Requirement', 'Please make sure to go beyond 62 degrees.')
        #     return

        # Check if interpolation has been done and if there are sufficient interpolated points
        # if not hasattr(self.plot_canvas, 'interpolated_points') or not self.plot_canvas.interpolated_points:
        #     QMessageBox.warning(self, 'Interpolation Required', 'Please perform interpolation before saving the data.')
        #     return

        # # Check if interpolation points are sufficient
        # if len(self.plot_canvas.interpolated_points) < 620:
        #     QMessageBox.warning(self, 'Insufficient Interpolation', 'Interpolation must generate at least 620 points.')
        #     return

        # Only show the save file dialog if all conditions above are satisfied
        fileName, _ = QFileDialog.getSaveFileName(self, "Save to Excel", "",
                                                  "Excel Files (*.xlsx);;All Files (*)",
                                                  options=QFileDialog.Options())
        if fileName:
            self.save_data_to_excel(fileName)

    def perform_downsampling(self):
        points_per_degree = self.downsampling_factor_input.value()
        self.plot_canvas.downsample_points(points_per_degree)

    def perform_upsampling(self):
        self.plot_canvas.upsample_points()

    def apply_smoothing(self, smoothing_enabled):
            smoothing_factor = self.smoothing_input.value() if smoothing_enabled else 0
            self.plot_canvas.apply_smoothing(smoothing_factor)


    def on_load_clicked(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "",
                                                  "Excel Files (*.xlsx);;All Files (*)",
                                                  options=options)
        if fileName:
            self.load_data_from_excel(fileName)

    def reset_plot(self):
        if hasattr(self.plot_canvas, 'original_points') and self.plot_canvas.original_points:
            # Reset to original points if available
            self.plot_canvas.points = self.plot_canvas.original_points[:]
        else:
            # Set to default point if no original data is available
            self.plot_canvas.points = [(0, 0)]

        self.plot_canvas.update_plot()  # Update to show the reset state
    def overall_reset(self):
        # Reset the application to its initial state
        self.plot_canvas.points = []  # Clear the points
        self.plot_canvas.original_points = []  # Clear original points
        self.plot_canvas.update_plot()  # Clear the plot
        self.loaded_file_line_edit.setText("No file loaded")  # Reset the loaded file text
        print("Overall Reset performed. All data has been cleared.")
        if hasattr(self.plot_canvas, 'original_points') and self.plot_canvas.original_points:
            # Reset to original points if available
            self.plot_canvas.points = self.plot_canvas.original_points[:]
        else:
            # Set to default point if no original data is available
            self.plot_canvas.points = [(0, 0)]

        self.plot_canvas.update_plot()  # Update to show the reset state


    def on_interpolation_clicked(self):
        self.plot_canvas.interpolate_points()

    def on_click(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.button == 1 and modifiers == Qt.ControlModifier:
            if event.xdata and event.ydata:
                self.plot_canvas.add_point(event.xdata, event.ydata)
                self.clear_envelope()  # clear after adding
        elif event.button == 1:  # Normal left click (select point to move)
            if event.xdata and event.ydata:
                self.selected_point = self.find_closest_point(event.xdata, event.ydata)
                self.plot_canvas.highlight_point(self.selected_point)

    def on_move(self, event):
        if event.button == 1 and self.selected_point:
            if event.xdata and event.ydata:
                new_point = (event.xdata, event.ydata)
                self.plot_canvas.move_point(self.selected_point, new_point)
                self.selected_point = new_point
                self.plot_canvas.highlight_point(self.selected_point)
                self.clear_envelope()  # clear after moving

    def on_release(self, event):
        if event.button == 1 and self.selected_point:
            pass  # No action needed on mouse release



    def load_data_from_excel(self, file_path):
        try:
            # First, read all sheet names
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names

            # Decide which sheet to load
            if "original points" in sheet_names:
                df = pd.read_excel(file_path, sheet_name="original points")
            else:
                df = pd.read_excel(file_path,
                                   sheet_name=sheet_names[0])  # Load the first sheet if "original points" is missing

            # Check if the DataFrame has at least two columns
            if df.shape[1] < 2:
                raise ValueError("Excel sheet must contain at least two columns (angle, amplitude)")

            # Take the first two columns as Angle and Amplitude
            points = list(zip(df.iloc[:, 0], df.iloc[:, 1]))  # iloc[:, 0] is the first column, iloc[:, 1] is the second

            # Store original points in both App and PlotCanvas
            self.original_points = points
            self.plot_canvas.original_points = points

            # Update the plot
            self.plot_canvas.points = points
            self.plot_canvas.update_plot()

            # Update the QLineEdit with the file name
            self.loaded_file_line_edit.setText(file_path)
            self.auto_adjust_axes()


        except Exception as e:
            print(f"Error loading from Excel: {e}")
            self.loaded_file_line_edit.setText("Error loading file")

    # save only original data

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Z and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.plot_canvas.undo()
            self.clear_envelope()  # clear after undo
        elif event.key() == Qt.Key_Delete and self.selected_point:
            self.plot_canvas.delete_point(self.selected_point)
            self.selected_point = None
            self.plot_canvas.plot_curve()
            self.clear_envelope()  # clear after delete

    def find_closest_point(self, x, y):
        if self.plot_canvas.points:
            return min(self.plot_canvas.points, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)
        return None

def main():
    app = QApplication(sys.argv)

    # Apply qtmodern styles
    qtmodern.styles.light(app)  # You can also use qtmodern.styles.dark(app) for dark theme

    ex = App()

    # Wrap the main window in qtmodern
    modern_window = qtmodern.windows.ModernWindow(ex)
    modern_window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
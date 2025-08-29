#!/usr/bin/env python3
"""
Thermal Camera Python Demo

This script demonstrates how to use the Python bindings for the P2/Tiny1C thermal camera.

Requirements:
- thermal_camera module (built from setup.py)
- numpy
- opencv-python (for visualization)
- matplotlib (for temperature visualization)

Usage:
    python3 thermal_camera_demo.py
"""

import sys
import time
import numpy as np
try:
    import thermal_camera
except ImportError:
    print("Error: thermal_camera module not found. Please build and install first:")
    print("python3 setup.py build_ext --inplace")
    sys.exit(1)

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    print("Warning: OpenCV not available. Image display disabled.")
    OPENCV_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Warning: Matplotlib not available. Temperature visualization disabled.")
    MATPLOTLIB_AVAILABLE = False


class ThermalCameraDemo:
    def __init__(self):
        self.camera = thermal_camera.ThermalCamera()
        self.temp_processor = thermal_camera.TemperatureProcessor()
        
    def initialize_camera(self):
        """Initialize and open the thermal camera"""
        print("Initializing thermal camera...")
        
        if not self.camera.open():
            print("Error: Failed to open thermal camera!")
            print("Please check:")
            print("1. Camera is connected via USB")
            print("2. User has permissions (try: sudo chmod 666 /dev/bus/usb/*/007)")
            print("3. No other applications are using the camera")
            return False
            
        width, height, fps = self.camera.get_camera_info()
        print(f"Camera opened successfully!")
        print(f"Resolution: {width}x{height}")
        print(f"FPS: {fps}")
        
        return True
    
    def start_streaming(self):
        """Start camera streaming"""
        print("Starting camera stream...")
        
        if not self.camera.start_stream():
            print("Error: Failed to start camera streaming!")
            return False
            
        print("Camera streaming started.")
        print("Note: For P2 series cameras, waiting 5 seconds for temperature data to stabilize...")
        time.sleep(5)  # Wait for temperature data to be ready
        
        return True
    
    def capture_single_frame(self):
        """Capture and analyze a single frame"""
        print("\n=== Capturing Single Frame ===")
        
        # Get temperature frame
        temp_frame = self.camera.get_temperature_frame()
        if temp_frame.size == 0:
            print("Error: Failed to get temperature frame")
            return
        
        print(f"Temperature frame shape: {temp_frame.shape}")
        print(f"Temperature range: {temp_frame.min()} - {temp_frame.max()} (raw values)")
        
        # Convert raw values to Celsius for display
        temp_celsius = np.vectorize(thermal_camera.temp_to_celsius)(temp_frame)
        print(f"Temperature range: {temp_celsius.min():.1f}°C - {temp_celsius.max():.1f}°C")
        
        # Get image frame if available
        image_frame = self.camera.get_image_frame()
        if image_frame.size > 0:
            print(f"Image frame shape: {image_frame.shape}")
        
        return temp_frame, image_frame, temp_celsius
    
    def analyze_temperatures(self, temp_frame):
        """Analyze temperatures at specific points and areas"""
        print("\n=== Temperature Analysis ===")
        
        height, width = temp_frame.shape
        center_x, center_y = width // 2, height // 2
        
        # Point temperature
        success, temp = self.temp_processor.get_point_temp(temp_frame, center_x, center_y)
        if success:
            print(f"Center point ({center_x}, {center_y}): {temp:.1f}°C")
        
        # Rectangle temperature (central 50x50 area)
        rect_size = min(50, width//4, height//4)
        rect_x = center_x - rect_size//2
        rect_y = center_y - rect_size//2
        
        success, max_temp, min_temp, avg_temp = self.temp_processor.get_rect_temp(
            temp_frame, rect_x, rect_y, rect_size, rect_size
        )
        if success:
            print(f"Central {rect_size}x{rect_size} area:")
            print(f"  Max: {max_temp:.1f}°C, Min: {min_temp:.1f}°C, Avg: {avg_temp:.1f}°C")
        
        # Line temperature (horizontal line through center)
        success, max_temp, min_temp, avg_temp = self.temp_processor.get_line_temp(
            temp_frame, 0, center_y, width-1, center_y
        )
        if success:
            print(f"Horizontal center line:")
            print(f"  Max: {max_temp:.1f}°C, Min: {min_temp:.1f}°C, Avg: {avg_temp:.1f}°C")
    
    def visualize_thermal_data(self, temp_celsius, image_frame):
        """Visualize thermal data using matplotlib and opencv"""
        if not MATPLOTLIB_AVAILABLE and not OPENCV_AVAILABLE:
            print("No visualization libraries available.")
            return
        
        if MATPLOTLIB_AVAILABLE:
            # Create thermal visualization
            fig, axes = plt.subplots(1, 2 if image_frame.size > 0 else 1, figsize=(12, 5))
            if image_frame.size == 0:
                axes = [axes]
            
            # Thermal image
            im1 = axes[0].imshow(temp_celsius, cmap='hot', interpolation='nearest')
            axes[0].set_title('Thermal Image')
            axes[0].set_xlabel('X (pixels)')
            axes[0].set_ylabel('Y (pixels)')
            plt.colorbar(im1, ax=axes[0], label='Temperature (°C)')
            
            # Visual image if available
            if image_frame.size > 0:
                # Convert BGR to RGB for matplotlib
                if len(image_frame.shape) == 3:
                    image_rgb = cv2.cvtColor(image_frame, cv2.COLOR_BGR2RGB)
                    axes[1].imshow(image_rgb)
                else:
                    axes[1].imshow(image_frame, cmap='gray')
                axes[1].set_title('Visual Image')
                axes[1].set_xlabel('X (pixels)')
                axes[1].set_ylabel('Y (pixels)')
            
            plt.tight_layout()
            plt.show()
        
        if OPENCV_AVAILABLE:
            # Create OpenCV visualization
            # Normalize thermal data for display
            temp_normalized = cv2.normalize(temp_celsius, None, 0, 255, cv2.NORM_MINMAX)
            temp_colored = cv2.applyColorMap(temp_normalized.astype(np.uint8), cv2.COLORMAP_JET)
            
            # Add temperature text overlay
            height, width = temp_celsius.shape
            center_temp = temp_celsius[height//2, width//2]
            cv2.putText(temp_colored, f"Center: {center_temp:.1f}C", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(temp_colored, f"Range: {temp_celsius.min():.1f}-{temp_celsius.max():.1f}C", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Thermal Camera', temp_colored)
            
            if image_frame.size > 0:
                cv2.imshow('Visual Camera', image_frame)
            
            print("Press any key in OpenCV window to continue...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
    def continuous_monitoring(self, duration=30):
        """Continuously monitor temperatures for specified duration"""
        print(f"\n=== Continuous Monitoring ({duration}s) ===")
        print("Press Ctrl+C to stop early")
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while time.time() - start_time < duration:
                temp_frame = self.camera.get_temperature_frame()
                if temp_frame.size == 0:
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                
                # Analyze every 10th frame
                if frame_count % 10 == 0:
                    temp_celsius = np.vectorize(thermal_camera.temp_to_celsius)(temp_frame)
                    height, width = temp_frame.shape
                    center_temp = temp_celsius[height//2, width//2]
                    
                    elapsed = time.time() - start_time
                    print(f"[{elapsed:6.1f}s] Frame {frame_count:4d}: "
                          f"Center={center_temp:6.1f}°C, "
                          f"Min={temp_celsius.min():6.1f}°C, "
                          f"Max={temp_celsius.max():6.1f}°C")
                
                time.sleep(0.1)  # Limit frame rate
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        print(f"Captured {frame_count} frames in {elapsed:.1f}s (avg {fps:.1f} FPS)")
    
    def run_demo(self):
        """Run the complete thermal camera demo"""
        print("=" * 50)
        print("Thermal Camera Python Demo")
        print("=" * 50)
        
        try:
            # Initialize camera
            if not self.initialize_camera():
                return False
            
            # Start streaming
            if not self.start_streaming():
                return False
            
            # Capture and analyze single frame
            temp_frame, image_frame, temp_celsius = self.capture_single_frame()
            if temp_frame is not None:
                self.analyze_temperatures(temp_frame)
                self.visualize_thermal_data(temp_celsius, image_frame)
            
            # Continuous monitoring
            response = input("\nRun continuous monitoring? (y/N): ").lower()
            if response.startswith('y'):
                duration = input("Duration in seconds (default 30): ")
                try:
                    duration = int(duration) if duration else 30
                except ValueError:
                    duration = 30
                self.continuous_monitoring(duration)
            
            return True
            
        except Exception as e:
            print(f"Error during demo: {e}")
            return False
        
        finally:
            # Cleanup
            print("\nCleaning up...")
            if self.camera.is_streaming():
                self.camera.stop_stream()
            if self.camera.is_open():
                self.camera.close()
            print("Demo completed.")


def main():
    """Main entry point"""
    demo = ThermalCameraDemo()
    success = demo.run_demo()
    
    if not success:
        print("\nDemo failed. Common issues:")
        print("1. Camera not connected or recognized")
        print("2. Permission issues (run with sudo or fix USB permissions)")
        print("3. Camera in use by another application")
        print("4. Missing libraries or incorrect installation")
        sys.exit(1)


if __name__ == "__main__":
    main()
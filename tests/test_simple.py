#!/usr/bin/env python3
"""
Simple test script for the thermal camera Python bindings
"""

import sys
import time
import numpy as np

try:
    import tiny_thermal_camera
except ImportError as e:
    print(f"Error importing tiny_thermal_camera: {e}")
    print("Make sure to build the extension first:")
    print("python3 setup.py build_ext --inplace")
    sys.exit(1)

def main():
    print("=== Thermal Camera Simple Test ===")
    
    # Create camera instance
    camera = tiny_thermal_camera.ThermalCamera()
    # TemperatureProcessor is a static class, no need to instantiate
    
    try:
        # Initialize camera system
        print("Initializing camera system...")
        if not camera.initialize():
            print("Failed to initialize camera system")
            return False
        
        # Get device list
        print("Getting device list...")
        success, devices = camera.get_device_list()
        if not success:
            print("Failed to get device list")
            return False
        
        print(f"Found {len(devices)} devices:")
        for i, device in enumerate(devices):
            print(f"  {i}: VID=0x{device['vid']:04X}, PID=0x{device['pid']:04X}, Name='{device['name']}'")
        
        # Open camera (look for our thermal camera)
        print("Opening thermal camera...")
        if not camera.open(vid=0x0BDA, pid=0x5840):
            print("Failed to open thermal camera")
            print("Make sure:")
            print("1. Camera is connected")
            print("2. USB permissions are correct")
            print("3. No other application is using the camera")
            return False
        
        print("Camera opened successfully!")
        
        # Get camera info
        width, height, fps = camera.get_camera_info()
        print(f"Camera info: {width}x{height} @ {fps} fps")
        
        # Start streaming
        print("Starting camera stream...")
        # The start_stream function now handles the 5-second wait and y16_preview_start command
        if not camera.start_stream(enable_temperature_mode=True, wait_seconds=5):
            print("Failed to start streaming")
            return False
        
        print("Camera streaming started and temperature mode enabled!")
        
        # Capture a few frames
        print("\nCapturing frames...")
        for frame_num in range(100):
            print(f"Capturing frame {frame_num + 1}/5...")
            
            raw_frame = camera.get_raw_frame()
            if raw_frame.size == 0:
                print("Failed to get frame")
                continue
            
            print(f"Raw frame shape: {raw_frame.shape}")
            print(f"Raw data range: {raw_frame.min()} - {raw_frame.max()}")
            
            # Convert to temperature
            temp_celsius = np.vectorize(tiny_thermal_camera.temp_to_celsius)(raw_frame)
            print(f"Temperature range: {temp_celsius.min():.1f}°C - {temp_celsius.max():.1f}°C")
            
            # Get center point temperature
            center_x, center_y = raw_frame.shape[1] // 2, raw_frame.shape[0] // 2
            success, center_temp = tiny_thermal_camera.TemperatureProcessor.get_point_temp(raw_frame, center_x, center_y)
            if success:
                print(f"Center temperature: {center_temp:.1f}°C")
            
            # Get area temperature statistics
            area_size = 20
            area_x = center_x - area_size // 2
            area_y = center_y - area_size // 2
            success, max_temp, min_temp, avg_temp = tiny_thermal_camera.TemperatureProcessor.get_rect_temp(
                raw_frame, area_x, area_y, area_size, area_size)
            if success:
                print(f"Central {area_size}x{area_size} area:")
                print(f"  Max: {max_temp:.1f}°C, Min: {min_temp:.1f}°C, Avg: {avg_temp:.1f}°C")
            
            print()
            time.sleep(0.5)
        
        print("Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    
    finally:
        # Cleanup
        print("Cleaning up...")
        if camera.is_streaming():
            camera.stop_stream()
        if camera.is_open():
            camera.close()
        print("Cleanup completed.")

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nTest failed. Check the error messages above.")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
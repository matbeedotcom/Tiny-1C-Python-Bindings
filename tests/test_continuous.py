#!/usr/bin/env python3
"""
Continuous monitoring script for thermal camera
Useful for testing temperature stabilization and real-time monitoring
"""

import sys
import time
import signal
import numpy as np
from datetime import datetime

try:
    import tiny_thermal_camera
except ImportError:
    print("Error: tiny_thermal_camera module not found")
    print("Run: ./build.sh")
    sys.exit(1)

# Global flag for clean shutdown
running = True

def signal_handler(sig, frame):
    global running
    print("\nShutdown signal received...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

def main():
    print("=== Thermal Camera Continuous Monitor ===")
    print("Press Ctrl+C to stop\n")
    
    camera = tiny_thermal_camera.ThermalCamera()
    
    try:
        # Initialize and open camera
        if not camera.initialize():
            print("Failed to initialize camera system")
            return False
        
        if not camera.open():
            print("Failed to open camera")
            return False
        
        width, height, fps = camera.get_camera_info()
        print(f"Camera: {width}x{height} @ {fps} fps")
        
        # Start streaming with temperature mode
        print("Starting stream (waiting for temperature mode)...")
        if not camera.start_stream(enable_temperature_mode=True, wait_seconds=5):
            print("Failed to start streaming")
            return False
        
        print("Monitoring started...\n")
        print("Time        | Frame | Center | Min    | Max    | Range  | Status")
        print("-" * 70)
        
        frame_count = 0
        start_time = time.time()
        temp_history = []
        
        while running:
            # Get frame
            raw_frame = camera.get_raw_frame()
            if raw_frame.size == 0:
                time.sleep(0.01)
                continue
            
            frame_count += 1
            current_time = time.time() - start_time
            
            # Convert to Celsius
            temp_celsius = np.vectorize(tiny_thermal_camera.temp_to_celsius)(raw_frame)
            
            # Calculate statistics
            center_y, center_x = temp_celsius.shape[0]//2, temp_celsius.shape[1]//2
            center_temp = temp_celsius[center_y, center_x]
            min_temp = temp_celsius.min()
            max_temp = temp_celsius.max()
            temp_range = max_temp - min_temp
            
            # Track center temperature history
            temp_history.append(center_temp)
            if len(temp_history) > 100:
                temp_history.pop(0)
            
            # Determine stability status
            if len(temp_history) >= 10:
                recent_std = np.std(temp_history[-10:])
                if recent_std < 0.5:
                    status = "STABLE"
                elif recent_std < 1.0:
                    status = "SETTLING"
                else:
                    status = "UNSTABLE"
            else:
                status = "WARMING"
            
            # Print status line
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{timestamp} | {frame_count:5d} | {center_temp:6.1f} | {min_temp:6.1f} | "
                  f"{max_temp:6.1f} | {temp_range:6.1f} | {status:8s}", end='\r')
            
            # Every 25 frames, print statistics and newline
            if frame_count % 25 == 0:
                avg_temp = np.mean(temp_history) if temp_history else 0
                std_temp = np.std(temp_history) if len(temp_history) > 1 else 0
                elapsed = time.time() - start_time
                actual_fps = frame_count / elapsed
                
                print(f"\n[Stats] Avg: {avg_temp:.1f}°C, StdDev: {std_temp:.2f}°C, "
                      f"FPS: {actual_fps:.1f}, Elapsed: {elapsed:.1f}s")
            
            # Frame rate limiting
            time.sleep(0.04)  # ~25 fps
        
        print("\n\n=== Final Statistics ===")
        print(f"Total frames: {frame_count}")
        print(f"Total time: {time.time() - start_time:.1f}s")
        print(f"Average FPS: {frame_count/(time.time() - start_time):.1f}")
        if temp_history:
            print(f"Temperature range observed: {min(temp_history):.1f}°C - {max(temp_history):.1f}°C")
            print(f"Average temperature: {np.mean(temp_history):.1f}°C")
            print(f"Standard deviation: {np.std(temp_history):.2f}°C")
        
        return True
        
    except Exception as e:
        print(f"\nError: {e}")
        return False
    
    finally:
        print("\nCleaning up...")
        if camera.is_streaming():
            camera.stop_stream()
        if camera.is_open():
            camera.close()
        print("Cleanup complete.")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
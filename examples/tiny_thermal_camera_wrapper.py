#!/usr/bin/env python3
"""
Simple Python wrapper for thermal camera

This provides a simplified interface to the thermal camera with common use cases.
Handles DLL loading on Windows automatically.
"""

import numpy as np
import time
import os
import platform
from typing import Tuple, Optional, Union

def _setup_dll_path():
    """Add DLL directory to PATH on Windows"""
    if platform.system().lower() == 'windows':
        # Get the directory of this module
        module_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Determine architecture
        is_64bit = platform.machine().endswith('64')
        
        if is_64bit:
            dll_dir = os.path.join(module_dir, 'libs', 'win', 'x64', 'dll')
        else:
            dll_dir = os.path.join(module_dir, 'libs', 'win', 'Win32', 'dll')
        
        if os.path.exists(dll_dir):
            # Add DLL directory to PATH
            current_path = os.environ.get('PATH', '')
            if dll_dir not in current_path:
                os.environ['PATH'] = dll_dir + os.pathsep + current_path
            
            # For Python 3.8+, also use os.add_dll_directory
            if hasattr(os, 'add_dll_directory'):
                try:
                    os.add_dll_directory(dll_dir)
                except (OSError, AttributeError):
                    pass  # Fallback to PATH method
            
            print(f"Added DLL directory to search path: {dll_dir}")
        else:
            print(f"Warning: DLL directory not found: {dll_dir}")

# Setup DLL path before importing the extension
_setup_dll_path()

# Import the thermal camera extension
try:
    import tiny_thermal_camera
except ImportError:
    tiny_thermal_camera = None
    print("Warning: tiny_thermal_camera module not found. Please build first with:")
    print("python setup_crossplatform.py build_ext --inplace")


class TinyThermalCamera:
    """Simplified thermal camera interface"""
    
    def __init__(self):
        if tiny_thermal_camera is None:
            raise RuntimeError("tiny_thermal_camera module not available")
        
        self._camera = tiny_thermal_camera.ThermalCamera()
        self._temp_processor = tiny_thermal_camera.TemperatureProcessor()
        self._is_initialized = False
    
    def __enter__(self):
        """Context manager entry"""
        if not self.open():
            raise RuntimeError("Failed to open thermal camera")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def open(self) -> bool:
        """
        Open and initialize the thermal camera
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self._is_initialized:
            return True
        
        if self._camera.open():
            self._is_initialized = True
            return True
        return False
    
    def close(self) -> None:
        """Close the thermal camera"""
        if self._is_initialized:
            if self._camera.is_streaming():
                self._camera.stop_stream()
            self._camera.close()
            self._is_initialized = False
    
    def start_streaming(self, wait_for_stabilization: bool = True) -> bool:
        """
        Start camera streaming
        
        Args:
            wait_for_stabilization: If True, wait 5 seconds for P2 series temperature data
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._is_initialized:
            raise RuntimeError("Camera not initialized. Call open() first.")
        
        if self._camera.start_stream():
            if wait_for_stabilization:
                time.sleep(5)  # Wait for temperature data stabilization
            return True
        return False
    
    def stop_streaming(self) -> bool:
        """
        Stop camera streaming
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self._camera.stop_stream()
    
    def get_camera_info(self) -> Tuple[int, int, int]:
        """
        Get camera information
        
        Returns:
            Tuple[int, int, int]: (width, height, fps)
        """
        return self._camera.get_camera_info()
    
    def capture_frame(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Capture a single frame
        
        Returns:
            Tuple containing:
                - Temperature frame as numpy array (uint16) or None if failed
                - Image frame as numpy array (uint8) or None if not available
        """
        if not self._camera.is_streaming():
            raise RuntimeError("Camera not streaming. Call start_streaming() first.")
        
        temp_frame = self._camera.get_temperature_frame()
        image_frame = self._camera.get_image_frame()
        
        temp_frame = temp_frame if temp_frame.size > 0 else None
        image_frame = image_frame if image_frame.size > 0 else None
        
        return temp_frame, image_frame
    
    def get_temperature_celsius(self, temp_frame: np.ndarray) -> np.ndarray:
        """
        Convert raw temperature frame to Celsius
        
        Args:
            temp_frame: Raw temperature frame from capture_frame()
        
        Returns:
            np.ndarray: Temperature data in Celsius
        """
        return np.vectorize(tiny_thermal_camera.temp_to_celsius)(temp_frame)
    
    def get_point_temperature(self, temp_frame: np.ndarray, x: int, y: int) -> Optional[float]:
        """
        Get temperature at specific point
        
        Args:
            temp_frame: Raw temperature frame
            x, y: Pixel coordinates
        
        Returns:
            float: Temperature in Celsius, or None if failed
        """
        success, temp = self._temp_processor.get_point_temp(temp_frame, x, y)
        return temp if success else None
    
    def get_area_temperature(self, temp_frame: np.ndarray, x: int, y: int, 
                           width: int, height: int) -> Optional[Tuple[float, float, float]]:
        """
        Get temperature statistics for rectangular area
        
        Args:
            temp_frame: Raw temperature frame
            x, y: Top-left corner coordinates
            width, height: Rectangle dimensions
        
        Returns:
            Tuple[float, float, float]: (max_temp, min_temp, avg_temp) or None if failed
        """
        success, max_temp, min_temp, avg_temp = self._temp_processor.get_rect_temp(
            temp_frame, x, y, width, height)
        return (max_temp, min_temp, avg_temp) if success else None
    
    def get_line_temperature(self, temp_frame: np.ndarray, x1: int, y1: int, 
                           x2: int, y2: int) -> Optional[Tuple[float, float, float]]:
        """
        Get temperature statistics along a line
        
        Args:
            temp_frame: Raw temperature frame
            x1, y1: Start point coordinates
            x2, y2: End point coordinates
        
        Returns:
            Tuple[float, float, float]: (max_temp, min_temp, avg_temp) or None if failed
        """
        success, max_temp, min_temp, avg_temp = self._temp_processor.get_line_temp(
            temp_frame, x1, y1, x2, y2)
        return (max_temp, min_temp, avg_temp) if success else None
    
    def find_hotspot(self, temp_frame: np.ndarray) -> Tuple[Tuple[int, int], float]:
        """
        Find the hottest point in the temperature frame
        
        Args:
            temp_frame: Raw temperature frame
        
        Returns:
            Tuple containing:
                - (x, y) coordinates of hottest point
                - Temperature in Celsius
        """
        temp_celsius = self.get_temperature_celsius(temp_frame)
        max_idx = np.unravel_index(np.argmax(temp_celsius), temp_celsius.shape)
        y, x = max_idx  # numpy uses (row, col) indexing
        max_temp = temp_celsius[max_idx]
        
        return (x, y), max_temp
    
    def find_coldspot(self, temp_frame: np.ndarray) -> Tuple[Tuple[int, int], float]:
        """
        Find the coldest point in the temperature frame
        
        Args:
            temp_frame: Raw temperature frame
        
        Returns:
            Tuple containing:
                - (x, y) coordinates of coldest point
                - Temperature in Celsius
        """
        temp_celsius = self.get_temperature_celsius(temp_frame)
        min_idx = np.unravel_index(np.argmin(temp_celsius), temp_celsius.shape)
        y, x = min_idx  # numpy uses (row, col) indexing
        min_temp = temp_celsius[min_idx]
        
        return (x, y), min_temp
    
    def get_temperature_stats(self, temp_frame: np.ndarray) -> dict:
        """
        Get comprehensive temperature statistics
        
        Args:
            temp_frame: Raw temperature frame
        
        Returns:
            dict: Temperature statistics including min, max, mean, std, etc.
        """
        temp_celsius = self.get_temperature_celsius(temp_frame)
        
        return {
            'min': float(np.min(temp_celsius)),
            'max': float(np.max(temp_celsius)),
            'mean': float(np.mean(temp_celsius)),
            'median': float(np.median(temp_celsius)),
            'std': float(np.std(temp_celsius)),
            'range': float(np.max(temp_celsius) - np.min(temp_celsius)),
        }
    
    @property
    def is_open(self) -> bool:
        """Check if camera is open"""
        return self._is_initialized
    
    @property
    def is_streaming(self) -> bool:
        """Check if camera is streaming"""
        return self._camera.is_streaming() if self._is_initialized else False


# Convenience functions for quick usage
def quick_capture() -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Quick capture function - opens camera, captures frame, closes camera
    
    Returns:
        Tuple[Optional[np.ndarray], Optional[np.ndarray]]: (temp_frame, image_frame)
    """
    try:
        with TinyThermalCamera() as camera:
            if camera.start_streaming():
                return camera.capture_frame()
    except Exception as e:
        print(f"Quick capture failed: {e}")
    
    return None, None


def quick_temperature_at_point(x: int, y: int) -> Optional[float]:
    """
    Quick function to get temperature at specific point
    
    Args:
        x, y: Pixel coordinates
    
    Returns:
        Optional[float]: Temperature in Celsius or None if failed
    """
    temp_frame, _ = quick_capture()
    if temp_frame is not None:
        try:
            with TinyThermalCamera() as camera:
                return camera.get_point_temperature(temp_frame, x, y)
        except Exception:
            pass
    return None


# Example usage
if __name__ == "__main__":
    print("Simple Thermal Camera Test")
    
    try:
        with TinyThermalCamera() as camera:
            print("Camera opened successfully")
            
            width, height, fps = camera.get_camera_info()
            print(f"Camera info: {width}x{height} @ {fps}fps")
            
            if camera.start_streaming():
                print("Streaming started")
                
                # Capture a frame
                temp_frame, image_frame = camera.capture_frame()
                
                if temp_frame is not None:
                    print(f"Temperature frame shape: {temp_frame.shape}")
                    
                    # Get temperature statistics
                    stats = camera.get_temperature_stats(temp_frame)
                    print(f"Temperature stats: {stats}")
                    
                    # Find hotspot and coldspot
                    hot_pos, hot_temp = camera.find_hotspot(temp_frame)
                    cold_pos, cold_temp = camera.find_coldspot(temp_frame)
                    print(f"Hotspot: {hot_temp:.1f}°C at {hot_pos}")
                    print(f"Coldspot: {cold_temp:.1f}°C at {cold_pos}")
                
    except Exception as e:
        print(f"Error: {e}")
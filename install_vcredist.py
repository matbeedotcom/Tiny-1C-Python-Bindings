#!/usr/bin/env python3
"""
Auto-installer for Visual C++ Redistributable
Detects and silently installs required vcredist for thermal camera DLLs
"""

import os
import sys
import platform
import subprocess
import tempfile
import urllib.request
import winreg
from pathlib import Path

# Visual C++ Redistributable download URLs (Microsoft official links)
VCREDIST_URLS = {
    'x64': {
        'url': 'https://aka.ms/vs/17/release/vc_redist.x64.exe',
        'filename': 'vc_redist.x64.exe',
        'registry_key': r'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X64',
        'min_version': '14.0'
    },
    'x86': {
        'url': 'https://aka.ms/vs/17/release/vc_redist.x86.exe', 
        'filename': 'vc_redist.x86.exe',
        'registry_key': r'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X86',
        'min_version': '14.0'
    }
}

def is_admin():
    """Check if running with administrator privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_architecture():
    """Get system architecture"""
    arch = platform.machine().lower()
    if arch in ['amd64', 'x86_64']:
        return 'x64'
    elif arch in ['x86', 'i386', 'i686']:
        return 'x86'
    else:
        return 'x64'  # Default to x64

def check_vcredist_installed(arch='x64'):
    """Check if Visual C++ Redistributable is installed"""
    try:
        config = VCREDIST_URLS[arch]
        
        # Check registry
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, config['registry_key']) as key:
            try:
                installed, _ = winreg.QueryValueEx(key, 'Installed')
                version, _ = winreg.QueryValueEx(key, 'Version')
                
                if installed == 1:
                    print(f"Found Visual C++ Redistributable {arch}: {version}")
                    return True
            except FileNotFoundError:
                pass
                
    except Exception as e:
        print(f"Registry check failed: {e}")
    
    # Alternative check: Look for common vcruntime DLLs in system32
    system32 = Path(os.environ.get('SYSTEMROOT', 'C:\\Windows')) / 'System32'
    vcruntime_dlls = [
        'msvcp140.dll',
        'vcruntime140.dll',
        'vcruntime140_1.dll'
    ]
    
    found_dlls = []
    for dll in vcruntime_dlls:
        dll_path = system32 / dll
        if dll_path.exists():
            found_dlls.append(dll)
    
    if found_dlls:
        print(f"Found vcruntime DLLs: {', '.join(found_dlls)}")
        return len(found_dlls) >= 2  # Need at least msvcp140 and vcruntime140
    
    return False

def download_file(url, filename, temp_dir):
    """Download file from URL"""
    filepath = os.path.join(temp_dir, filename)
    
    print(f"Downloading {filename}...")
    try:
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded * 100) // total_size
                        print(f"\rProgress: {percent}%", end='', flush=True)
        
        print(f"\nDownloaded: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Download failed: {e}")
        return None

def install_vcredist(filepath):
    """Install Visual C++ Redistributable silently"""
    print(f"\nInstalling Visual C++ Redistributable...")
    
    try:
        # Silent installation flags:
        # /S or /silent = Silent install
        # /q = Quiet mode (no UI)
        # /norestart = Don't restart after installation
        cmd = [filepath, '/install', '/quiet', '/norestart']
        
        print(f"Running: {' '.join(cmd)}")
        
        # Run the installer
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("[SUCCESS] Visual C++ Redistributable installed successfully!")
            return True
        elif result.returncode == 1638:
            print("[SUCCESS] Visual C++ Redistributable already installed (newer version)")
            return True
        elif result.returncode == 3010:
            print("[SUCCESS] Visual C++ Redistributable installed (reboot required)")
            print("  Note: You may need to restart Windows for changes to take effect")
            return True
        else:
            print(f"[ERROR] Installation failed with exit code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Installation timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"[ERROR] Installation error: {e}")
        return False

def elevate_and_retry():
    """Restart script with administrator privileges"""
    print("\nAdministrator privileges required for installation.")
    print("Attempting to restart with elevated permissions...")
    
    try:
        import ctypes
        # Re-run this script as administrator
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            f'"{__file__}"', 
            None, 
            1  # SW_SHOWNORMAL
        )
        return True
    except Exception as e:
        print(f"Failed to elevate: {e}")
        return False

def main():
    """Main installation function"""
    if platform.system().lower() != 'windows':
        print("Visual C++ Redistributable is only required on Windows")
        return True
    
    print("=== Visual C++ Redistributable Auto-Installer ===\n")
    
    arch = get_architecture()
    print(f"System architecture: {arch}")
    
    # Check if already installed
    if check_vcredist_installed(arch):
        print("[OK] Visual C++ Redistributable is already installed")
        return True
    
    print("[MISSING] Visual C++ Redistributable not found")
    
    # Check admin privileges
    if not is_admin():
        print("[WARNING] Administrator privileges required for installation")
        response = input("Attempt to install with elevated privileges? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            return elevate_and_retry()
        else:
            print("Installation cancelled by user")
            return False
    
    # Download and install
    config = VCREDIST_URLS[arch]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\nUsing temporary directory: {temp_dir}")
        
        # Download vcredist
        filepath = download_file(config['url'], config['filename'], temp_dir)
        if not filepath:
            return False
        
        # Install vcredist
        if not install_vcredist(filepath):
            return False
    
    # Verify installation
    print("\nVerifying installation...")
    if check_vcredist_installed(arch):
        print("[SUCCESS] Installation verified successfully!")
        return True
    else:
        print("[ERROR] Installation verification failed")
        return False

def check_and_install():
    """Convenience function for other modules"""
    if platform.system().lower() != 'windows':
        return True
        
    arch = get_architecture()
    if not check_vcredist_installed(arch):
        print("Visual C++ Redistributable required for thermal camera DLLs")
        return main()
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n" + "="*50)
        print("INSTALLATION FAILED")
        print("="*50)
        print("Manual installation options:")
        print("1. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("2. Run as administrator: vc_redist.x64.exe /install /quiet")
        print("3. Or install Visual Studio with C++ tools")
        sys.exit(1)
    else:
        print("\n" + "="*50)
        print("INSTALLATION COMPLETED")
        print("="*50)
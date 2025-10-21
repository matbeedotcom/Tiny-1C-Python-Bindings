# Thermal Camera Utility Tools

Essential tools for camera setup, diagnostics, and troubleshooting.

## 🚀 Quick Start

**First-time setup on Windows:**
```batch
SETUP_WINDOWS.bat
```

**Having issues? Run troubleshooter:**
```batch
python tools/troubleshoot.py
```

---

## 📁 Available Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **`SETUP_WINDOWS.bat`** | Complete first-time setup wizard | First time on new computer |
| **`troubleshoot.py`** | All-in-one diagnostic & troubleshooting | Camera not working, need help |
| **`install_driver.py`** | WinUSB driver installation | Need to install/fix driver |

That's it! Just 3 tools that do everything you need.

---

## 🔧 Tool Details

### SETUP_WINDOWS.bat
**Complete automated setup for Windows**

Runs from the command line and guides you through:
1. Checking Python installation
2. Building the package (if needed)
3. Checking for camera hardware
4. Installing WinUSB driver
5. Testing the camera

**Usage:**
```batch
# From project root
setup.bat

# Or directly from tools/
tools\SETUP_WINDOWS.bat
```

**When to use:** First time setting up on a new computer

---

### troubleshoot.py
**All-in-one diagnostic and troubleshooting tool**

Interactive menu with options to:
- **Quick Diagnostics** - Check everything at once
- **Check Driver Status** - Verify WinUSB driver (Windows)
- **Test Camera** - Try to connect to camera
- **Install/Fix Driver** - Launch driver installer
- **Generate Bug Report** - Create detailed report for GitHub issues
- **Open GitHub Issues** - Submit a bug report

**Usage:**
```bash
python tools/troubleshoot.py
```

**When to use:**
- Camera not working
- Need to diagnose issues
- Want to report a bug
- Need guided troubleshooting

**Features:**
- Interactive menu system
- Comprehensive diagnostics
- Automated bug report generation
- Direct integration with GitHub issues
- Platform-aware (Windows/Linux)

---

### install_driver.py
**WinUSB driver installation tool**

Automates driver installation:
- Downloads Zadig automatically
- Checks current driver status
- Launches Zadig with step-by-step instructions
- Verifies installation
- Provides troubleshooting guidance

**Usage:**
```bash
python tools/install_driver.py
```

**When to use:**
- First time setup (driver needed)
- Switching from libusbK to WinUSB
- Driver installation failed
- Camera detected but can't open

**Requires:** Administrator privileges (will prompt for elevation)

**Platform:** Windows only (Linux doesn't need this)

---

## 🎯 Common Workflows

### First-Time Setup (Windows)
```batch
# Just run this!
setup.bat
```

The batch script handles everything automatically.

---

### Camera Not Working

**Step 1: Run troubleshooter**
```bash
python tools/troubleshoot.py
```

Select option 1 (Quick Diagnostics) - it will:
- Check your Python environment
- Verify package installation
- Check driver status (Windows)
- Test camera connection
- Tell you exactly what's wrong

**Step 2: Follow the recommendations**

The troubleshooter will suggest specific fixes, like:
- Install package if missing
- Install WinUSB driver if needed
- Check USB connection if camera not found

---

### Just Need to Install/Fix Driver

**Quick method:**
```bash
python tools/install_driver.py
```

Follows these steps:
1. Checks if camera is detected
2. Checks current driver
3. Downloads Zadig
4. Guides you through installation
5. Verifies installation succeeded

---

### Need to Report a Bug

**Step 1: Generate report**
```bash
python tools/troubleshoot.py
```

Select option 5 (Generate Bug Report)

**Step 2: Review the report**

The tool creates `thermal_camera_bug_report.txt` with:
- System information
- Package status
- Driver status (Windows)
- Camera test results

**Step 3: Submit to GitHub**

From troubleshooter, select option 6 (Open GitHub Issues)

Or manually visit GitHub and attach the report file.

---

## 📝 Detailed Command Reference

### SETUP_WINDOWS.bat

```batch
SETUP_WINDOWS.bat
```

**Options:** None (fully automated)

**Output:**
- Success: Camera ready to use
- Failure: Specific error message with next steps

---

### troubleshoot.py

```bash
python tools/troubleshoot.py
```

**Interactive Menu:**
1. Quick Diagnostics - Run all checks
2. Check Driver Status - Windows driver verification
3. Test Camera Connection - Try to open camera
4. Install/Fix WinUSB Driver - Launch installer
5. Generate Bug Report - Create diagnostic report
6. Open GitHub Issues - Submit bug report

**Options:** Menu-driven (no command-line arguments)

**Output Files:**
- `thermal_camera_bug_report.txt` - Bug report (option 5)

---

### install_driver.py

```bash
python tools/install_driver.py
```

**Requirements:**
- Windows only
- Administrator privileges
- Internet connection (downloads Zadig)

**What it does:**
1. Checks admin privileges (elevates if needed)
2. Detects camera and current driver
3. Downloads Zadig (~2MB)
4. Launches Zadig with instructions
5. Verifies WinUSB installation

**Exit codes:**
- 0: Success (driver installed)
- 1: Failure (see error message)

---

## 💡 Tips & Best Practices

### For New Users
1. **Start with setup.bat** - Handles everything automatically
2. **If issues arise, use troubleshoot.py** - Interactive diagnostics
3. **Read the messages** - Tools provide specific guidance

### For Driver Issues
1. **Check driver first:** `python tools/troubleshoot.py` → Option 2
2. **If wrong driver, fix it:** `python tools/install_driver.py`
3. **Verify after install:** Run troubleshooter again

### For Reporting Bugs
1. **Generate report first:** Use troubleshoot.py option 5
2. **Include all details:** Attach the `.txt` file
3. **Add screenshots:** Device Manager, error messages, etc.

---

## 🆘 Still Having Issues?

If these tools don't solve your problem:

1. **Run full diagnostics:**
   ```bash
   python tools/troubleshoot.py
   # Select option 1 (Quick Diagnostics)
   ```

2. **Generate bug report:**
   ```bash
   python tools/troubleshoot.py
   # Select option 5 (Generate Bug Report)
   ```

3. **Create GitHub issue:**
   - Use troubleshooter option 6, or
   - Manually visit GitHub Issues
   - Attach the bug report file
   - Include any screenshots

4. **Provide:**
   - Bug report file
   - Device Manager screenshot (Windows)
   - Python version: `python --version`
   - OS version
   - What you were trying to do

---

## 🔗 Related Documentation

- [Main README](../README.md) - Full project documentation
- [Windows Setup Guide](../WINDOWS_SETUP_GUIDE.md) - Detailed Windows instructions
- [Quick Reference](../QUICK_REFERENCE.md) - One-page cheat sheet

---

## 🐞 Tool Development

These tools are part of the Tiny-1C-Python-Bindings project.

**Contributing:**
- Tools are written in Python 3.7+
- Should work cross-platform (Windows/Linux)
- Follow existing error message style
- Test on fresh Windows install if possible

**Questions?** Open an issue on GitHub.

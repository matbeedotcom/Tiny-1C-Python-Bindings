# Release Guide

This guide explains how to create and publish pre-compiled wheel releases for the `tiny-thermal-camera` package.

## Overview

Pre-compiled wheels eliminate the need for users to have C++ build tools installed. The project uses:
- **cibuildwheel** - Automated wheel building for multiple platforms/Python versions
- **GitHub Actions** - CI/CD pipeline for automated builds
- **PyPI** - Package distribution

## Automated Release Process (Recommended)

### Prerequisites

1. **PyPI Account Setup**
   ```bash
   # Create account at https://pypi.org/account/register/
   # Generate API token at https://pypi.org/manage/account/token/
   ```

2. **GitHub Secrets Configuration**
   - Go to your repository settings
   - Navigate to Secrets and variables → Actions
   - Add secret: `PYPI_API_TOKEN` with your PyPI API token

### Creating a Release

1. **Update Version Number**
   ```bash
   # Edit pyproject.toml
   version = "1.0.1"  # Increment version
   ```

2. **Commit Changes**
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 1.0.1"
   git push
   ```

3. **Create and Push Tag**
   ```bash
   # Create a version tag
   git tag v1.0.1
   git push origin v1.0.1
   ```

4. **Automated Build Process**
   - GitHub Actions automatically triggers on tag push
   - Builds wheels for:
     - **Windows**: Python 3.8-3.12 (x64)
     - **Linux**: Python 3.8-3.12 (x86_64, aarch64)
   - Publishes to PyPI automatically
   - Creates GitHub Release with wheel attachments

5. **Verify Release**
   ```bash
   # After ~20-30 minutes, verify on PyPI
   pip install tiny-thermal-camera==1.0.1
   ```

## Manual Release Process

For testing or when automation is not available:

### Build Wheels Locally

#### Windows
```bash
# Install cibuildwheel
pip install cibuildwheel delvewheel

# Build wheels for all Python versions
python -m cibuildwheel --platform windows --output-dir dist

# Or build for current Python only
pip install build
python -m build --wheel
```

#### Linux
```bash
# Install cibuildwheel
pip install cibuildwheel

# Build wheels (uses Docker for manylinux)
python -m cibuildwheel --platform linux --output-dir dist

# For ARM cross-compilation, see cross_compile.sh
```

### Upload to PyPI

```bash
# Install twine
pip install twine

# Upload wheels and source distribution
twine upload dist/*

# Or upload to TestPyPI first
twine upload --repository testpypi dist/*
```

## What Gets Built

### Wheel Matrix

| Platform | Architectures | Python Versions | Wheel Name Pattern |
|----------|---------------|-----------------|-------------------|
| Windows  | x64 (AMD64)   | 3.8, 3.9, 3.10, 3.11, 3.12 | `*-win_amd64.whl` |
| Linux    | x86_64        | 3.8, 3.9, 3.10, 3.11, 3.12 | `*-manylinux*_x86_64.whl` |
| Linux    | aarch64       | 3.8, 3.9, 3.10, 3.11, 3.12 | `*-manylinux*_aarch64.whl` |

### Example Wheel Names
```
tiny_thermal_camera-1.0.0-cp311-cp311-win_amd64.whl
tiny_thermal_camera-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl
tiny_thermal_camera-1.0.0-cp310-cp310-manylinux_2_17_aarch64.whl
```

## Library Bundling

### Windows (delvewheel)
Automatically bundles these DLLs into wheels:
- `libiruvc.dll`, `libirtemp.dll`, `libirprocess.dll`, `libirparse.dll`
- `pthreadVC2.dll`
- `msvcp140.dll`, `vcruntime140.dll` (if needed)

### Linux (auditwheel)
Automatically bundles these libraries into wheels:
- `libiruvc.a`, `libirtemp.a`, `libirprocess.a`, `libirparse.a`
- System libraries are statically linked

Users can install without having these libraries on their system!

## Testing Wheels Before Release

### Test on TestPyPI

```bash
# Build wheels
python -m cibuildwheel --output-dir dist

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    tiny-thermal-camera
```

### Local Testing

```bash
# Build wheel
pip install build
python -m build --wheel

# Install locally
pip install dist/tiny_thermal_camera-*.whl

# Test import
python -c "import tiny_thermal_camera; print('Success!')"
```

## Release Checklist

- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG updated (if you have one)
- [ ] All tests passing locally
- [ ] Clean working directory (`git status`)
- [ ] Committed and pushed to main branch
- [ ] Created and pushed version tag (`git tag v1.x.x`)
- [ ] GitHub Actions build succeeded
- [ ] Wheels uploaded to PyPI
- [ ] GitHub Release created
- [ ] Verified installation: `pip install tiny-thermal-camera==1.x.x`
- [ ] Tested basic functionality on fresh install

## Troubleshooting

### Build Failures

**Check GitHub Actions logs:**
- Go to Actions tab in your repository
- Click on the failing workflow
- Examine build logs for errors

**Common issues:**
1. Missing library files - Ensure `libs/` directory is committed
2. DLL bundling fails - Check delvewheel/auditwheel versions
3. ARM build fails - QEMU setup issue, may need to disable ARM builds initially

### Upload Failures

**PyPI upload errors:**
```bash
# Verify package before upload
twine check dist/*

# Common fix: remove old builds
rm -rf dist/ build/ *.egg-info
python -m build --wheel
```

**Authentication errors:**
```bash
# Use API token (not password)
# Create token at https://pypi.org/manage/account/token/

# Configure .pypirc
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE
EOF
```

## Continuous Deployment

The GitHub Actions workflow automatically:
1. Builds wheels on every push to `main`
2. Uploads artifacts for testing
3. Publishes to PyPI only on version tags (`v*`)
4. Creates GitHub releases with wheel attachments

### Workflow Triggers

- **Push to main** - Build wheels, save as artifacts (7 day retention)
- **Pull requests** - Build wheels for testing
- **Tag push (v*)** - Build + publish to PyPI + create GitHub release
- **Manual trigger** - Workflow dispatch for on-demand builds

## Version Management

We use [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

## Support

For questions or issues with releases:
- Check GitHub Actions logs
- Review [cibuildwheel documentation](https://cibuildwheel.readthedocs.io/)
- Open an issue on GitHub

## References

- [Python Packaging Guide](https://packaging.python.org/)
- [cibuildwheel Documentation](https://cibuildwheel.readthedocs.io/)
- [PyPI Help](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)

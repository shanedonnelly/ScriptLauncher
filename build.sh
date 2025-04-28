#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Step 0: Cleaning up previous builds..."
rm -rf build/ dist/ __pycache__ ScriptLauncher.spec

# Step 1: Install dependencies
echo "Step 1: Installing dependencies..."
pip install -r requirements.txt

# Step 2: Locate the Python shared library
echo "Step 2: Locating libpython3.12.so.1.0..."
LIBPYTHON_PATH=$(ldconfig -p | grep libpython3.12.so.1.0 | awk '{print $NF}' | head -n1)

if [ -z "$LIBPYTHON_PATH" ]; then
    echo "Error: libpython3.12.so.1.0 not found. Please install the python3.12-dev package."
    echo "You can install it using: sudo apt-get install python3.12-dev"
    exit 1
fi

echo "Found libpython3.12.so.1.0 at $LIBPYTHON_PATH"

# Step 3: Build the executable with PyInstaller, including assets and the Python shared library
echo "Step 3: Building the executable with PyInstaller..."
pyinstaller --onefile \
            --add-data "assets/app_icons:assets/app_icons" \
            --add-binary "$LIBPYTHON_PATH:." \
            ScriptLauncher.py

# Step 4: Prepare the build directory
echo "Step 4: Preparing the build directory..."
mkdir -p build/assets/app_icons

# Step 5: Remove existing build/ScriptLauncher if it exists
if [ -e "build/ScriptLauncher" ]; then
    echo "Removing existing build/ScriptLauncher..."
    rm -rf build/ScriptLauncher
fi

# Step 6: Copy the executable to the build directory
echo "Step 6: Copying the executable to the build directory..."
cp dist/ScriptLauncher build/

# Step 7: Copy the assets to the build directory
echo "Step 7: Copying assets to the build directory..."
cp -r assets/app_icons build/assets/

cp icon.png build/

# Step 8: Clean up unnecessary files
echo "Step 8: Cleaning up unnecessary files..."
rm -rf dist __pycache__ *.spec

# Step 9: Verify the contents of the build directory
echo "Step 9: Verifying the build directory contents..."
ls -l build/
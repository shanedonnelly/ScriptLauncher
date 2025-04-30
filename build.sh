#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
APP_NAME_PKG="scriptlauncher" # Lowercase package name
APP_NAME_EXEC="ScriptLauncher" # Capitalized executable name (from PyInstaller --name)
VERSION="1.0"
ARCH="amd64" # Adjust if building for a different architecture
MAINTAINER="Shane Donnelly shaneboss34@gmail.com" # !!! CHANGE THIS !!!
EMAIL="shaneboss34@gmail.com" # !!! CHANGE THIS !!!
DESCRIPTION="A simple application to launch scripts and macros."
ENTRY_POINT="main.py"
ICON_FILE="icon.png"
REQUIREMENTS_FILE="requirements.txt"

# --- Directories ---
BUILD_DIR="debian_build"
DIST_DIR="dist" # PyInstaller output dir
FINAL_DEB_FILE="${APP_NAME_PKG}_${VERSION}_${ARCH}.deb"

# --- Script Start ---
echo "Starting Build Process for ${APP_NAME_EXEC} v${VERSION}"

# 1. Clean previous builds
echo "Cleaning previous build artifacts..."
rm -rf "${DIST_DIR}" build "${APP_NAME_EXEC}.spec" "${BUILD_DIR}" "${FINAL_DEB_FILE}"

# 2. Check for Virtual Environment (Optional but recommended)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Not running in a Python virtual environment. Dependencies will be installed globally or user-wide."
    # Uncomment the line below to enforce virtual environment usage
    # exit 1
fi

# 3. Install Dependencies
echo "Installing dependencies from ${REQUIREMENTS_FILE} and PyInstaller..."
pip install --upgrade pip
pip install -r "${REQUIREMENTS_FILE}" pyinstaller

# 4. Build Standalone Executable with PyInstaller
echo "Running PyInstaller..."
pyinstaller --noconfirm \
    --onefile \
    --windowed \
    --name "${APP_NAME_EXEC}" \
    --icon="${ICON_FILE}" \
    --add-data="assets:assets" \
    --add-data="presets:presets_default" \
    "${ENTRY_POINT}"

# Verify PyInstaller output
if [ ! -f "${DIST_DIR}/${APP_NAME_EXEC}" ]; then
    echo "PyInstaller build failed. Executable not found in ${DIST_DIR}/"
    exit 1
fi
echo "PyInstaller build successful: ${DIST_DIR}/${APP_NAME_EXEC}"

# 5. Prepare .deb Structure
echo "Creating .deb directory structure in ${BUILD_DIR}..."
mkdir -p "${BUILD_DIR}/DEBIAN"
mkdir -p "${BUILD_DIR}/usr/local/bin"
mkdir -p "${BUILD_DIR}/usr/share/applications"
mkdir -p "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps"

# 6. Create DEBIAN/control file
echo "Creating DEBIAN/control file..."
cat << EOF > "${BUILD_DIR}/DEBIAN/control"
Package: ${APP_NAME_PKG}
Version: ${VERSION}
Architecture: ${ARCH}
Maintainer: ${MAINTAINER}
Description: ${DESCRIPTION}
Depends: libc6
EOF

# 7. Create .desktop file
echo "Creating .desktop file..."
cat << EOF > "${BUILD_DIR}/usr/share/applications/${APP_NAME_PKG}.desktop"
[Desktop Entry]
Version=1.0
Name=${APP_NAME_EXEC}
Comment=${DESCRIPTION}
Exec=/usr/local/bin/${APP_NAME_PKG}
Icon=${APP_NAME_PKG}
Terminal=false
Type=Application
Categories=Utility;
EOF

# 8. Copy Files into Structure
echo "Copying application files..."
# Copy executable and rename to lowercase package name for consistency in bin
cp "${DIST_DIR}/${APP_NAME_EXEC}" "${BUILD_DIR}/usr/local/bin/${APP_NAME_PKG}"
# Copy icon and rename to lowercase package name
cp "${ICON_FILE}" "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME_PKG}.png"

# 9. Set Permissions
echo "Setting executable permissions..."
chmod +x "${BUILD_DIR}/usr/local/bin/${APP_NAME_PKG}"

# 10. Build the .deb Package
echo "Building .deb package..."
fakeroot dpkg-deb --build "${BUILD_DIR}" "${FINAL_DEB_FILE}"

# --- Script End ---
echo "-----------------------------------------------------"
echo "Build Complete!"
echo "Standalone executable: ${DIST_DIR}/${APP_NAME_EXEC}"
echo "Debian package: ${FINAL_DEB_FILE}"
echo "-----------------------------------------------------"
echo "To install: sudo apt install ./${FINAL_DEB_FILE}"

exit 0
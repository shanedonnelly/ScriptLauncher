#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
APP_NAME_PKG="scriptlauncher" # Lowercase package name
APP_NAME_EXEC="ScriptLauncher" # Capitalized executable name (from PyInstaller --name)
VERSION="1.0.0-beta" # <-- UPDATE THIS VERSION FOR A NEW RELEASE
ARCH="amd64" # Adjust if building for a different architecture
MAINTAINER="Shane Donnelly shaneboss34@gmail.com"
EMAIL="shaneboss34@gmail.com"
DESCRIPTION="A simple application to launch scripts and macros."
ENTRY_POINT="main.py"
ICON_FILE="icon.png"
REQUIREMENTS_FILE="requirements.txt"
GITHUB_REPO="shanedonnelly/ScriptLauncher" # GitHub repository for release creation

# --- Release Flag ---
CREATE_RELEASE=false
if [[ "$1" == "-release" ]]; then
    CREATE_RELEASE=true
    echo "Release flag detected. Will attempt to create Git tag and GitHub release if version changed."
fi

# --- Directories ---
BUILD_DIR="debian_build"
DIST_DIR="dist" # PyInstaller output dir
FINAL_DEB_FILE="${APP_NAME_PKG}_${VERSION}_${ARCH}.deb"

# --- Version Check ---
PREVIOUS_VERSION=""
# Find the latest existing .deb file matching the pattern
LATEST_DEB=$(ls -t ${APP_NAME_PKG}_*_${ARCH}.deb 2>/dev/null | head -n 1)

if [[ -n "$LATEST_DEB" ]] && [[ -f "$LATEST_DEB" ]]; then
    # Extract version from filename: scriptlauncher_VERSION_amd64.deb
    PREVIOUS_VERSION=$(echo "$LATEST_DEB" | sed -n "s/${APP_NAME_PKG}_\(.*\)_${ARCH}\.deb/\1/p")
    echo "Found previous .deb: $LATEST_DEB with version: $PREVIOUS_VERSION"
else
    echo "No previous .deb file found."
fi

VERSION_CHANGED=false
if [[ "$VERSION" != "$PREVIOUS_VERSION" ]]; then
    VERSION_CHANGED=true
    echo "Version has changed: $PREVIOUS_VERSION -> $VERSION"
else
    echo "Version has not changed ($VERSION)."
fi

# --- Script Start ---
echo "Starting Build Process for ${APP_NAME_EXEC} v${VERSION}"

# 1. Clean previous builds (keep old .deb for version check until now)
echo "Cleaning previous build artifacts..."
rm -rf "${DIST_DIR}" build "${APP_NAME_EXEC}.spec" "${BUILD_DIR}"
# Only delete the specific deb we are about to build, if it exists
rm -f "${FINAL_DEB_FILE}"

# 2. Check for Virtual Environment (Optional but recommended)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Not running in a Python virtual environment."
fi

# 3. Install Dependencies
echo "Installing dependencies from ${REQUIREMENTS_FILE} and PyInstaller..."
pip install --upgrade pip > /dev/null
pip install -r "${REQUIREMENTS_FILE}" pyinstaller > /dev/null
echo "Dependencies installed."

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
cp "${DIST_DIR}/${APP_NAME_EXEC}" "${BUILD_DIR}/usr/local/bin/${APP_NAME_PKG}"
cp "${ICON_FILE}" "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME_PKG}.png"

# 9. Set Permissions
echo "Setting executable permissions..."
chmod +x "${BUILD_DIR}/usr/local/bin/${APP_NAME_PKG}"

# 10. Build the .deb Package
echo "Building .deb package..."
fakeroot dpkg-deb --build "${BUILD_DIR}" "${FINAL_DEB_FILE}"
echo ".deb package created: ${FINAL_DEB_FILE}"

# 11. Git Tagging and GitHub Release (Conditional)
if [[ "$CREATE_RELEASE" = true ]]; then
    echo "Attempting Git tag and GitHub release (version check bypassed)..."
    # ... release logic ...

    # Check for Git
    if ! command -v git &> /dev/null; then
        echo "Error: git command not found. Cannot create tag."
        exit 1
    fi
    # Check if in a git repo
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
        echo "Error: Not inside a Git repository. Cannot create tag."
        exit 1
    fi

    # Check for GitHub CLI (gh)
    if ! command -v gh &> /dev/null; then
        echo "Error: gh command not found. Install GitHub CLI to create releases."
        echo "See: https://cli.github.com/"
        exit 1
    fi
    # Check gh authentication status
    if ! gh auth status &> /dev/null; then
         echo "Error: Not logged into GitHub CLI (gh). Please run 'gh auth login'."
         exit 1
    fi

    GIT_TAG="v${VERSION}"
    echo "Checking if Git tag ${GIT_TAG} already exists..."
    if git rev-parse "${GIT_TAG}" >/dev/null 2>&1; then
        echo "Error: Git tag ${GIT_TAG} already exists. Cannot create release."
        exit 1
    fi

    echo "Creating Git tag ${GIT_TAG}..."
    git tag "${GIT_TAG}"
    echo "Pushing Git tag ${GIT_TAG} to origin..."
    git push origin "${GIT_TAG}"

    echo "Creating GitHub pre-release for tag ${GIT_TAG}..."
    gh release create "${GIT_TAG}" \
        "${FINAL_DEB_FILE}" \
        --repo "${GITHUB_REPO}" \
        --prerelease \
        --title "${APP_NAME_EXEC} v${VERSION}" \
        --notes "Automated pre-release build for v${VERSION}. Includes ${FINAL_DEB_FILE} for Debian/Ubuntu."

    if [ $? -eq 0 ]; then
        echo "GitHub pre-release created successfully."
    else
        echo "Error: Failed to create GitHub release. Check gh output above."
        # Optionally remove the tag if release failed?
        # git tag -d "${GIT_TAG}"
        # git push --delete origin "${GIT_TAG}"
        exit 1
    fi

else
    if [[ "$CREATE_RELEASE" = true ]] && [[ "$VERSION_CHANGED" = false ]]; then
        echo "Skipping Git tag and GitHub release because version did not change."
    elif [[ "$CREATE_RELEASE" = false ]]; then
        echo "Skipping Git tag and GitHub release (release flag not set)."
    fi
fi


# --- Script End ---
echo "-----------------------------------------------------"
echo "Build Complete!"
echo "Standalone executable: ${DIST_DIR}/${APP_NAME_EXEC}"
echo "Debian package: ${FINAL_DEB_FILE}"
echo "-----------------------------------------------------"
if [[ "$CREATE_RELEASE" = true ]] && [[ "$VERSION_CHANGED" = true ]]; then
    echo "GitHub pre-release created for tag ${GIT_TAG}."
else
    echo "To install locally: sudo apt install ./${FINAL_DEB_FILE}"
fi

exit 0
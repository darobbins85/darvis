#!/usr/bin/env bash
# Darvis Desktop Integration Installation Script
# This script installs Darvis as a proper desktop application
# Supports both Linux and macOS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect platform
PLATFORM="$(uname -s)"
IS_MACOS=false
IS_LINUX=false

if [ "$PLATFORM" = "Darwin" ]; then
    IS_MACOS=true
    echo -e "${GREEN}Detected: macOS${NC}"
elif [ "$PLATFORM" = "Linux" ]; then
    IS_LINUX=true
    echo -e "${GREEN}Detected: Linux${NC}"
else
    echo -e "${YELLOW}Unknown platform: $PLATFORM${NC}"
    echo "Proceeding with limited functionality..."
fi

echo ""
echo -e "${GREEN}Darvis Voice Assistant - Desktop Integration Setup${NC}"
echo "=================================================="

# Get the absolute path of the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_DIR="$PROJECT_DIR"

echo "Project directory: $PROJECT_DIR"
echo "Script directory: $SCRIPT_DIR"
echo ""

# Check if required files exist
echo -e "${YELLOW}Checking required files...${NC}"

if [ ! -f "$PROJECT_DIR/assets/darvis-logo.png" ]; then
    echo -e "${RED}Error: assets/darvis-logo.png not found in $PROJECT_DIR${NC}"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/launch-darvis.sh" ]; then
    echo -e "${RED}Error: launch-darvis.sh not found in $PROJECT_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All required files found${NC}"
echo ""

# Platform-specific installation
if [ "$IS_LINUX" = true ]; then
    install_linux
elif [ "$IS_MACOS" = true ]; then
    install_macos
else
    echo -e "${YELLOW}⚠️  Unsupported platform. Skipping desktop integration.${NC}"
    echo "You can still run Darvis manually with: $PROJECT_DIR/launch-darvis.sh"
fi

# Common setup for both platforms
install_common() {
    # Test launcher script
    echo -e "${YELLOW}Testing launcher script...${NC}"
    if [ -x "$PROJECT_DIR/launch-darvis.sh" ]; then
        echo -e "${GREEN}✓ Launcher script is executable${NC}"
    else
        chmod +x "$PROJECT_DIR/launch-darvis.sh"
        echo -e "${GREEN}✓ Made launcher script executable${NC}"
    fi
    
    # Test darvis module
    echo -e "${YELLOW}Testing Darvis module...${NC}"
    if [ -d "$PROJECT_DIR/venv" ]; then
        if ! "$PROJECT_DIR/venv/bin/python" -c "import darvis.config" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Could not import darvis module. Make sure to activate the virtual environment.${NC}"
        else
            echo -e "${GREEN}✓ Darvis module is importable${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Virtual environment not found. Please run: python3 -m venv venv${NC}"
    fi
}

install_linux() {
    echo -e "${YELLOW}Installing for Linux...${NC}"
    
    if [ ! -f "$PROJECT_DIR/darvis.desktop" ]; then
        echo -e "${RED}Error: darvis.desktop not found in $PROJECT_DIR${NC}"
        exit 1
    fi
    
    # Create application directory if it doesn't exist
    APP_DIR="$HOME/.local/share/applications"
    ICON_DIR="$HOME/.local/share/icons"
    
    echo -e "${YELLOW}Setting up directories...${NC}"
    mkdir -p "$APP_DIR"
    mkdir -p "$ICON_DIR"
    echo -e "${GREEN}✓ Directories ready${NC}"
    echo ""
    
    # Copy icon
    echo -e "${YELLOW}Installing application icon...${NC}"
    cp "$PROJECT_DIR/assets/darvis-logo.png" "$ICON_DIR/"
    echo -e "${GREEN}✓ Icon installed to $ICON_DIR${NC}"
    echo ""
    
    # Update desktop file paths
    echo -e "${YELLOW}Configuring desktop file...${NC}"
    DESKTOP_FILE="$APP_DIR/darvis.desktop"
    cp "$PROJECT_DIR/darvis.desktop" "$DESKTOP_FILE"
    
    # Update paths in desktop file using sed
    sed -i.bak "s|/home/david/Code/github/darobbins85/darvis|$PROJECT_DIR|g" "$DESKTOP_FILE"
    rm -f "$DESKTOP_FILE.bak"
    
    echo -e "${GREEN}✓ Desktop file installed to $APP_DIR${NC}"
    echo ""
    
    # Update desktop database
    echo -e "${YELLOW}Updating desktop database...${NC}"
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$APP_DIR" || true
        echo -e "${GREEN}✓ Desktop database updated${NC}"
    else
        echo -e "${YELLOW}⚠️  update-desktop-database not found (optional)${NC}"
    fi
    
    # Install common components
    install_common
    
    echo ""
    echo -e "${GREEN}🎉 Installation Complete!${NC}"
    echo ""
    echo "Darvis is now available in your application menu."
    echo ""
    echo "To launch manually:"
    echo "  $PROJECT_DIR/launch-darvis.sh"
    echo ""
    echo "Or find 'Darvis Voice Assistant' in your application menu."
    echo ""
    echo -e "${YELLOW}Note:${NC} You may need to log out and back in for the icon to appear,"
    echo "or run: killall -HUP gnome-panel unity-panel plasma-desktop"
    echo "depending on your desktop environment."
}

install_macos() {
    echo -e "${YELLOW}Installing for macOS...${NC}"
    
    # Create Application Support directory
    APP_SUPPORT_DIR="$HOME/Library/Application Support/Darvis"
    ICON_DIR="$APP_SUPPORT_DIR"
    
    echo -e "${YELLOW}Setting up directories...${NC}"
    mkdir -p "$APP_SUPPORT_DIR"
    echo -e "${GREEN}✓ Directories ready${NC}"
    echo ""
    
    # Copy icon
    echo -e "${YELLOW}Installing application icon...${NC}"
    cp "$PROJECT_DIR/assets/darvis-logo.png" "$ICON_DIR/"
    echo -e "${GREEN}✓ Icon installed to $ICON_DIR${NC}"
    echo ""
    
    # Create macOS app launcher script
    echo -e "${YELLOW}Creating macOS app launcher...${NC}"
    MACOS_APP_DIR="$APP_SUPPORT_DIR/Darvis.app"
    MACOS_CONTENTS="$MACOS_APP_DIR/Contents"
    MACOS_MACOS="$MACOS_CONTENTS/MacOS"
    
    mkdir -p "$MACOS_MACOS"
    
    # Create Info.plist
    cat > "$MACOS_CONTENTS/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Darvis</string>
    <key>CFBundleIdentifier</key>
    <string>com.darvis.voice-assistant</string>
    <key>CFBundleName</key>
    <string>Darvis Voice Assistant</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
EOF
    
    # Create the executable script
    cat > "$MACOS_MACOS/Darvis" << EOF
#!/bin/bash
cd "$PROJECT_DIR"
exec "$PROJECT_DIR/launch-darvis.sh"
EOF
    chmod +x "$MACOS_MACOS/Darvis"
    
    echo -e "${GREEN}✓ macOS app bundle created at $MACOS_APP_DIR${NC}"
    echo ""
    
    # Create symlink in Applications
    if [ -d "/Applications" ]; then
        echo -e "${YELLOW}Creating symlink in Applications...${NC}"
        ln -sf "$MACOS_APP_DIR" "/Applications/Darvis.app" 2>/dev/null || echo -e "${YELLOW}⚠️  Could not create symlink in /Applications (try with sudo)${NC}"
    fi
    
    # Install common components
    install_common
    
    echo ""
    echo -e "${GREEN}🎉 Installation Complete!${NC}"
    echo ""
    echo "Darvis has been installed as a macOS application."
    echo ""
    echo "To launch:"
    echo "  - Double-click Darvis.app in /Applications"
    echo "  - Or run: $PROJECT_DIR/launch-darvis.sh"
    echo ""
    echo "Note: On first launch, macOS may warn about the app being from an"
    echo "unidentified developer. Go to System Preferences > Security & Privacy"
    echo "to allow it."
}

# Run platform-specific installation
if [ "$IS_LINUX" = true ]; then
    install_linux
elif [ "$IS_MACOS" = true ]; then
    install_macos
else
    install_common
    echo ""
    echo -e "${YELLOW}Installation complete with limited functionality.${NC}"
    echo "You can still run Darvis manually with: $PROJECT_DIR/launch-darvis.sh"
fi

#!/usr/bin/env bash
# Darvis Desktop Integration Installation Script
# This script installs Darvis as a proper desktop application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

if [ ! -f "$PROJECT_DIR/darvis-logo.png" ]; then
    echo -e "${RED}Error: darvis-logo.png not found in $PROJECT_DIR${NC}"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/launch-darvis.sh" ]; then
    echo -e "${RED}Error: launch-darvis.sh not found in $PROJECT_DIR${NC}"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/darvis.desktop" ]; then
    echo -e "${RED}Error: darvis.desktop not found in $PROJECT_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All required files found${NC}"
echo ""

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
cp "$PROJECT_DIR/darvis-logo.png" "$ICON_DIR/"
echo -e "${GREEN}✓ Icon installed to $ICON_DIR${NC}"
echo ""

# Update desktop file paths
echo -e "${YELLOW}Configuring desktop file...${NC}"
DESKTOP_FILE="$APP_DIR/darvis.desktop"
cp "$PROJECT_DIR/darvis.desktop" "$DESKTOP_FILE"

# Update paths in desktop file
sed -i "s|/home/david/Code/github/darobbins85/darvis|$PROJECT_DIR|g" "$DESKTOP_FILE"

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

# Test launcher script
echo -e "${YELLOW}Testing launcher script...${NC}"
if [ -x "$PROJECT_DIR/launch-darvis.sh" ]; then
    echo -e "${GREEN}✓ Launcher script is executable${NC}"
else
    chmod +x "$PROJECT_DIR/launch-darvis.sh"
    echo -e "${GREEN}✓ Made launcher script executable${NC}"
fi

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
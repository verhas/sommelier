#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Building Sommelier...${NC}"

# 1. Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

# 2. Install/upgrade build tools
echo "Installing build dependencies..."
pip install --upgrade pip setuptools wheel build

# 3. Run tests
echo -e "${BLUE}Running tests...${NC}"
pip install -e ".[dev]"
pytest tests/ -v --cov=src/sommelier --cov-report=term-missing

# 4. Build distribution packages
echo -e "${BLUE}Building distributions...${NC}"
python -m build

# 5. Validate with twine
echo "Validating packages..."
pip install twine
twine check dist/*

echo -e "${GREEN}✓ Build successful!${NC}"
echo "Artifacts: $(ls -lh dist/)"

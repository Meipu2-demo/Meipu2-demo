#!/bin/bash

# External components download script for Meipu2-demo
# This script downloads contents (example), gene submodule, and dictation-kit

set -e

echo "Starting external components download..."

# Check if we're in the correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Please run this script from the Meipu2-demo root directory"
    exit 1
fi

# Function to download and extract
download_and_extract() {
    local filename="$1"
    local url="$2"
    local extract_name="$3"
    local target_name="$4"
    
    echo "Downloading $filename..."
    curl -L -o "$filename" "$url"
    
    # Use bsdtar which handles encoding better on macOS
    if command -v bsdtar >/dev/null 2>&1; then
        bsdtar -xf "$filename"
    else
        # Fallback to unzip with encoding handling
        export UNZIP="-O CP932"
        unzip -q "$filename" || {
            echo "Trying with different encoding..."
            export UNZIP="-O UTF-8"
            unzip -q "$filename" 2>/dev/null || true
        }
    fi
    
    # Move and rename
    if [ -n "$target_name" ] && [ -d "$extract_name" ]; then
        if [ -d "$target_name" ]; then
            rm -rf "$target_name"
        fi
        mv "$extract_name" "$target_name"
    fi
    
    # Clean up
    rm "$filename"
    echo "Setup complete for $target_name"
}

# contentsをダウンロード・展開
download_and_extract \
    "contents.zip" \
    "https://github.com/mmdagent-ex/example/archive/95e3a0b389be60d5c8fd0215684f82512cb81d36.zip" \
    "example-95e3a0b389be60d5c8fd0215684f82512cb81d36" \
    "contents"

# geneサブモジュールをダウンロード・展開
download_and_extract \
    "gene.zip" \
    "https://github.com/mmdagent-ex/gene/archive/c7eace43dffaccff6ad0597433ef85fa57c91e03.zip" \
    "gene-c7eace43dffaccff6ad0597433ef85fa57c91e03" \
    "contents/gene"

# dictation-kitをダウンロード・展開
download_and_extract \
    "dictation-kit.zip" \
    "https://github.com/julius-speech/dictation-kit/archive/1ceb4dec245ef482918ca33c55c71d383dce145e.zip" \
    "dictation-kit-1ceb4dec245ef482918ca33c55c71d383dce145e" \
    "dictation-kit"

echo "All external components downloaded successfully!"

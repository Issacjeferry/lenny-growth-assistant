#!/usr/bin/env bash
set -e

mkdir -p data/raw
cd data/raw
if [ -d "lennys-podcast-transcripts" ]; then
    echo "Transcripts already downloaded. Pulling latest..."
    cd lennys-podcast-transcripts
    git pull
else
    echo "Cloning transcripts repository..."
    git clone https://github.com/ChatPRD/lennys-podcast-transcripts.git
fi

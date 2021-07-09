#!/bin/bash
set -o errexit -o pipefail -o nounset

SAVE_PATH=${INPUT_SAVE_PATH}
GIF_NAME=${INPUT_GIF_NAME}

echo "_________ START GIF CREATION _________"

export HOME=/root

python3 /app/make_gif.py || cat /app/geckodriver.log

export HOME=/github/home

echo "_________ END GIF CREATION _________"

echo " - Saving GIF to ${SAVE_PATH} as ${GIF_NAME}.gif"

cp "/app/${GIF_NAME}.gif" "/github/workspace${SAVE_PATH}"

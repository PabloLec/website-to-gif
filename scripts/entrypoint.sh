#!/bin/bash
set -o errexit -o pipefail -o nounset

SAVE_PATH=${INPUT_SAVE_PATH}
FILE_NAME=${INPUT_FILE_NAME}
FORMAT=${INPUT_FILE_FORMAT}
LC_FORMAT="${FORMAT,,}"

echo "_________ START CAPTURE _________"

export HOME=/root

export PATH=$PATH:/app
python3 /app/make_gif.py || cat /app/geckodriver.log

cp /app/${FILE_NAME}.${LC_FORMAT} /dev/null # Verify presence of output file

export HOME=/github/home

echo "_________ FILE CREATED _________"

echo " - Saving file to ${SAVE_PATH} as ${FILE_NAME}.${LC_FORMAT}"

cp "/app/${FILE_NAME}.${LC_FORMAT}" "/github/workspace${SAVE_PATH}"

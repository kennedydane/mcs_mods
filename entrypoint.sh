#!/bin/bash
set -e

# --- Copy Custom Add-ons ---
echo ">>> Copying custom add-ons..."

# Copy behavior packs
BEHAVIOR_PACKS_DIR="/app/custom_addons/behavior_packs"
if [ -d "$BEHAVIOR_PACKS_DIR" ] && [ "$(ls -A $BEHAVIOR_PACKS_DIR)" ]; then
  echo "Found custom behavior packs, copying to server..."
  cp -r $BEHAVIOR_PACKS_DIR/* /app/behavior_packs/
else
  echo "No custom behavior packs found."
fi

# Copy resource packs
RESOURCE_PACKS_DIR="/app/custom_addons/resource_packs"
if [ -d "$RESOURCE_PACKS_DIR" ] && [ "$(ls -A $RESOURCE_PACKS_DIR)" ]; then
  echo "Found custom resource packs, copying to server..."
  cp -r $RESOURCE_PACKS_DIR/* /app/resource_packs/
else
  echo "No custom resource packs found."
fi

echo ">>> Add-on copy complete."
echo "----------------------------------------"

# --- Execute the main process passed as arguments ---
echo ">>> Starting main process..."
exec "$@"

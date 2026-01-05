#!/bin/bash
# Shell script to run the character loader unit test

echo "============================================"
echo "Running SoulLink Character Loader Tests..."
echo "============================================"

# Activate virtual environment if you have one
# source venv/bin/activate

python3 -m unittest tests/test_character_loader.py

echo
echo "Tests finished."

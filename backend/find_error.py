import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

with open('src/api/chat_api.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        if 'conversation_id' in line and ('int(' in line or 'Integer' in line):
            print(f'{i}: {line.strip()}')
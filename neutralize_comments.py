import os
import re

root = r'c:\Users\MW\Downloads\coding\PZ\Pulse\src\main\java'
modified_files = []

for dirpath, dirnames, filenames in os.walk(root):
    for filename in filenames:
        if filename.endswith('.java'):
            filepath = os.path.join(dirpath, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            new_lines = []
            changed = False
            for line in lines:
                stripped = line.lstrip()
                # Only modify comment lines
                if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
                    new_line = re.sub(r'\bEcho\b', 'profiler', line)
                    new_line = re.sub(r'\bFuse\b', 'optimizer', new_line)
                    new_line = re.sub(r'\bNerve\b', 'stabilizer', new_line)
                    if new_line != line:
                        changed = True
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)
            
            if changed:
                with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
                    f.write('\n'.join(new_lines))
                modified_files.append(filename)

print(f'Modified {len(modified_files)} files:')
for f in modified_files:
    print(f'  - {f}')

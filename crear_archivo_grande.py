import sys
import random

if len(sys.argv) != 3:
    print(f"uso: {sys.argv[0]} <archivo> <tamaño en Kb>")
    exit(1)


size = int(sys.argv[2]) * 1024

lines: list[str] = list()

for _ in range((size // 120) + 1):
    new_line: list[str] = list()

    for _ in range (120):
        new_line.append(chr(random.randint(33, 126)))

    lines.append(''.join(new_line))

text = '\n'.join(lines)

with open(sys.argv[1], 'w') as file:
    print(f"se escribieron {file.write(text)} bytes")



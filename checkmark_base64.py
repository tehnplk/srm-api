import base64

# Read the SVG file
with open('checkmark.svg', 'r', encoding='utf-8') as f:
    svg_content = f.read()

# Encode to base64
encoded = base64.b64encode(svg_content.encode('utf-8')).decode('ascii')
print(f"Base64 encoded: {encoded}")

# Test decode
decoded = base64.b64decode(encoded).decode('utf-8')
print(f"Decoded: {decoded}")

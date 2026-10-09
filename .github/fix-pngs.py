#!/usr/bin/env python3
"""Fix reapack-index bug: ensure all 13 PNGs are in index.xml for fma-sub-air."""
import re
import sys

PNGS = ['panel.png', 'knob_marron.png', 'knob_hueso.png', 'knob_naranja.png',
        'knob_rojo.png', 'knob_monobelow.png', 'toggle_2pos.png', 'mode_3pos.png',
        'power_2pos.png', 'led_verde_fs.png', 'led_amarillo_fs.png',
        'vu_face.png', 'vu_off.png']

with open('index.xml', 'r') as f:
    xml = f.read()

# Find all version blocks for fma-sub-air.jsfx
def fix_version(m):
    ver_block = m.group(0)
    ver_name = m.group(1)
    # Get commit from existing JSFX source
    src = re.search(r'raw/([a-f0-9]+)/FMA%20Series/fma-sub-air\.jsfx', ver_block)
    if not src:
        return ver_block
    commit = src.group(1)
    # Build full source list
    sources = [f'        <source>https://github.com/FMA-Series/fma-reapack/raw/{commit}/FMA%20Series/fma-sub-air.jsfx</source>']
    for png in PNGS:
        url = f"https://github.com/FMA-Series/fma-reapack/raw/{commit}/FMA%20Series/fma-sub-air_gfx/{png}"
        sources.append(f'        <source file="fma-sub-air_gfx/{png}">{url}</source>')
    # Replace existing sources in this version block
    # Find changelog end, then replace everything until </version>
    pattern = r'(<changelog>.*?</changelog>\n)(.*?)(\n      </version>)'
    def repl_sources(sm):
        return sm.group(1) + '\n'.join(sources) + sm.group(3)
    return re.sub(pattern, repl_sources, ver_block, flags=re.DOTALL)

# Apply to each reapack entry for fma-sub-air
pattern = r'(<reapack name="fma-sub-air\.jsfx".*?</reapack>)'
# Actually, fix each version within
xml = re.sub(r'<version name="([^"]+)"[^>]*>.*?</version>', 
             lambda m: fix_version(m) if 'fma-sub-air' in xml[max(0,m.start()-500):m.start()] else m.group(0),
             xml, flags=re.DOTALL)

# Simpler: fix all version blocks that contain fma-sub-air.jsfx source
def fix_all_versions(xml):
    # Find version blocks and check if they're for fma-sub-air
    parts = re.split(r'(<version name="[^"]+"[^>]*>.*?</version>)', xml, flags=re.DOTALL)
    result = []
    for part in parts:
        if part.startswith('<version') and 'fma-sub-air.jsfx' in part:
            # This is a fma-sub-air version, fix its sources
            src = re.search(r'raw/([a-f0-9]+)/FMA%20Series/fma-sub-air\.jsfx', part)
            if src:
                commit = src.group(1)
                sources = [f'        <source>https://github.com/FMA-Series/fma-reapack/raw/{commit}/FMA%20Series/fma-sub-air.jsfx</source>']
                for png in PNGS:
                    url = f"https://github.com/FMA-Series/fma-reapack/raw/{commit}/FMA%20Series/fma-sub-air_gfx/{png}"
                    sources.append(f'        <source file="fma-sub-air_gfx/{png}">{url}</source>')
                pattern = r'(<changelog>.*?</changelog>\n)(.*?)(\n      </version>)'
                part = re.sub(pattern, 
                             lambda sm: sm.group(1) + '\n'.join(sources) + sm.group(3),
                             part, flags=re.DOTALL)
        result.append(part)
    return ''.join(result)

xml = fix_all_versions(xml)

with open('index.xml', 'w') as f:
    f.write(xml)
print("index.xml fixed: all versions now have 13 PNGs")

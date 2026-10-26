#!/usr/bin/env python3
"""Fix reapack-index bug: ensure all 14 PNGs are in index.xml for fma-sub-air.

NOTE (2026-10-26): version blocks WITHOUT a <changelog> element (v1.7.1+,
which ships clean by the author's order) MUST also be fixed. The old
pattern required <changelog> to anchor the source replacement, so it
silently skipped changelog-less versions and v1.7.1 shipped with only
vu_off.png (the last @provides line, the one MetaHeader keeps) -- a
black GUI for everyone who updated. The fix below anchors on the
<version> tag itself and preserves the changelog only if present.
It also FAILS LOUDLY if any fma-sub-air version ends up missing PNGs,
so a broken index can never be committed silently again.

NOTE (2026-10-26, author's order): the plugin file itself carries NO
changelog, but the index entry MUST still show one -- synthesized,
very brief, only the concrete changes, no sophisticated explanations.
BRIEF_CHANGELOGS below holds those texts, keyed by version; the fix
injects them into changelog-less version blocks.
"""
import re
import sys


PNGS = ['panel.png', 'knob_marron.png', 'knob_hueso.png', 'knob_naranja.png',
        'knob_rojo.png', 'knob_monobelow.png', 'knob_lowcut.png', 'toggle_2pos.png', 'mode_3pos.png',
        'power_2pos.png', 'led_verde_fs.png', 'led_amarillo_fs.png',
        'vu_face.png', 'vu_off.png']

BRIEF_CHANGELOGS = {
    '1.7.1': 'v1.7.1 (2026-10-26)\n- Sin changelog dentro del archivo; aviso de licencia en cabecera.\n- Sonido identico a la v1.7.0, sin cambios de DSP.',
}

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
                # Anchor on the <version> tag itself, NOT on <changelog>:
                # changelog-less versions (v1.7.1+) must be fixed too.
                # Preserve the changelog block if one exists; otherwise
                # inject the brief synthesized changelog for this version.
                vm = re.match(r'(<version[^>]*>\s*)', part, flags=re.DOTALL)
                cm = re.search(r'<changelog>.*?</changelog>', part, flags=re.DOTALL)
                if cm:
                    keep = cm.group(0) + '\n'
                else:
                    ver = re.search(r'<version name="([^"]+)"', part).group(1)
                    brief = BRIEF_CHANGELOGS.get(ver)
                    keep = ('<changelog><![CDATA[' + brief + ']]></changelog>\n') if brief else ''
                part = vm.group(1) + keep + '\n'.join(sources) + '\n      </version>'
        result.append(part)
    return ''.join(result)

xml = fix_all_versions(xml)

# Fail loudly instead of publishing a broken index: every fma-sub-air
# version must list the jsfx + all 14 PNGs after the fix, and every
# version with a brief changelog must actually carry it.
for vm in re.finditer(r'<version name="([^"]+)"[^>]*>.*?</version>', xml, flags=re.DOTALL):
    block = vm.group(0)
    if 'fma-sub-air.jsfx' in block:
        missing = [p for p in PNGS if p not in block]
        if missing:
            print(f"ERROR: fma-sub-air version {vm.group(1)} is missing PNGs: {missing}", file=sys.stderr)
            sys.exit(1)
        if vm.group(1) in BRIEF_CHANGELOGS and '<changelog>' not in block:
            print(f"ERROR: fma-sub-air version {vm.group(1)} is missing its brief changelog", file=sys.stderr)
            sys.exit(1)

with open('index.xml', 'w') as f:
    f.write(xml)
print("index.xml fixed: all versions now have 14 PNGs")

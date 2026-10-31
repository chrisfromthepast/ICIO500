import base64
import os

art_dir = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611"

def to_b64(fname):
    p = os.path.join(art_dir, fname)
    with open(p, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")

b64_fp = to_b64("assembly_front_faceplate_v12_crop.png")
b64_top = to_b64("assembly_top_v12_crop.png")
b64_iso_hero = to_b64("assembly_iso_hero_v12_crop.png")
b64_iso_left = to_b64("assembly_iso_front_left_v12_crop.png")
b64_iso_right = to_b64("assembly_iso_front_right_v12_crop.png")
b64_side = to_b64("assembly_side_left_v12_crop.png")

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: flex; }}
    .active-btn {{
      background-color: var(--primary) !important;
      color: var(--primary-foreground) !important;
      border-color: var(--primary) !important;
    }}
  </style>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-2">
  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-xl p-4 shadow-sm max-w-4xl mx-auto">
    
    <!-- Title & Status Header -->
    <div class="flex flex-wrap items-center justify-between pb-3 border-b border-[var(--border)] gap-2">
      <div>
        <h2 class="text-base font-semibold text-[var(--foreground)] flex items-center gap-2">
          <span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          ICIO500 500-Series Chassis & Mechanical Assembly Verification (V12)
        </h2>
        <p class="text-xs text-[var(--muted-foreground)]">Symmetrical Frame Rail Centering • Würth SMD Brackets • Stripped Wordless Faceplate • Vertical Daisy Seed</p>
      </div>
      <div class="flex items-center gap-2 text-xs bg-[var(--background)] px-2.5 py-1 rounded-md border border-[var(--border)]">
        <span class="text-emerald-500 font-medium">✓ Centered Rail Mounting</span>
        <span class="text-[var(--border)]">|</span>
        <span class="text-emerald-500 font-medium">✓ Brackets Flush</span>
        <span class="text-[var(--border)]">|</span>
        <span class="text-emerald-500 font-medium">✓ Zero Words</span>
        <span class="text-[var(--border)]">|</span>
        <span class="text-emerald-500 font-medium">✓ 0 DRC Violations</span>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex flex-wrap gap-1.5 pt-3 pb-2 text-xs">
      <button onclick="selectTab('fp')" id="btn-fp" class="tab-btn active-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--secondary)]">
        🎛️ Front Faceplate (No Words)
      </button>
      <button onclick="selectTab('top')" id="btn-top" class="tab-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]">
        📐 Full Top Profile (Centered Rail Holes)
      </button>
      <button onclick="selectTab('iso-hero')" id="btn-iso-hero" class="tab-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]">
        🧊 Full 3D Assembly (Vertical Daisy)
      </button>
      <button onclick="selectTab('iso-left')" id="btn-iso-left" class="tab-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]">
        🔧 Würth SMD Brackets (Left ISO)
      </button>
      <button onclick="selectTab('iso-right')" id="btn-iso-right" class="tab-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]">
        🔌 Connector Mating (Right ISO)
      </button>
      <button onclick="selectTab('side')" id="btn-side" class="tab-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]">
        📏 Side Profile (Chassis Rail Overhang)
      </button>
    </div>

    <!-- Image Display Panes -->
    <div class="mt-2 relative rounded-lg overflow-hidden border border-[var(--border)] bg-black/20 flex items-center justify-center min-h-[500px]">
      
      <!-- Tab 1: Front Faceplate -->
      <div id="tab-fp" class="tab-content active flex-col items-center p-3 w-full">
        <img src="{b64_fp}" alt="Front Faceplate (No Words)" class="max-h-[520px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Authentic Minimalist Faceplate: Strictly Zero Words</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Stripped of all text (no GAIN, LEVEL, CLIP, dBu, WISPY AUDIO, or ICIO 500). Retains only the 10 numeric level indicators on the right (+20 to -25), 10 VU meter LED holes, encoder cutout, and chassis rail mounting holes.</p>
        </div>
      </div>

      <!-- Tab 2: Top Full -->
      <div id="tab-top" class="tab-content flex-col items-center p-3 w-full">
        <img src="{b64_top}" alt="Full Top View" class="max-h-[520px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">500-Series Chassis Centering (Card Edge Center Y = 102.75 mm)</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Faceplate is centered exactly on the backplane connector tongue. Symmetrical ~9.5 mm overhang top and bottom past the 4.500" carrier card. Chassis rail holes are at Y=40.035 mm and Y=165.465 mm (exact 4.938" / 125.43 mm rail spacing).</p>
        </div>
      </div>

      <!-- Tab 3: Full 3D Hero -->
      <div id="tab-iso-hero" class="tab-content flex-col items-center p-3 w-full">
        <img src="{b64_iso_hero}" alt="Full 3D Assembly" class="max-h-[520px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Complete Rigid Assembly with Vertical Daisy Seed U5</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Vertical Daisy Seed (at 95 90), carrier audio section, power supply, and satellite board firmly anchored to front faceplate.</p>
        </div>
      </div>

      <!-- Tab 4: Left ISO (Brackets) -->
      <div id="tab-iso-left" class="tab-content flex-col items-center p-3 w-full">
        <img src="{b64_iso_left}" alt="Würth SMD Mounting Brackets" class="max-h-[520px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Würth Elektronik 7466303 SMD Right-Angle Mounting Brackets</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Brackets soldered to B.Cu of satellite board mate flush into carrier card mounting holes MH1 and MH2 with M3 hardware.</p>
        </div>
      </div>

      <!-- Tab 5: Right ISO (Connector Mating) -->
      <div id="tab-iso-right" class="tab-content flex-col items-center p-3 w-full">
        <img src="{b64_iso_right}" alt="Connector Mating" class="max-h-[520px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Right-Angle Inter-Board Header Mating (U6 ⇄ J1)</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Right-angle 2x10 header U6 on carrier card engages 2x10 SMD socket J1 on satellite board, eliminating ribbon cable while maintaining 0 DRC errors.</p>
        </div>
      </div>

      <!-- Tab 6: Side Profile -->
      <div id="tab-side" class="tab-content flex-col items-center p-3 w-full">
        <img src="{b64_side}" alt="Side Profile View" class="max-h-[520px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Standard 500-Series Profile</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Front panel height 5.250" (133.35 mm), carrier card height 4.500" (114.30 mm). Top and bottom rail screw slots are located 0.156" (3.96 mm) from panel ends.</p>
        </div>
      </div>

    </div>

  </div>

  <script>
    function selectTab(tabId) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => {{
        el.classList.remove('active-btn');
        el.classList.remove('text-[var(--foreground)]');
        el.classList.add('text-[var(--muted-foreground)]');
      }});
      
      const targetTab = document.getElementById('tab-' + tabId);
      const targetBtn = document.getElementById('btn-' + tabId);
      if (targetTab) targetTab.classList.add('active');
      if (targetBtn) {{
        targetBtn.classList.add('active-btn');
        targetBtn.classList.remove('text-[var(--muted-foreground)]');
        targetBtn.classList.add('text-[var(--foreground)]');
      }}
    }}
  </script>
</body>
</html>'''

out_path = os.path.join(art_dir, "render_gallery.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated {out_path} ({len(html_content)} bytes)")

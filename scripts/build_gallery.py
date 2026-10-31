import base64
import os

art_dir = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611"

def to_b64(fname):
    p = os.path.join(art_dir, fname)
    with open(p, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")

b64_top_zoom = to_b64("v11_top_connector_crop.png")
b64_top_full = to_b64("v11_top_full_crop.png")
b64_iso_zoom = to_b64("v11_iso_connector_crop.png")
b64_iso_full = to_b64("v11_iso_full_crop.png")
b64_side = to_b64("v11_side_profile_crop.png")
b64_faceplate = to_b64("v11_faceplate_front_ui.png")

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
          ICIO500 Assembly Verification Gallery (V11)
        </h2>
        <p class="text-xs text-[var(--muted-foreground)]">4.500" VPR-500 Card Height • Centered Tongue • Symmetrical 25.8/26mm Notches • 0.000 mm Header Mating</p>
      </div>
      <div class="flex items-center gap-2 text-xs bg-[var(--background)] px-2.5 py-1 rounded-md border border-[var(--border)]">
        <span class="text-emerald-500 font-medium">✓ Y=[45.7, 160] mm</span>
        <span class="text-[var(--border)]">|</span>
        <span class="text-emerald-500 font-medium">✓ Symmetrical Notches</span>
        <span class="text-[var(--border)]">|</span>
        <span class="text-emerald-500 font-medium">✓ Zero Bottom Bulk</span>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex flex-wrap gap-1.5 pt-3 pb-2 text-xs">
      <button onclick="selectTab('top-zoom')" id="btn-top-zoom" class="tab-btn active-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--secondary)]">
        🔍 Connector Mating (U6 ⇄ J1)
      </button>
      <button onclick="selectTab('top-full')" id="btn-top-full" class="tab-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]">
        📐 Full Top Profile (Centered Tongue)
      </button>
      <button onclick="selectTab('faceplate')" id="btn-faceplate" class="tab-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]">
        🎛️ Front Faceplate UI
      </button>
      <button onclick="selectTab('iso-full')" id="btn-iso-full" class="tab-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]">
        🧊 Isometric 3D View
      </button>
      <button onclick="selectTab('iso-zoom')" id="btn-iso-zoom" class="tab-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]">
        🔎 ISO Mating Close-Up
      </button>
      <button onclick="selectTab('side')" id="btn-side" class="tab-btn px-3 py-1.5 rounded-lg font-medium transition bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]">
        📏 Side Profile (4.500" Spec)
      </button>
    </div>

    <!-- Image Display Panes -->
    <div class="mt-2 relative rounded-lg overflow-hidden border border-[var(--border)] bg-black/20 flex items-center justify-center min-h-[460px]">
      
      <!-- Tab 1: Top Zoom -->
      <div id="tab-top-zoom" class="tab-content active flex-col items-center p-3 w-full">
        <img src="{b64_top_zoom}" alt="Top Connector Mating" class="max-h-[500px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Header U6 & Socket J1 Concentric Mating (0.000 mm Offset)</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Right-angle header U6 is shifted to Y=131.905 mm on the carrier card. Pins align precisely with SMD socket J1 at Y=175.000 mm in satellite frame.</p>
        </div>
      </div>

      <!-- Tab 2: Top Full -->
      <div id="tab-top-full" class="tab-content flex-col items-center p-3 w-full">
        <img src="{b64_top_full}" alt="Full Top View" class="max-h-[500px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Symmetrical VPR-500 Outline with Centered Tongue</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Top notch: 25.80 mm (Y=45.70 to 71.50) • Tongue: 62.50 mm (Y=71.50 to 134.00) • Bottom notch: 26.00 mm (Y=134.00 to 160.00). Bottom edge baseline unchanged at Y=160.00 mm.</p>
        </div>
      </div>

      <!-- Tab 3: Faceplate -->
      <div id="tab-faceplate" class="tab-content flex-col items-center p-3 w-full">
        <img src="{b64_faceplate}" alt="Front Faceplate UI" class="max-h-[500px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Front Faceplate User Interface (Oriented Forward)</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Control layout facing forward with dual encoder scales, silkscreen labeling, and standard VPR mounting slots. Zero through-hole pin protrusion.</p>
        </div>
      </div>

      <!-- Tab 4: ISO Full -->
      <div id="tab-iso-full" class="tab-content flex-col items-center p-3 w-full">
        <img src="{b64_iso_full}" alt="Isometric 3D Module" class="max-h-[500px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Full 3D Module Isometric View</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Rigid 3-point mechanical assembly: Upper SMRA M3 bracket, lower SMRA M3 bracket, and central 20-pin interconnect header forming a rigid triangulated structure.</p>
        </div>
      </div>

      <!-- Tab 5: ISO Zoom -->
      <div id="tab-iso-zoom" class="tab-content flex-col items-center p-3 w-full">
        <img src="{b64_iso_zoom}" alt="ISO Mating Close-Up" class="max-h-[500px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Triangulated 3-Point Mating Interface</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Both 5mm threaded brackets mate concentrically with carrier mounting holes MH1 and MH2. Header pins enter socket J1 with standard 4.5mm engagement depth.</p>
        </div>
      </div>

      <!-- Tab 6: Side -->
      <div id="tab-side" class="tab-content flex-col items-center p-3 w-full">
        <img src="{b64_side}" alt="Side Profile" class="max-h-[500px] object-contain rounded drop-shadow" />
        <div class="mt-3 text-center">
          <p class="text-xs font-semibold text-[var(--foreground)]">Side Elevation Profile</p>
          <p class="text-[11px] text-[var(--muted-foreground)]">Total card height: 114.30 mm (4.500" VPR-500 standard). Module depth: 150.81 mm (5.938" standard). Bottom edge at Y=160.00 mm fits into standard rack card guides.</p>
        </div>
      </div>

    </div>

  </div>

  <script>
    function selectTab(tabId) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => {{
        el.classList.remove('active-btn');
        el.classList.add('text-[var(--muted-foreground)]');
      }});
      
      const target = document.getElementById('tab-' + tabId);
      const btn = document.getElementById('btn-' + tabId);
      if (target) target.classList.add('active');
      if (btn) {{
        btn.classList.add('active-btn');
        btn.classList.remove('text-[var(--muted-foreground)]');
      }}
    }}
  </script>
</body>
</html>
'''

out_path = os.path.join(art_dir, "render_gallery.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Interactive Render Gallery updated at: {out_path}")

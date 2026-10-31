from PIL import Image
import numpy as np
import os
import shutil

art_dir = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611"

def crop_content(img, pad=20):
    arr = np.array(img)
    mask = arr[:, :, 3] > 0
    coords = np.argwhere(mask)
    if len(coords) == 0:
        return img
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    y0 = max(0, y0 - pad)
    x0 = max(0, x0 - pad)
    y1 = min(arr.shape[0], y1 + pad)
    x1 = min(arr.shape[1], x1 + pad)
    return img.crop((x0, y0, x1, y1))

# 1. Top full crop
im_top = Image.open('views/assembly_top_v11.png')
crop_top_full = crop_content(im_top, pad=15)
crop_top_full.save('views/v11_top_full_crop.png')
shutil.copyfile('views/v11_top_full_crop.png', os.path.join(art_dir, 'v11_top_full_crop.png'))
print("Saved v11_top_full_crop.png")

# 2. Top connector & bracket mating close-up
crop_top_conn = im_top.crop((320, 200, 750, 700))
crop_top_conn.save('views/v11_top_connector_crop.png')
shutil.copyfile('views/v11_top_connector_crop.png', os.path.join(art_dir, 'v11_top_connector_crop.png'))
print("Saved v11_top_connector_crop.png")

# 3. ISO full crop
im_iso = Image.open('views/assembly_iso_front_v11.png')
crop_iso_full = crop_content(im_iso, pad=15)
crop_iso_full.save('views/v11_iso_full_crop.png')
shutil.copyfile('views/v11_iso_full_crop.png', os.path.join(art_dir, 'v11_iso_full_crop.png'))
print("Saved v11_iso_full_crop.png")

# 4. ISO connector mating close-up
crop_iso_conn = im_iso.crop((350, 150, 850, 700))
crop_iso_conn.save('views/v11_iso_connector_crop.png')
shutil.copyfile('views/v11_iso_connector_crop.png', os.path.join(art_dir, 'v11_iso_connector_crop.png'))
print("Saved v11_iso_connector_crop.png")

# 5. Side profile crop
im_side = Image.open('views/assembly_side_left_v11.png')
crop_side = crop_content(im_side, pad=15)
crop_side.save('views/v11_side_profile_crop.png')
shutil.copyfile('views/v11_side_profile_crop.png', os.path.join(art_dir, 'v11_side_profile_crop.png'))
print("Saved v11_side_profile_crop.png")

# 6. Faceplate front 3D crop (from assembly_front_faceplate_v11)
im_fp = Image.open('views/assembly_front_faceplate_v11.png')
crop_fp = crop_content(im_fp, pad=15)
crop_fp.save('views/v11_faceplate_crop.png')
shutil.copyfile('views/v11_faceplate_crop.png', os.path.join(art_dir, 'v11_faceplate_crop.png'))
print("Saved v11_faceplate_crop.png")

# 7. Faceplate direct 3D crop (from assembly_faceplate_direct)
im_fp_dir = Image.open('views/assembly_faceplate_direct.png')
crop_fp_dir = crop_content(im_fp_dir, pad=15)
crop_fp_dir.save('views/v11_faceplate_direct_crop.png')
shutil.copyfile('views/v11_faceplate_direct_crop.png', os.path.join(art_dir, 'v11_faceplate_direct_crop.png'))
print("Saved v11_faceplate_direct_crop.png")

# 8. Faceplate Front UI (authentic direct PCB render with full silkscreen, VU meter, labels, encoder dial)
im_ui = Image.open('views/faceplate_front_ui.png')
crop_ui = crop_content(im_ui, pad=15)
crop_ui.save('views/v11_faceplate_front_ui.png')
shutil.copyfile('views/v11_faceplate_front_ui.png', os.path.join(art_dir, 'v11_faceplate_front_ui.png'))
print("Saved v11_faceplate_front_ui.png")

print("All v11 crops saved and copied to artifacts directory!")

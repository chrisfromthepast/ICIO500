from PIL import Image
import os
import shutil

artifact_dir = r"C:\Users\Chris Williams\.gemini\antigravity\brain\27d96d43-0ba0-4cfa-ba0b-2ac48d075611"

# 1. Top view connector crop:
im_top = Image.open('views/assembly_top_v10.png')
# Dimensions (1568, 872)
# Front mating zone is roughly X in [380, 750], Y in [250, 650]
crop_top = im_top.crop((380, 250, 750, 650))
crop_top.save('views/v10_top_connector_crop.png')
shutil.copyfile('views/v10_top_connector_crop.png', os.path.join(artifact_dir, 'v10_top_connector_crop.png'))

# 2. ISO view connector & bracket crop:
im_iso = Image.open('views/assembly_iso_front_v10.png')
crop_iso = im_iso.crop((380, 180, 850, 700))
crop_iso.save('views/v10_iso_connector_crop.png')
shutil.copyfile('views/v10_iso_connector_crop.png', os.path.join(artifact_dir, 'v10_iso_connector_crop.png'))

# 3. Direct front faceplate crop:
im_fp = Image.open('views/assembly_front_faceplate_v10.png')
crop_fp = im_fp.crop((300, 50, 1150, 850))
crop_fp.save('views/v10_faceplate_crop.png')
shutil.copyfile('views/v10_faceplate_crop.png', os.path.join(artifact_dir, 'v10_faceplate_crop.png'))

print("All v10 crops generated and copied to artifacts!")

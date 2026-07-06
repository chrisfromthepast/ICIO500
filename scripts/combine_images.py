import sys
from PIL import Image

def combine_side_by_side(img1_path, img2_path, out_path):
    img1 = Image.open(img1_path).convert('RGBA')
    img2 = Image.open(img2_path).convert('RGBA')
    # Create canvas
    total_width = img1.width + img2.width
    max_height = max(img1.height, img2.height)
    new_img = Image.new('RGBA', (total_width, max_height), (0,0,0,0))
    new_img.paste(img1, (0,0))
    new_img.paste(img2, (img1.width,0))
    new_img.save(out_path)
    print(f"Combined image saved to {out_path}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: combine_images.py <img1> <img2> <out>')
        sys.exit(1)
    combine_side_by_side(sys.argv[1], sys.argv[2], sys.argv[3])

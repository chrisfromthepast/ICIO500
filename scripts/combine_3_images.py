import sys
from PIL import Image

def combine(img1_path, img2_path, img3_path, out_path):
    img1 = Image.open(img1_path).convert('RGBA')
    img2 = Image.open(img2_path).convert('RGBA')
    img3 = Image.open(img3_path).convert('RGBA')
    total_width = img1.width + img2.width + img3.width
    max_height = max(img1.height, img2.height, img3.height)
    new_img = Image.new('RGBA', (total_width, max_height), (0,0,0,0))
    new_img.paste(img1, (0,0))
    new_img.paste(img2, (img1.width, 0))
    new_img.paste(img3, (img1.width + img2.width, 0))
    new_img.save(out_path)
    print(f"Combined image saved to {out_path}")

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage: combine_3_images.py <img1> <img2> <img3> <out>')
        sys.exit(1)
    combine(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

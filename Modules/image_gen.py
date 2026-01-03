import os
import numpy as np
from PIL import Image
from Modules.dds_module import save_image_dds

def generate_alpha_mask(input_path, output_dir=None, target_size=None, texconv_path="texconv.exe"):
    """Generate an alpha mask by converting alpha channel to blue/cyan"""
    img = Image.open(input_path).convert('RGBA')
    alpha = np.array(img, dtype=np.uint8)[:, :, 3]
    
    if target_size:
        alpha = np.array(Image.fromarray(alpha, mode='L').resize(target_size, Image.LANCZOS))
    
    h, w = alpha.shape
    output_data = np.zeros((h, w, 3), dtype=np.uint8)
    output_data[:, :, 0] = 0
    output_data[:, :, 1] = alpha
    output_data[:, :, 2] = 255
    
    result = Image.fromarray(output_data, 'RGB')
    output_dir = output_dir or os.path.dirname(input_path)
    
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    
    if ext.lower() == '.dds':
        output_path = save_image_dds(result, output_dir, name, '_alpha', 'BC1_UNORM', texconv_path)
    else:
        output_path = os.path.join(output_dir, f"{name}_alpha{ext}")
        result.save(output_path)
    
    return output_path, name

def generate_icon(input_path, output_dir=None, texconv_path="texconv.exe"):
    """Generate a 128x128 icon from an image"""
    img = Image.open(input_path)
    icon = img.resize((128, 128), Image.LANCZOS).convert('RGBA')
    
    output_dir = output_dir or os.path.dirname(input_path)
    name, ext = os.path.splitext(os.path.basename(input_path))
    
    if ext.lower() == '.dds':
        output_path = save_image_dds(icon, output_dir, name, '_icon', 'BC3_UNORM', texconv_path)
    else:
        output_path = os.path.join(output_dir, f"{name}_icon{ext}")
        icon.save(output_path)
    
    return output_path, name
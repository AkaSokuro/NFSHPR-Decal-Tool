import os
from PIL import Image
from Modules.dds_module import get_dds_compression_data, get_dds_format_info, run_texconv
from Modules.utils import get_base_name, is_alpha_mask

def convert_image_to_dat(image_path, dat_path, texconv_path):
    """Convert image to DAT by extracting raw texture data"""
    try:
        file_ext = os.path.splitext(image_path)[1].lower()
        
        if file_ext == '.dds':
            texture_data = get_dds_compression_data(image_path)
            
            if not texture_data:
                print(f"Error: Could not extract texture data from {image_path}")
                return False
                
            print(f"       Extracted raw DDS texture data")
        
        # For other formats, convert to DDS first, then extract
        elif file_ext in ['.png', '.jpg', '.jpeg', '.tga']:
            print(f"       Converting {file_ext.upper()} to DDS first...")
            
            img = Image.open(image_path)
            img_width, img_height = img.size
            has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
            
            # Try to match format from existing DDS or metadata DAT
            format_type = None
            base_name = get_base_name(os.path.basename(image_path))
            
            # Check for existing DDS to match format
            possible_dds = os.path.join(os.path.dirname(image_path), f"{base_name}.dds")
            if os.path.exists(possible_dds):
                existing_format, _ = get_dds_format_info(possible_dds)
                if existing_format in ['DXT1', 'DXT3', 'DXT5']:
                    # Map to BC format
                    format_map = {'DXT1': 'BC1_UNORM', 'DXT3': 'BC2_UNORM', 'DXT5': 'BC3_UNORM'}
                    format_type = format_map.get(existing_format)
                    print(f"       Matching existing DDS format: {existing_format} → {format_type}")
            
            # Check metadata DAT file
            if not format_type:
                # Look for the metadata DAT - need to check the actual dat_path location
                metadata_dat_path = dat_path.replace('_texture.dat', '.dat')
                
                if os.path.exists(metadata_dat_path):
                    try:
                        with open(metadata_dat_path, 'rb') as f:
                            # Check if it's remastered or original
                            magic = f.read(13)
                            if magic in (b'\x00' * 12 + b'\x07', b'\x00' * 12 + b'\x09'):
                                # Remastered - format at 0x2C
                                f.seek(0x2C)
                                fmt_byte = f.read(1)
                                if fmt_byte == b'\x47':
                                    format_type = 'BC1_UNORM'  # DXT1
                                    print(f"       From metadata DAT: DXT1 → BC1_UNORM")
                                elif fmt_byte == b'\x4D':
                                    format_type = 'BC3_UNORM'  # DXT5
                                    print(f"       From metadata DAT: DXT5 → BC3_UNORM")
                            elif magic[:9] == b'\x00' * 8 + b'\x01':
                                # Original - format at 0xC
                                f.seek(0xC)
                                fmt_str = f.read(4).decode('ascii', errors='ignore')
                                if fmt_str == 'DXT1':
                                    format_type = 'BC1_UNORM'
                                    print(f"       From metadata DAT: DXT1 → BC1_UNORM")
                                elif fmt_str == 'DXT5':
                                    format_type = 'BC3_UNORM'
                                    print(f"       From metadata DAT: DXT5 → BC3_UNORM")
                    except Exception as e:
                        print(f"       Warning: Could not read metadata DAT: {e}")
                else:
                    print(f"       Warning: Metadata DAT not found at {metadata_dat_path}")
            
            # Fallback to auto-detection
            if not format_type:
                if is_alpha_mask(image_path):
                    format_type = 'BC1_UNORM'  # DXT1 for alpha masks
                    print(f"       Auto-detect: Alpha mask → BC1_UNORM (DXT1)")
                elif has_alpha:
                    format_type = 'BC3_UNORM'  # DXT5 for transparency
                    print(f"       Auto-detect: Has alpha → BC3_UNORM (DXT5)")
                else:
                    format_type = 'BC1_UNORM'  # DXT1 for opaque
                    print(f"       Auto-detect: Opaque → BC1_UNORM (DXT1)")
            
            # Pre-process PNG
            temp_dir = os.path.dirname(image_path)
            base_name_file = os.path.splitext(os.path.basename(image_path))[0]
            
            # Save a clean version of the PNG for conversion
            temp_png = os.path.join(temp_dir, f"{base_name_file}_temp_clean.png")
            if format_type == 'BC1_UNORM':
                # BC1/DXT1 - convert to RGB (no alpha)
                img_clean = img.convert('RGB')
            else:
                # BC3/DXT5 - keep RGBA
                img_clean = img.convert('RGBA')
            img_clean.save(temp_png, 'PNG')
            
            temp_dds = os.path.join(temp_dir, f"{base_name_file}_temp_convert.dds")
            
            # Convert using texconv (uses existing run_texconv function)
            result = run_texconv(temp_png, temp_dir, format_type, f"{base_name_file}_temp_convert.dds", texconv_path)
            
            # Clean up temp PNG
            try:
                os.remove(temp_png)
            except:
                pass
            
            if not result or not os.path.exists(temp_dds):
                print(f"       Error: texconv conversion failed")
                return False
            
            # Extract raw texture data from the temporary DDS
            texture_data = get_dds_compression_data(temp_dds)
            
            # Clean up temporary file
            try:
                os.remove(temp_dds)
            except:
                pass
            
            if not texture_data:
                print(f"       Error: Could not extract texture data from converted DDS")
                return False
        
        else:
            print(f"Error: Unsupported file format {file_ext}")
            print(f"       Supported: .dds, .png, .jpg, .jpeg, .tga")
            return False
        
        # Create DAT directory if needed
        dat_dir = os.path.dirname(dat_path)
        if dat_dir and not os.path.exists(dat_dir):
            os.makedirs(dat_dir)
        
        # Write raw texture data to _texture.dat
        with open(dat_path, 'wb') as f:
            f.write(texture_data)
        
        print(f"       Wrote: {len(texture_data)} bytes → {dat_path}")
        return True
        
    except Exception as e:
        print(f"Error converting {image_path}: {e}")
        return False
import os
from PIL import Image
from Modules.dds_module import get_dds_compression_data, get_dds_format_info, run_texconv
from Modules.utils import get_base_name, is_alpha_mask

def convert_image_to_dat(image_path, dat_path, texconv_path):
    """Convert image to DAT by extracting raw texture data"""
    try:
        file_ext = os.path.splitext(image_path)[1].lower()
        format_type = None
        
        if file_ext == '.dds':
            # Get format info from the DDS file
            dds_format, _ = get_dds_format_info(image_path)
            if dds_format in ['DXT1', 'DXT3', 'DXT5']:
                format_map = {'DXT1': 'BC1_UNORM', 'DXT3': 'BC2_UNORM', 'DXT5': 'BC3_UNORM'}
                format_type = format_map.get(dds_format)
                print(f"       DDS file format: {dds_format} → {format_type}")
            
            texture_data = get_dds_compression_data(image_path)
            
            if not texture_data:
                print(f"Error: Could not extract texture data from {image_path}")
                return False
            
            # Verify DDS data size
            img_w, img_h = Image.open(image_path).size
            expected_size = calculate_dds_size(img_w, img_h, dds_format)
            actual_size = len(texture_data)
            
            print(f"       Extracted raw DDS texture data")
            print(f"       Expected size: {expected_size} bytes")
            print(f"       Actual size: {actual_size} bytes")
            
            if actual_size < expected_size * 0.9:  # Allow 10% tolerance
                print(f"       WARNING: DDS data size mismatch!")
        
        elif file_ext in ['.png', '.jpg', '.jpeg', '.tga']:
            print(f"       Converting {file_ext.upper()} to DDS first...")
            
            img = Image.open(image_path)
            img_width, img_height = img.size
            has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
            
            is_alpha = is_alpha_mask(image_path)
            
            # DXT/BC formats require dimensions that are multiples of 4
            # Calculate padded dimensions
            padded_width = ((img_width + 3) // 4) * 4
            padded_height = ((img_height + 3) // 4) * 4
            
            # Check for power-of-2 requirement
            from Modules.utils import is_power_of_2, next_power_of_2, previous_power_of_2
            
            pow2_warning = False
            if not is_power_of_2(padded_width) or not is_power_of_2(padded_height):
                pow2_warning = True
                print(f"       ")
                print(f"       ⚠️  WARNING: INVALID TEXTURE DIMENSIONS ⚠️")
                print(f"       Current size: {padded_width}x{padded_height}")
                print(f"       ")
                print(f"       NFS:HPR require POWER-OF-2 dimensions:")
                print(f"       Valid sizes: 128, 256, 512, 1024, 2048, 4096")
                print(f"       ")
                print(f"       Suggested sizes:")
                
                if not is_power_of_2(padded_width):
                    prev_w = previous_power_of_2(padded_width)
                    next_w = next_power_of_2(padded_width)
                    print(f"       Width:  {prev_w} (smaller) or {next_w} (larger)")
                
                if not is_power_of_2(padded_height):
                    prev_h = previous_power_of_2(padded_height)
                    next_h = next_power_of_2(padded_height)
                    print(f"       Height: {prev_h} (smaller) or {next_h} (larger)")
                
                print(f"       ")
                print(f"       ⚠️  GAME MAY CRASH OR FAIL TO LOAD THIS DECAL PROPERLY ⚠️")
                print(f"       ")
                
                # Ask user if they want to auto-resize
                user_input = input("       Resize to nearest power-of-2? (y/n): ").strip().lower()
                
                if user_input == 'y':
                    target_width = previous_power_of_2(padded_width)
                    target_height = previous_power_of_2(padded_height)
                    
                    if abs(next_power_of_2(padded_width) - padded_width) < abs(padded_width - previous_power_of_2(padded_width)):
                        target_width = next_power_of_2(padded_width)
                    if abs(next_power_of_2(padded_height) - padded_height) < abs(padded_height - previous_power_of_2(padded_height)):
                        target_height = next_power_of_2(padded_height)
                    
                    print(f"       Resizing to {target_width}x{target_height}...")
                    img = img.resize((target_width, target_height), Image.LANCZOS)
                    padded_width, padded_height = target_width, target_height
                    img_width, img_height = target_width, target_height
                    
                    # Update metadata
                    metadata_dat_path = dat_path.replace('_texture.dat', '.dat')
                    if os.path.exists(metadata_dat_path):
                        try:
                            from Modules.dat_module import write_dat_dimensions
                            write_dat_dimensions(metadata_dat_path, target_width, target_height)
                            print(f"       Updated .DAT dimensions to {target_width}x{target_height}")
                        except Exception as e:
                            print(f"       Warning: Could not update .DAT dimensions: {e}")
                else:
                    print(f"       Continuing with non-power-of-2 dimensions (may crash game)...")
            
            if (img_width, img_height) != (padded_width, padded_height) and not pow2_warning:
                print(f"       Padding image from {img_width}x{img_height} to {padded_width}x{padded_height}")
                print(f"       (DXT/BC formats require dimensions divisible by 4)")
                
                # Create new image with padded size
                if has_alpha or is_alpha:
                    padded_img = Image.new('RGBA', (padded_width, padded_height), (0, 0, 0, 0))
                else:
                    padded_img = Image.new('RGB', (padded_width, padded_height), (0, 0, 0))
                
                # Paste original image at top-left
                if img.mode != padded_img.mode:
                    img = img.convert(padded_img.mode)
                padded_img.paste(img, (0, 0))
                img = padded_img
                img_width, img_height = padded_width, padded_height
                
                # Update .DAT metadata with new dimensions
                metadata_dat_path = dat_path.replace('_texture.dat', '.dat')
                if os.path.exists(metadata_dat_path):
                    try:
                        from Modules.dat_module import write_dat_dimensions
                        write_dat_dimensions(metadata_dat_path, padded_width, padded_height)
                        print(f"       Updated .DAT dimensions to {padded_width}x{padded_height}")
                    except Exception as e:
                        print(f"       Warning: Could not update .DAT dimensions: {e}")
            
            # Try to match format from existing DDS or metadata DAT
            format_type = None
            base_name = get_base_name(os.path.basename(image_path))
            
            possible_dds = os.path.join(os.path.dirname(image_path), f"{base_name}.dds")
            if os.path.exists(possible_dds):
                existing_format, _ = get_dds_format_info(possible_dds)
                if existing_format in ['DXT1', 'DXT3', 'DXT5']:
                    format_map = {'DXT1': 'BC1_UNORM', 'DXT3': 'BC2_UNORM', 'DXT5': 'BC3_UNORM'}
                    format_type = format_map.get(existing_format)
                    print(f"       Matching existing DDS format: {existing_format} → {format_type}")
            
            # Check metadata DAT file
            if not format_type and not is_alpha:
                metadata_dat_path = dat_path.replace('_texture.dat', '.dat')
                
                if os.path.exists(metadata_dat_path):
                    try:
                        with open(metadata_dat_path, 'rb') as f:
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
                                elif fmt_byte == b'\x62':
                                    format_type = 'BC7_UNORM'  # BC7
                                    print(f"       From metadata DAT: BC7 → BC7_UNORM")
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
            
            # Fallback to auto-detection
            if not format_type:
                if is_alpha:
                    format_type = 'BC3_UNORM'
                    print(f"       Auto-detect: Alpha mask detected → BC3_UNORM (DXT5)")
                elif has_alpha:
                    format_type = 'BC3_UNORM'
                    print(f"       Auto-detect: Has alpha channel → BC3_UNORM (DXT5)")
                else:
                    format_type = 'BC1_UNORM'
                    print(f"       Auto-detect: Opaque image → BC1_UNORM (DXT1)")
            
            # Pre-process PNG
            temp_dir = os.path.dirname(image_path)
            base_name_file = os.path.splitext(os.path.basename(image_path))[0]
            
            # Save a clean version of the PNG for conversion
            temp_png = os.path.join(temp_dir, f"{base_name_file}_temp_clean.png")
            
            if format_type == 'BC1_UNORM':
                img_clean = img.convert('RGB')
            elif is_alpha:
                img_clean = img.convert('RGB')
            else:
                img_clean = img.convert('RGBA')
            
            img_clean.save(temp_png, 'PNG')
            
            temp_dds = os.path.join(temp_dir, f"{base_name_file}_temp_convert.dds")
            
            # Run texconv
            result = run_texconv(temp_png, temp_dir, format_type, f"{base_name_file}_temp_convert.dds", texconv_path)
            
            # Clean up temp PNG
            try:
                os.remove(temp_png)
            except:
                pass
            
            if not result or not os.path.exists(temp_dds):
                print(f"       Error: texconv conversion failed")
                return False
            
            # Verify the DDS file before extracting
            dds_format, _ = get_dds_format_info(temp_dds)
            dds_size = os.path.getsize(temp_dds)
            expected_data_size = calculate_dds_size(img_width, img_height, dds_format)
            
            print(f"       Generated DDS: {dds_size} bytes total")
            print(f"       Expected texture data: {expected_data_size} bytes")
            
            # Verify DDS has correct size
            if dds_size < (128 + expected_data_size * 0.9):  # Header + 90% of expected data
                print(f"       ERROR: DDS file is too small!")
                print(f"       This usually means texconv failed silently.")
                try:
                    os.remove(temp_dds)
                except:
                    pass
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
            
            # Verify extracted data size
            if len(texture_data) < expected_data_size * 0.9:
                print(f"       ERROR: Extracted data is too small!")
                print(f"       Expected: {expected_data_size} bytes")
                print(f"       Got: {len(texture_data)} bytes")
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
        
        # Update metadata DAT format if needed and possible
        metadata_dat_path = dat_path.replace('_texture.dat', '.dat')
        if os.path.exists(metadata_dat_path):
            if format_type:
                try:
                    with open(metadata_dat_path, 'r+b') as f:
                        magic = f.read(13)
                        if magic in (b'\x00' * 12 + b'\x07', b'\x00' * 12 + b'\x09'):
                            # Remastered - format at 0x2C
                            f.seek(0x2C)
                            if format_type == 'BC1_UNORM':
                                f.write(b'\x47')  # DXT1
                                print(f"       Updated metadata DAT format to DXT1")
                            elif format_type == 'BC3_UNORM':
                                f.write(b'\x4D')  # DXT5
                                print(f"       Updated metadata DAT format to DXT5")
                            elif format_type == 'BC7_UNORM':
                                f.write(b'\x62')  # BC7
                                print(f"       Updated metadata DAT format to BC7")
                        elif magic[:9] == b'\x00' * 8 + b'\x01':
                            # Original - format at 0xC
                            f.seek(0xC)
                            if format_type == 'BC1_UNORM':
                                f.write(b'DXT1')
                                print(f"       Updated metadata DAT format to DXT1")
                            elif format_type == 'BC3_UNORM':
                                f.write(b'DXT5')
                                print(f"       Updated metadata DAT format to DXT5")
                except Exception as e:
                    print(f"       Warning: Could not update metadata DAT format: {e}")
            else:
                print(f"       Note: Format type unknown, metadata DAT not updated")
        else:
            print(f"       Note: Metadata DAT not found, texture data only")
        
        return True
        
    except Exception as e:
        print(f"Error converting {image_path}: {e}")
        import traceback
        traceback.print_exc()
        return False


def calculate_dds_size(width, height, format_name):
    """Calculate expected DDS texture data size using pure integer math"""
    # DXT/BC formats work on 4x4 blocks, dimensions must round up to multiples of 4
    block_width = (width + 3) // 4
    block_height = (height + 3) // 4
    
    if format_name in ['DXT1', 'BC1', 'BC1_UNORM']:
        # DXT1/BC1: 4x4 blocks, 8 bytes per block
        return block_width * block_height * 8
    elif format_name in ['DXT5', 'BC3', 'BC3_UNORM']:
        # DXT5/BC3: 4x4 blocks, 16 bytes per block
        return block_width * block_height * 16
    elif format_name in ['BC7', 'BC7_UNORM']:
        # BC7: 4x4 blocks, 16 bytes per block (Remastered)
        return block_width * block_height * 16
    elif format_name in ['RGBA', 'BGRA']:
        # Uncompressed RGBA
        return width * height * 4
    else:
        # Unknown format
        return width * height * 4

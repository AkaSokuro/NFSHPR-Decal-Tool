import os
from PIL import Image
from Modules.config import save_config, DEFAULT_CONFIG
from Modules.utils import strip_quotes, print_section, print_menu_options, confirm_action, parse_dimensions, is_alpha_mask, get_base_name
from Modules.image_gen import generate_alpha_mask, generate_icon
from Modules.dat_module import read_dat_dimensions, write_dat_dimensions, warn_if_dimension_mismatch
from Modules.image_conv import convert_image_to_dat

def setup_directories_menu(config):
    """Menu for configuring directory paths"""
    print_section("DIRECTORY SETUP")
    
    print("Current configuration:")
    print(f"  Images Directory: {config['images_dir']}")
    print(f"  Raw Directory:    {config['raw_dir']}")
    print(f"  Texconv Path:     {config['texconv_path']}")
    
    print("\nWhat would you like to configure?")
    print_menu_options([
        "[1] Images Directory (where exported textures are stored)",
        "[2] Raw Directory (where .DAT files are located)",
        "[3] Texconv Path (path to texconv.exe)",
        "[4] Reset to defaults",
        "[5] Back to main menu"
    ])
    
    choice = input("\nChoice: ").strip()
    
    if choice == '1':
        new_path = strip_quotes(input("\nEnter Images Directory path: "))
        if new_path:
            config['images_dir'] = new_path
            print(f"\nImages Directory set to: {new_path}")
            save_config(config)
    
    elif choice == '2':
        new_path = strip_quotes(input("\nEnter Raw Directory path: "))
        if new_path:
            config['raw_dir'] = new_path
            print(f"\nRaw Directory set to: {new_path}")
            save_config(config)
    
    elif choice == '3':
        new_path = strip_quotes(input("\nEnter Texconv path (e.g., C:/Tools/texconv.exe): "))
        if new_path:
            config['texconv_path'] = new_path
            print(f"\nTexconv path set to: {new_path}")
            save_config(config)
    
    elif choice == '4':
        if confirm_action("Reset all settings to defaults? (y/n): "):
            config.update(DEFAULT_CONFIG)
            save_config(config)
            print("\nConfiguration reset to defaults!")
    
    elif choice == '5':
        return
    
    else:
        print("\nInvalid choice.\n")

def icon_generator_menu(config):
    print_section("ICON GENERATOR (128x128)")
    
    input_file = strip_quotes(input("Enter File: "))
    if not os.path.exists(input_file):
        print(f"\nError: File '{input_file}' not found!\n")
        return
    
    try:
        img = Image.open(input_file)
        w, h = img.size
        img.close()
        print(f"\nOriginal size: {w}x{h}\nIcon will be resized to: 128x128")
    except Exception as e:
        print(f"\nError reading image: {e}\n")
        return
    
    output_dir = strip_quotes(input("\nEnter Output Directory (Leave empty for same directory): "))
    if output_dir and not os.path.exists(output_dir):
        print(f"\nError: Directory '{output_dir}' not found!\n")
        return
    
    try:
        output_path, filename = generate_icon(input_file, output_dir, config['texconv_path'])
        print(f"\nGenerated Icon for {filename}.\nSaved to: {output_path}\n")
    except Exception as e:
        print(f"\nError generating icon: {e}\n")

def alpha_mask_menu(config):
    print_section("ALPHA MASK GENERATOR")
    
    input_file = strip_quotes(input("Enter File: "))
    if not os.path.exists(input_file):
        print(f"\nError: File '{input_file}' not found!\n")
        return
    
    try:
        w, h = Image.open(input_file).size
        print(f"\nOriginal size: {w}x{h}")
    except:
        pass
    
    custom_size = input("\nEnter custom size (WIDTHxHEIGHT | e.g., 1024x1024) or leave empty to keep original: ").strip()
    target_size = parse_dimensions(custom_size)
    
    if target_size:
        print(f"Target size set to: {target_size[0]}x{target_size[1]}")
    
    output_dir = strip_quotes(input("\nEnter Output Directory (Leave empty for same directory): "))
    if output_dir and not os.path.exists(output_dir):
        print(f"\nError: Directory '{output_dir}' not found!\n")
        return
    
    try:
        output_path, filename = generate_alpha_mask(input_file, output_dir, target_size, config['texconv_path'])
        print(f"\nGenerated Alpha Mask for {filename}.")
        if target_size:
            print(f"Resized to: {target_size[0]}x{target_size[1]}")
        print(f"Saved to: {output_path}\n")
    except Exception as e:
        print(f"\nError generating alpha mask: {e}\n")

def regenerate_alpha_mask_menu(config):
    """Menu for regenerating a specific alpha mask"""
    print_section("REGENERATE ALPHA MASK")
    
    input_file = strip_quotes(input("Enter Source Image File: "))
    if not os.path.exists(input_file):
        print(f"\nError: File '{input_file}' not found!\n")
        return
    
    if is_alpha_mask(input_file):
        print(f"\nError: This file is already an alpha mask!\n")
        return
    
    try:
        w, h = Image.open(input_file).size
        print(f"\nSource image size: {w}x{h}")
    except:
        pass
    
    alpha_mask_file = strip_quotes(input("\nEnter Alpha Mask File to Replace: "))
    if not os.path.exists(alpha_mask_file):
        print(f"\nError: Alpha mask file '{alpha_mask_file}' not found!\n")
        return
    
    try:
        alpha_w, alpha_h = Image.open(alpha_mask_file).size
        print(f"Alpha mask size: {alpha_w}x{alpha_h}")
    except:
        pass
    
    if not is_alpha_mask(alpha_mask_file):
        print(f"\nWarning: The specified file doesn't appear to be an alpha mask.")
        if not confirm_action("Continue anyway? (y/n): "):
            print("\nCancelled.\n")
            return
    
    custom_size = input("\nEnter custom size (WIDTHxHEIGHT | eg. 1024x1024) or leave empty to keep original: ").strip()
    target_size = parse_dimensions(custom_size)
    
    if target_size:
        print(f"Target size set to: {target_size[0]}x{target_size[1]}")
    
    try:
        output_path, filename = generate_alpha_mask(input_file, os.path.dirname(input_file), target_size, config['texconv_path'])
        os.replace(output_path, alpha_mask_file)
        
        print(f"\nRegenerated Alpha Mask for {filename}.")
        if target_size:
            print(f"Resized to: {target_size[0]}x{target_size[1]}")
        print(f"Replaced: {alpha_mask_file}\n")
    except Exception as e:
        print(f"\nError regenerating alpha mask: {e}\n")

def decal_locator_menu(locator):
    while True:
        print_section("DECAL LOCATOR")
        print_menu_options([
            "[1] Find .DAT file for an image",
            "[2] Search decals",
            "[3] Rebuild index",
            "[4] Back to main menu"
        ])
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            image_name = input("\nEnter image filename: ").strip()
            result = locator.find_dat(image_name)
            
            if result:
                print(f"\n{'=' * 60}\n  DECAL FOUND\n{'=' * 60}")
                print(f"\n  Image:  {result['image_path']}")
                print(f"  DAT:    {result['dat_path']}")
                print(f"  Bundle: {result['bundle']}\n")
            else:
                print(f"\nCould not find .DAT file for '{image_name}'\n")
        
        elif choice == '2':
            query = input("\nEnter search query: ").strip()
            results = locator.search(query)
            
            if results:
                print(f"\n{'=' * 60}\n  {len(results)} RESULT(S) FOUND\n{'=' * 60}\n")
                for i, (img, info) in enumerate(results, 1):
                    print(f"  [{i}] {img}")
                    print(f"      DAT: {info['dat_path']}")
                    print(f"      Bundle: {info['bundle']}\n")
            else:
                print(f"\nNo results found for '{query}'\n")
        
        elif choice == '3':
            locator.build_index()
        
        elif choice == '4':
            break
        
        else:
            print("\nInvalid choice. Please enter 1-4.\n")

def change_decal_dimensions_menu(locator):
    """Menu for changing decal dimensions in metadata files"""
    print_section("CHANGE DECAL DIMENSIONS")
    
    if not locator.texture_map:
        print("Error: No texture mappings found. Please rebuild index first.\n")
        return
    
    print_menu_options([
        "[1] Single File - Change dimensions for a specific file",
        "[2] Bundle - Change dimensions for all files in a bundle",
        "[3] Cancel"
    ])
    
    choice = input("\nChoice: ").strip()
    
    if choice == '3':
        print("\nCancelled.\n")
        return
    
    if choice == '1':
        print(f"\n{'-' * 60}\nEnter image filename OR bundle name + filename\n"
              f"Examples:\n  - 8A_EA_7D_70out.dds\n  - TEX_1273701_1273702_DL/8A_EA_7D_70out.dds\n{'-' * 60}")
        
        file_input = input("\nFile: ").strip()
        info = locator.find_dat(file_input)
        
        if not info and ('/' in file_input or '\\' in file_input):
            parts = file_input.replace('\\', '/').split('/')
            bundle_name = parts[0] if len(parts) > 1 else None
            filename = parts[-1]
            
            for img, img_info in locator.texture_map.items():
                if bundle_name and img_info['bundle'] != bundle_name:
                    continue
                if img.lower() == filename.lower() or img_info['base_name'].lower() == get_base_name(filename).lower():
                    info = img_info
                    break
        
        if not info or not os.path.exists(info['dat_path']):
            print(f"\nError: Could not find mapping for '{file_input}'\n")
            return
        
        try:
            curr_w, curr_h = read_dat_dimensions(info['dat_path'])
            
            if curr_w == 128 and curr_h == 128:
                print(f"\nError: Cannot change dimensions for icon files (128x128).\n")
                return
            
            print(f"\nCurrent dimensions: {curr_w}x{curr_h}")
        except Exception as e:
            print(f"\nError reading current dimensions: {e}\n")
            return
        
        new_size = input("\nEnter new dimensions (WIDTHxHEIGHT | eg. 2048x2048): ").strip()
        dims = parse_dimensions(new_size)
        
        if not dims:
            print("\nInvalid format. Use WIDTHxHEIGHT (eg. 2048x2048)\n")
            return
        
        new_w, new_h = dims
        print(f"\nChanging dimensions from {curr_w}x{curr_h} to {new_w}x{new_h}")
        print(f"File: {info['dat_path']}")
        
        if confirm_action():
            if write_dat_dimensions(info['dat_path'], new_w, new_h):
                print("\nDimensions changed successfully!\n")
            else:
                print("\nFailed to change dimensions.\n")
        else:
            print("\nCancelled.\n")
    
    elif choice == '2':
        print(f"\n{'-' * 60}\nEnter bundle name OR select from list\n{'-' * 60}")
        
        bundles = locator.get_bundles()
        if not bundles:
            print("\nNo bundles found.\n")
            return
        
        print(f"\nAvailable bundles ({len(bundles)}):\n")
        for i, bundle in enumerate(bundles, 1):
            count = sum(1 for info in locator.texture_map.values() if info['bundle'] == bundle)
            print(f"  [{i}] {bundle} ({count} files)")
        
        bundle_input = input("\nEnter bundle name or number: ").strip()
        selected = locator.select_bundle(bundle_input, bundles)
        
        if not selected:
            print(f"\nError: Bundle '{bundle_input}' not found.\n")
            return
        
        files = [(img, info) for img, info in locator.texture_map.items() if info['bundle'] == selected]
        
        valid_count = sum(1 for _, info in files if os.path.exists(info['dat_path'])
                         and read_dat_dimensions(info['dat_path']) != (128, 128))
        
        print(f"\nBundle: {selected}")
        print(f"Files to modify: {valid_count} (excluding icon files)\n")
        
        new_size = input("Enter new dimensions (WIDTHxHEIGHT | eg. 2048x2048): ").strip()
        dims = parse_dimensions(new_size)
        
        if not dims:
            print("\nInvalid format. Use WIDTHxHEIGHT (e.g., 2048x2048)\n")
            return
        
        new_w, new_h = dims
        print(f"\nThis will change dimensions to {new_w}x{new_h} for all files in the bundle.")
        
        if not confirm_action():
            print("\nCancelled.\n")
            return
        
        changed, skipped, errors = 0, 0, 0
        
        for image_name, info in files:
            if not os.path.exists(info['dat_path']):
                skipped += 1
                continue
            
            try:
                curr_w, curr_h = read_dat_dimensions(info['dat_path'])
                
                if curr_w == 128 and curr_h == 128:
                    print(f"Skipping icon file (128x128): {image_name}")
                    skipped += 1
                    continue
                
                print(f"Changing {image_name}: {curr_w}x{curr_h} -> {new_w}x{new_h}")
                
                if write_dat_dimensions(info['dat_path'], new_w, new_h):
                    changed += 1
                else:
                    errors += 1
            except Exception as e:
                print(f"  Error: {e}")
                errors += 1
        
        print(f"\n{'=' * 60}\nSUMMARY\n{'=' * 60}")
        print(f"Files changed: {changed}\nFiles skipped: {skipped}\nErrors: {errors}\n{'=' * 60}\n")
    
    else:
        print("\nInvalid choice.\n")

def convert_images_to_dat_menu(locator, config):
    """Menu for converting images to DAT files"""
    print_section("CONVERT IMAGES TO DAT")

    if not locator.texture_map:
        print("Error: No texture mappings found. Please rebuild index first.\n")
        return

    print_menu_options([
        "[1] File - Convert a specific file",
        "[2] Bundle - Convert all files in a bundle",
        "[3] All Bundles - Convert every bundle",
        "[4] Cancel"
    ])

    choice = input("\nChoice: ").strip()

    if choice == '4':
        print("\nCancelled.\n")
        return

    if choice == '1':
        print(f"\n{'-' * 60}\nEnter image filename OR bundle name + filename\n"
              f"Examples:\n  - 8A_EA_7D_70out.dds\n"
              f"  - TEX_1273701_1273702_DL/8A_EA_7D_70out.dds\n{'-' * 60}")

        file_input = input("\nFile: ").strip()
        info = locator.find_dat(file_input)

        if not info and ('/' in file_input or '\\' in file_input):
            parts = file_input.replace('\\', '/').split('/')
            bundle_name = parts[0] if len(parts) > 1 else None
            filename = parts[-1]

            for img, img_info in locator.texture_map.items():
                if bundle_name and img_info['bundle'] != bundle_name:
                    continue
                if img.lower() == filename.lower() or \
                   img_info['base_name'].lower() == get_base_name(filename).lower():
                    info = img_info
                    break

        if not info or not os.path.exists(info['image_path']):
            print(f"\nError: Could not find mapping for '{file_input}'\n")
            return

        dat_dir = os.path.dirname(info['dat_path'])
        texture_dat = os.path.join(dat_dir, f"{info['base_name']}_texture.dat")

        file_type = "Alpha Mask" if is_alpha_mask(info['image_path']) else "Texture"

        print(f"\nFound: {os.path.basename(info['image_path'])} ({file_type})")
        print(f"Bundle: {info['bundle']}")
        print(f"\nConverting: {info['image_path']}")

        warnings = warn_if_dimension_mismatch(
            info['image_path'],
            info['dat_path']
        )

        if warnings:
            print("\nWARNINGS:")
            for w in warnings:
                print(f"  - {w}")

            if not confirm_action("Continue conversion anyway? (y/n): "):
                print("\nSkipped.\n")
                return

        if convert_image_to_dat(info['image_path'], texture_dat, config['texconv_path']):
            print("\nConversion successful!\n")
        else:
            print("\nConversion failed!\n")

    elif choice in ('2', '3'):
        if choice == '2':
            print(f"\n{'-' * 60}\nEnter bundle name OR select from list\n{'-' * 60}")

            bundles = locator.get_bundles()
            if not bundles:
                print("\nNo bundles found.\n")
                return

            print(f"\nAvailable bundles ({len(bundles)}):\n")
            for i, bundle in enumerate(bundles, 1):
                count = sum(1 for info in locator.texture_map.values()
                            if info['bundle'] == bundle)
                print(f"  [{i}] {bundle} ({count} images)")

            bundle_input = input("\nEnter bundle name or number: ").strip()
            selected = locator.select_bundle(bundle_input, bundles)

            if not selected:
                print(f"\nError: Bundle '{bundle_input}' not found.\n")
                return

            images_to_convert = [
                (img, info) for img, info in locator.texture_map.items()
                if info['bundle'] == selected
            ]
        else:
            print("\nThis will convert ALL images in EVERY bundle to their")
            print("corresponding _texture.dat files.")

            images_to_convert = list(locator.texture_map.items())

        if not confirm_action():
            print("\nCancelled.\n")
            return

        converted, skipped, errors = 0, 0, 0

        for image_name, info in images_to_convert:
            if not os.path.exists(info['image_path']):
                skipped += 1
                continue

            dat_dir = os.path.dirname(info['dat_path'])
            texture_dat = os.path.join(dat_dir, f"{info['base_name']}_texture.dat")

            file_type = "Alpha" if is_alpha_mask(info['image_path']) else "Texture"
            print(f"\nConverting [{file_type}]: {image_name}")

            # Dimension Warning
            warnings = warn_if_dimension_mismatch(
                info['image_path'],
                info['dat_path']
            )

            if warnings:
                print("  WARNINGS:")
                for w in warnings:
                    print(f"    - {w}")

            if convert_image_to_dat(info['image_path'], texture_dat, config['texconv_path']):
                converted += 1
            else:
                errors += 1

        print(f"\n{'=' * 60}\nSUMMARY\n{'=' * 60}")
        print(f"Images converted: {converted}")
        print(f"Images skipped:   {skipped}")
        print(f"Errors:           {errors}")
        print(f"{'=' * 60}\n")

    else:
        print("\nInvalid choice.\n")
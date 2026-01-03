from Modules.config import load_config, VERSION
from Modules.utils import print_menu_options
from Modules.decal_locator import DecalLocator
from Modules.menu import (
    alpha_mask_menu,
    regenerate_alpha_mask_menu,
    icon_generator_menu,
    change_decal_dimensions_menu,
    convert_images_to_dat_menu,
    decal_locator_menu,
    setup_directories_menu
)

def main():
    config = load_config()
    locator = DecalLocator(config['images_dir'], config['raw_dir'])
    
    print(f"\n{'=' * 60}\n{'NFS:HPR DECAL MODDING TOOL':^60}\n{'@AkaSokuro':^60}\n{'=' * 60}")
    print(f"\nVersion: {VERSION}")
    
    if not locator.load_index():
        print("\nNo index found. Building decal index...\n")
        locator.build_index()
    else:
        print(f"\nDecal index loaded! {len(locator.texture_map)} decals indexed.\n")
        
    if len(locator.texture_map) <= 0:
        print("\nNOTICE:")
        print("No index is founded, make sure you have both textures and scripts in the same folder.")
        print("You can also configure custom directories in the setup menu.")
        print("Try rebuild decal index once you set it up.")
    
    menu_options = [
        "",
        "[ IMAGE GENERATION ]",
        "[1] Generate Alpha Mask",
        "[2] Regenerate Alpha Mask (Replace Existing)",
        "[3] Generate Icon (128x128)",
        "",
        "[ METADATA & CONVERSION ]",
        "[4] Change Decal Dimensions (Metadata)",
        "[5] Convert Images to DAT Files",
        "",
        "[ TOOLS & UTILITIES ]",
        "[6] Decal Locator (Search & Find)",
        "[7] Rebuild Decal Index",
        "[8] Directory Setup",
        "",
        "[0] Exit",
        ""
    ]
    
    while True:
        print_menu_options(menu_options)
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            alpha_mask_menu(config)
        elif choice == '2':
            regenerate_alpha_mask_menu(config)
        elif choice == '3':
            icon_generator_menu(config)
        elif choice == '4':
            change_decal_dimensions_menu(locator)
        elif choice == '5':
            convert_images_to_dat_menu(locator, config)
        elif choice == '6':
            decal_locator_menu(locator)
        elif choice == '7':
            locator.build_index()
        elif choice == '8':
            setup_directories_menu(config)
            # Reload locator with new paths
            locator = DecalLocator(config['images_dir'], config['raw_dir'])
        elif choice == '0':
            break
        else:
            print("\nInvalid choice. Please enter 0-8.\n")

if __name__ == "__main__":
    main()
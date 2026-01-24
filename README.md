# NFSHPR Decal Tool
[![GitHub release](https://img.shields.io/github/v/release/AkaSokuro/NFSHPR-Decal-Tool)](https://github.com/AkaSokuro/NFSHPR-Decal-Tool/releases)

[![GitHub download](https://img.shields.io/github/downloads/AkaSokuro/NFSHPR-Decal-Tool/latest/nfshpr-decal-tool-scripts.zip?color=green)](https://github.com/AkaSokuro/NFSHPR-Decal-Tool/releases/latest/download/nfshpr-decal-tool-scripts.zip)
[![Texturepack download](https://img.shields.io/github/downloads/AkaSokuro/NFSHPR-Decal-Tool/v5.0/nfshpr-decal-textures.zip?color=green)](https://github.com/AkaSokuro/NFSHPR-Decal-Tool/releases/download/v5.0/nfshpr-decal-textures.zip)

This script is for easing the process of modifying Need For Speed: Hot Pursuit Remastered's decals so custom wraps can be made faster.

## Disclaimer
The custom decals can be seen by other players so abide to the game's TOS.

**Do not use any inappropriate wrap/decal in Online lobby or else you might get banned.**</br>

## Requirements
- [Python (>v3.6)](https://www.python.org/downloads/)
- [Decal Texture/Data Pack](https://github.com/AkaSokuro/NFSHPR-Decal-Tool/releases/download/v5.0/nfshpr-decal-textures.zip)

### Recommended Image Editor
- [Paint.NET](https://www.getpaint.net/download.html) - Fast and easy lightweight image editor.

## Installation
- Download packages from **releases**.
- Unzip the `nfshpr-decal-tool-scripts.zip` and `nfshpr-decal-textures.zip` anywhere in the same folder.
- Run `run_tool.bat`, the batch will ask you to install any necessary packages.

## Updating
- Download only `nfshpr-decal-tool-scripts.zip` from **releases**.
- Unzip the `nfshpr-decal-tool-scripts.zip` into the installed folder and replace existing files.

## Features
### Automation
- `Auto Convert Decal` - Automatically convert an image into a decal without having to do it manually step by step
### Image Generation
- `Generate Alpha Mask` - Automatically generate an alpha mask from the image (Determine what to render on the decal)
- `Regenerate Alpha Mask` - Automatically generate an alpha mask from the image replacing the existing alpha mask
- `Generate Icon` - Automatically generate a small icon (*Currently doesn't work in game*)
### Metadata / Conversion
- `Change Decal Dimensions` - Change the dimension/size of the decal metadata to appears as that size ingame
- `Convert Images to DAT` - Convert the decal image file into raw data file
### Tools / Utilities
- `Decal Locator` - Get linked raw data file for specify decal image
- `Packer` - Pack the decal bundles into **BIN** file

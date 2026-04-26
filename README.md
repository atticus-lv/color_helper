## Color Helper (Blender Extension)
> Palette workflow tools for Blender

![animation](docs/animation.gif)

### Overview
Color Helper streamlines palette creation, color extraction, palette editing, shader node generation, Pantone matching, and PNG palette export directly inside Blender.

It works from the 3D View and Shader Node Editor side panel, making color palettes available where materials and look development happen.

### Features
+ **Palette management**
  + Create, copy, remove, reorder, and move palettes between collections.
  + Organize multiple palettes with collection-based management.
+ **Color extraction**
  + Generate palettes from clipboard images.
  + Import colors from palette PNG files.
  + Paste Hex or RGB text values as Blender colors with gamma correction.
+ **Color generation and editing**
  + Batch-generate random palettes.
  + Generate color schemes using common color harmony rules such as analogous, complementary, split complementary, monochromatic, and triadic palettes.
  + Adjust Hue, Saturation, and Value offsets.
  + Sort colors by Hue, Saturation, or Value.
  + Shuffle palette colors.
+ **Shader node workflow**
  + Create or update Shader Node Groups from palettes.
  + Output individual color sockets and a generated ColorRamp from each palette.
  + Insert palette node groups directly in the Shader Node Editor.
  + Optionally auto-update linked node groups when palette colors change.
+ **Blender paint palette support**
  + Convert Color Helper palettes into Blender paint palettes.
+ **Pantone matching**
  + Convert palette colors to the nearest Pantone colors.
  + Copy Pantone color names to the clipboard.
+ **Export**
  + Create PNG preview images from palettes.
  + Batch-export all palettes in a collection.


### Log
### v0.71
+ adapt to Blender Extension
+ add GPL license file


### v0.6
+ fix non-english locale issue in collection name 

### v0.52
+ support blender 4.0
+ remove support of lower version
+ auto convert old palette node group to new version with index

#### v0.4.2
+ add support for blender 3.5/3.6

#### v0.4.1
+ fix uncorrectable name when create palette node group
+ add max return color preference

#### v0.4
+ Add nearest Pantone color converter
  + library base on http://www.excaliburcreations.com/pantone.html
+ Generate ramp node in the linked node group

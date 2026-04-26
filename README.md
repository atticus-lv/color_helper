## Color Helper(Blender addon)
> Palette addon for blender

![animation](res/animation.gif)
### Feature
+ Clipboard (pixel/hex or rgb value string) image generation palette
+ Palette Dynamic Link Materials (node group)
+ Batch random palette generation (based on adobe color website)
+ Palette adjustment (hsv, finishing), asset loading and exporting
+ Nearest Pantone color converter


### Log

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

# SPDX-FileCopyrightText: 2026 Atticus
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy


class ClipboardImageError(Exception):
    """Raised when Blender cannot read a compatible image from the clipboard."""


class Clipboard:
    """Read image data from Blender's native image clipboard."""

    def pull_image_from_clipboard(self, context=None):
        context = context or bpy.context
        area = context.area
        window = context.window
        screen = context.screen

        if area is None or window is None or screen is None:
            return None

        old_area_type = area.type
        old_ui_type = getattr(area, "ui_type", None)
        images_before = set(bpy.data.images)

        try:
            area.type = "IMAGE_EDITOR"
            region = next((r for r in area.regions if r.type == "WINDOW"), None)
            if region is None:
                return None

            with context.temp_override(window=window, screen=screen, area=area, region=region):
                try:
                    result = bpy.ops.image.clipboard_paste()
                except RuntimeError as exc:
                    message = str(exc)
                    if "No compatible images are on the clipboard" in message:
                        raise ClipboardImageError(
                            "No compatible image found on the clipboard. Copy an image first, then try Paste."
                        ) from None

                    raise ClipboardImageError(
                        "Blender could not paste an image from the clipboard."
                    ) from None

            if "FINISHED" not in result:
                return None

            pasted_images = [image for image in bpy.data.images if image not in images_before]
            if pasted_images:
                return pasted_images[-1]

            return None
        finally:
            area.type = old_area_type
            if old_ui_type is not None and hasattr(area, "ui_type"):
                try:
                    area.ui_type = old_ui_type
                except TypeError:
                    pass

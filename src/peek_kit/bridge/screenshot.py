import Quartz
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Tuple, Optional
import time
import base64

from peek_kit.models.elements import AccessibilityTree, Screenshot
from peek_kit.utils.encoding import encode_image_base64
from peek_kit.bridge.apps import get_bundle_id

def capture_cg_window(app_name: str) -> Optional[Image.Image]:
    from peek_kit.bridge.apps import list_running_apps
    apps = list_running_apps()
    target_pid = None
    for a in apps:
        if a.display_name == app_name or a.bundle_id == app_name:
            target_pid = a.pid
            break
            
    if not target_pid:
        return None
        
    # We use CGWindowListCreateImage
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
    
    target_window = None
    for window in window_list:
        if window.get('kCGWindowOwnerPID') == target_pid and window.get('kCGWindowLayer', -1) == 0:
            target_window = window
            break
            
    # Fallback if no layer 0 window found
    if not target_window:
        for window in window_list:
            if window.get('kCGWindowOwnerPID') == target_pid:
                target_window = window
                break

    if not target_window:
        return None
        
    window_id = target_window['kCGWindowNumber']
    cg_image = Quartz.CGWindowListCreateImage(
        Quartz.CGRectNull,
        Quartz.kCGWindowListOptionIncludingWindow,
        window_id,
        Quartz.kCGWindowImageBoundsIgnoreFraming | Quartz.kCGWindowImageBestResolution
    )
    
    if not cg_image:
        return None
        
    width = Quartz.CGImageGetWidth(cg_image)
    height = Quartz.CGImageGetHeight(cg_image)
    color_space = Quartz.CGColorSpaceCreateDeviceRGB()
    bytes_per_row = Quartz.CGImageGetBytesPerRow(cg_image)
    
    data_provider = Quartz.CGImageGetDataProvider(cg_image)
    raw_data = Quartz.CGDataProviderCopyData(data_provider)
    
    img = Image.frombuffer("RGBA", (width, height), raw_data, "raw", "BGRA", bytes_per_row, 1)
    
    # BGRA to RGBA
    b, g, r, a = img.split()
    img = Image.merge("RGBA", (r, g, b, a))
    
    return img

def take_screenshot(app_name: str, annotated: bool = True, tree: Optional[AccessibilityTree] = None) -> Optional[Screenshot]:
    img = capture_cg_window(app_name)
    if not img:
        return None
        
    width, height = img.size
    
    # If annotated and we have a tree, overlay boxes
    if annotated and tree:
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # We need a font, defaulting to built-in if no true type available
        font = ImageFont.load_default()
        
        def draw_element(el):
            if el.position and el.size:
                x, y = el.position
                w, h = el.size
                
                color = (136, 135, 128, 102) # #888780 Gray with 0.4 alpha (102/255)
                outline_color = (136, 135, 128, 255)
                if 'Button' in el.role:
                    color = (29, 158, 117, 102) # #1D9E75 Green
                    outline_color = (29, 158, 117, 255)
                elif 'Text' in el.role:
                    color = (239, 159, 39, 102) # #EF9F27 Amber
                    outline_color = (239, 159, 39, 255)
                elif 'Menu' in el.role:
                    color = (55, 138, 221, 102) # #378ADD Blue
                    outline_color = (55, 138, 221, 255)
                    
                draw.rectangle([x, y, x + w, y + h], fill=color, outline=outline_color, width=2)
                
                # Draw ID label above
                label = f"{el.role} {el.element_id}"
                # Get font size
                bbox = font.getbbox(label)
                if bbox:
                    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    draw.rectangle([x, y - text_h - 2, x + text_w, y], fill=(0,0,0,180))
                    draw.text((x, y - text_h - 2), label, fill=(255,255,255,255), font=font)
                
            for child in el.children:
                draw_element(child)
                
        draw_element(tree.root_element)
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
    fp = BytesIO()
    img.save(fp, format="PNG")
    b64 = encode_image_base64(fp)
    
    return Screenshot(
        base64_png=b64,
        width=width,
        height=height,
        element_count=tree.element_count if tree else 0,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

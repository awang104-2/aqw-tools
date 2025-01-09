from PIL import Image
from src.handlers import get_client_hwnd
import win32con
import win32gui
import win32ui


def capture_window_with_offset(hwnd, save_path=None, save=False, offset_x=0, offset_y=0, capture_width=None, capture_height=None):
    # Get the full window size
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    window_width = right - left
    window_height = bot - top

    # Default to the remaining area if width/height not specified
    if capture_width is None:
        capture_width = window_width - offset_x
    if capture_height is None:
        capture_height = window_height - offset_y

    # Ensure the capture region doesn't exceed the window dimensions
    width = min(capture_width, window_width - offset_x)
    height = min(capture_height, window_height - offset_y)

    # Get the window's device context
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # Create a bitmap object to save the screenshot
    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(save_bitmap)

    # Adjust for offset by using BitBlt to copy from the offset region
    save_dc.BitBlt((0, 0), (width, height), mfc_dc, (offset_x, offset_y), win32con.SRCCOPY)

    # Convert the bitmap to an image object
    bmp_info = save_bitmap.GetInfo()
    bmp_str = save_bitmap.GetBitmapBits(True)
    image = Image.frombuffer('RGB', (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_str, 'raw', 'BGRX', 0, 1)

    # Cleanup resources
    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    # Save the image
    if save and save_path:
        image.save(save_path)

    return image


if __name__ == '__main__':
    hwnd = get_client_hwnd()
    image = capture_window_with_offset(hwnd=hwnd, capture_width=300, capture_height=300)
    image.show()
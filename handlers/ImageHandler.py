import win32ui
import win32gui
import ctypes
from PIL import Image
import cv2
import numpy as np
from pywinauto import Application


class ImageNotFound(Exception):

    def __init__(self, message):
        super().__init__(message)


def get_screenshot_of_window(hwnd, args=(0, 0, 1920, 1080), save=False, save_path='screenshot.png'):
    # Get the window size
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    left, top, right, bot = args
    width = right - left
    height = bot - top

    # Get the window's device context
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # Create a bitmap object to save the screenshot
    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(save_bitmap)

    # Capture the screenshot into the bitmap
    result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)  # 3 = Captures background window
    if result != 1:
        print("Failed to capture window content.")
        return None

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
    if save:
        image.save(save_path)

    return image


def get_screenshot_of_window_title(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    return get_screenshot_of_window(hwnd=hwnd)


def check_images(main_image, template, confidence=1):
    # Convert PIL images to OpenCV images
    main_image = np.array(main_image)
    template = np.array(template)

    # Convert images to grayscale for better matching
    main_gray = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Perform template matching
    result = cv2.matchTemplate(main_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Find the best match position using minMaxLoc
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Returns None if there aren't any matches with high enough confidence
    if max_val < confidence:
        raise ImageNotFound('No image found with necessary confidence level: ' + str(max_val) + ' < ' + str(confidence))

    # Get the dimensions of the template
    template_height, template_width = template_gray.shape

    # Draw a rectangle around the matched region on the main image
    top_left = max_loc
    bottom_right = (top_left[0] + template_width, top_left[1] + template_height)

    # Return the top left and bottom right coordinates
    return top_left, bottom_right


def find_best_match(main_image, template, convert_to_grayscale=True):
    # Convert PIL images to OpenCV images
    main_image = convert_PIL_to_cv2(main_image)
    template = convert_PIL_to_cv2(template)

    # Convert images to grayscale for better matching
    if convert_to_grayscale:
        main_gray = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    else:
        main_gray = main_image
        template_gray = template

    # Perform template matching
    result = cv2.matchTemplate(main_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Find the best match position using minMaxLoc
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Get the dimensions of the template
    template_height, template_width = template_gray.shape[0:2]

    # Draw a rectangle around the matched region on the main image
    top_left = max_loc
    bottom_right = (top_left[0] + template_width, top_left[1] + template_height)

    # Return the top left and bottom right coordinates
    return top_left, bottom_right, max_val


def is_image_on_screen(main_image, template, confidence=1):
    # Convert PIL images to OpenCV images
    main_image = convert_PIL_to_cv2(main_image)
    template = convert_PIL_to_cv2(template)

    # Convert images to grayscale for better matching
    main_gray = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Perform template matching
    result = cv2.matchTemplate(main_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Find the best match position using minMaxLoc
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Returns None if there aren't any matches with high enough confidence
    return max_val >= confidence


def draw_rectangle(image, top_left, bottom_right):
    image = convert_PIL_to_cv2(image)
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    cv2.imshow('Image with Rectangle', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show(image, grayscale=False):
    image = convert_PIL_to_cv2(image)
    if grayscale:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def convert_PIL_to_cv2(image):
    pil_image = image.convert('RGB')
    open_cv_image = np.array(pil_image)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return open_cv_image


def load_image(path):
    return Image.open(path)


def get_aqw_hwnd():
    app = Application(backend='win32').connect(title='GameLauncher on Artix Entertainment v.212', timeout=3)
    client = app['Chrome_WidgetWin_1']
    return client.handle






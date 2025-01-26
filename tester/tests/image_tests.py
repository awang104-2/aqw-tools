from handlers.ImageHandler import *
from . import top_level


def different_resolution_image_comparison():
    main_image = load_image(top_level + 'assets\\quest\\general\\log_complete.png')
    template = load_image(top_level + 'assets\\quest\\general\\log_complete_laptop.png')
    top_left, bot_right, confidence = find_best_match(main_image=template, template=main_image, draw_rect=True)
    print(f'Coordinates: ({top_left}, {bot_right})')
    print(f'Confidence: {confidence * 100:.2f}% match.')


def tesseract_ocr_test():
    pass

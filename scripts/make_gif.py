import os
from time import sleep
from PIL import Image
from io import BytesIO
from base64 import b64decode
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

_FORMAT = os.getenv("INPUT_FILE_FORMAT").upper().strip()
_FILE_NAME = os.getenv("INPUT_FILE_NAME")
_URL = os.getenv("INPUT_URL")
_WINDOW_W = int(os.getenv("INPUT_WINDOW_WIDTH"))
_WINDOW_H = int(os.getenv("INPUT_WINDOW_HEIGHT"))
_START_Y = os.getenv("INPUT_START_Y")
_STOP_Y = os.getenv("INPUT_STOP_Y")
_FINAL_W = os.getenv("INPUT_FINAL_WIDTH")
_FINAL_H = os.getenv("INPUT_FINAL_HEIGHT")
_SCROLL_STEP = os.getenv("INPUT_SCROLL_STEP")
_TIME_PER_FRAME = os.getenv("INPUT_TIME_PER_FRAME")
_RESIZING_FILTER = os.getenv("INPUT_RESIZING_FILTER").upper().strip()
_START_DELAY = int(os.getenv("INPUT_START_DELAY"))
_NO_SCROLL = bool(os.getenv("INPUT_NO_SCROLL"))
_TIME_BETWEEN_FRAMES = int(os.getenv("INPUT_TIME_BETWEEN_FRAMES"))
_NUMBER_OF_FRAMES = int(os.getenv("INPUT_NUMBER_OF_FRAMES"))

_DRIVER: webdriver.Firefox = None


def start_driver():
    """Start Selenium driver."""
    global _DRIVER

    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--width={_WINDOW_W}")
    options.add_argument(f"--height={_WINDOW_H}")

    _DRIVER = webdriver.Firefox(
        options=options,
        service=Service(
            executable_path="/app/geckodriver", log_path="/app/geckodriver.log"
        ),
    )
    _DRIVER.get(_URL)
    sleep(5)


def stop_driver():
    """Stop Selenium driver."""
    _DRIVER.quit()


def get_inner_size() -> tuple:
    """Get real inner window size"""
    return (
        int(_DRIVER.execute_script("return window.innerWidth;")),
        int(_DRIVER.execute_script("return window.innerHeight;")),
    )


def fix_aspect_ratio():
    """Fix window size to take into account browser toolbar and scrollbar."""
    print(f" - Window size before fix: {get_inner_size()}")
    real_width, real_height = get_inner_size()
    width_gap = _WINDOW_W - real_width
    height_gap = _WINDOW_H - real_height
    _DRIVER.set_window_size(_WINDOW_W + width_gap, _WINDOW_H + height_gap)
    print(f" - Window size after fix: {get_inner_size()}")


def validate_stop_y():
    """Validate user provided STOP_Y value.
    Must be defined and lower than total page height.
    Else, defaults to bottom of page.
    """
    global _STOP_Y

    page_height = _DRIVER.execute_script("return document.body.parentNode.scrollHeight")

    _STOP_Y = int(_STOP_Y)

    if _STOP_Y == 0:
        _STOP_Y = int(page_height)
        print(f" - STOP Y not defined, _STOP_Y set to {_STOP_Y}")
    elif _STOP_Y > int(page_height):
        _STOP_Y = page_height
        print(f" - STOP Y greater than page height, _STOP_Y set to {_STOP_Y}")


def take_screenshot(num: int):
    """Return current page display as base64

    Args:
        num (int): Screenshot number.

    Returns:
        str: base64 screenshot
    """
    print(f"Taking screenshot n°{num}")
    return _DRIVER.get_screenshot_as_base64()


def scroll_page():
    """Drive scrolling process and request screenshot at given scroll step.

    Returns:
        list: List of taken screenshots local files.
    """
    validate_stop_y()
    _DRIVER.execute_script(f"window.scrollTo(0, {_START_Y})")
    screenshot_list = [take_screenshot(num=0)]
    current_y = int(_START_Y)

    while current_y < _STOP_Y:
        current_y += int(_SCROLL_STEP)
        _DRIVER.execute_script(f"window.scrollTo(0, {current_y})")
        screenshot = take_screenshot(num=len(screenshot_list))
        screenshot_list.append(screenshot)
    print(f" - {len(screenshot_list)} screenshots taken")

    return screenshot_list


def capture_page():
    """Capture page without scrolling.

    Returns:
        list: List of taken screenshots local files.
    """
    screenshot_list = [take_screenshot(num=0)]

    for _ in range(_NUMBER_OF_FRAMES):
        screenshot = take_screenshot(num=len(screenshot_list))
        screenshot_list.append(screenshot)
        sleep(_TIME_BETWEEN_FRAMES / 1000)
    print(f" - {len(screenshot_list)} screenshots taken")

    return screenshot_list


def process_frame(file: str):
    """Open screenshot as a Pillow Image object and resize it.

    Args:
        file (str): Screenshot frame.

    Returns:
        Image: Pillow Image object.
    """
    image = Image.open(BytesIO(b64decode(file)))
    image = image.resize(
        size=(int(_FINAL_W), int(_FINAL_H)), resample=Image.Resampling[_RESIZING_FILTER]
    )

    return image


def create_gif(screenshots: list):
    """Use Pillow to create file.

    Args:
        screenshots (list): List of previously taken screenshots.
    """
    print(f" - Creating file: FINAL_WIDTH={_FINAL_W} | FINAL_HEIGHT={_FINAL_H}")
    fp_out = f"/app/{_FILE_NAME}.gif"
    img, *imgs = map(process_frame, screenshots)
    img.save(
        fp=fp_out,
        format="gif",
        append_images=imgs,
        save_all=True,
        duration=int(_TIME_PER_FRAME),
        loop=0,
        optimize=False,
    )


def create_webp(screenshots: list):
    """Use Pillow to create file.

    Args:
        screenshots (list): List of previously taken screenshots.
    """
    print(f" - Creating file: FINAL_WIDTH={_FINAL_W} | FINAL_HEIGHT={_FINAL_H}")
    fp_out = f"/app/{_FILE_NAME}.webp"
    img, *imgs = map(process_frame, screenshots)
    img.save(
        fp=fp_out,
        format="webp",
        append_images=imgs,
        save_all=True,
        duration=int(_TIME_PER_FRAME),
        loop=0,
        lossless=True,
        minimize_size=True,
        method=6,
        quality=100,
    )


if __name__ == "__main__":
    start_driver()
    fix_aspect_ratio()
    sleep(_START_DELAY / 1000)
    screenshots = capture_page() if _NO_SCROLL else scroll_page()
    stop_driver()

    if _FORMAT == "GIF":
        create_gif(screenshots=screenshots)
    elif _FORMAT == "WEBP":
        create_webp(screenshots=screenshots)
    else:
        raise Exception(f"Unknown file format:{_FORMAT}")

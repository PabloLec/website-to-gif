import os
from time import sleep
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

_GIF_NAME = os.getenv("INPUT_GIF_NAME")
_URL = os.getenv("INPUT_URL")
_WINDOW_W = os.getenv("INPUT_WINDOW_WIDTH")
_WINDOW_H = os.getenv("INPUT_WINDOW_HEIGHT")
_START_Y = os.getenv("INPUT_START_Y")
_STOP_Y = os.getenv("INPUT_STOP_Y")
_FINAL_W = os.getenv("INPUT_FINAL_WIDTH")
_FINAL_H = os.getenv("INPUT_FINAL_HEIGHT")
_SCROLL_STEP = os.getenv("INPUT_SCROLL_STEP")
_TIME_PER_FRAME = os.getenv("INPUT_TIME_PER_FRAME")

_DRIVER = None


def start_driver():
    """Start Selenium driver."""
    global _DRIVER

    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--width={_WINDOW_W}")
    options.add_argument(f"--height={_WINDOW_H}")

    _DRIVER = webdriver.Firefox(
        options=options,
        service_log_path="/app/geckodriver.log",
    )
    _DRIVER.get(_URL)
    sleep(5)


def close_driver():
    """Stop Selenium driver."""
    _DRIVER.close()
    _DRIVER.quit()


def take_screenshot(num: int):
    """Save current page display as a .png

    Args:
        num (int): Screenshot number.

    Returns:
        str: Screenshot save path.
    """
    path = f"/app/screenshot{num}.png"
    _DRIVER.save_screenshot(path)

    return path


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


def process_frame(file: str):
    """Open screenshot file as a Pillow Image object and resize it.

    Args:
        file (str): Local screenshot path.

    Returns:
        Image: Pillow Image object.
    """
    image = Image.open(file)
    image = image.resize(
        size=(int(_FINAL_W), int(_FINAL_H)),
        resample=Image.LANCZOS,
        reducing_gap=3,
    )

    return image


def create_gif(screenshots: list):
    """Use Pillow to create GIF.

    Args:
        screenshots (list): List of taken screenshots local files.
    """
    fp_out = f"/app/{_GIF_NAME}.gif"
    img, *imgs = map(process_frame, screenshots)
    img.save(
        fp=fp_out,
        format="GIF",
        append_images=imgs,
        save_all=True,
        duration=int(_TIME_PER_FRAME),
        loop=0,
        optimize=False,
    )


start_driver()
screenshots = scroll_page()
close_driver()
create_gif(screenshots=screenshots)

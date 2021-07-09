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
_QUALITY = os.getenv("INPUT_QUALITY")

_DRIVER = None


def take_screenshot(num: int):
    global _DRIVER

    path = f"/app/screenshot{str(num)}.png"
    _DRIVER.save_screenshot(path)

    return path


def scroll_page():
    global _START_Y
    global _STOP_Y
    global _SCROLL_STEP
    global _DRIVER

    page_height = _DRIVER.execute_script("return document.body.parentNode.scrollHeight")

    _STOP_Y = int(_STOP_Y)

    if _STOP_Y == 0:
        _STOP_Y = int(page_height)
        print(f" - STOP Y not defined, _STOP_Y set to {_STOP_Y}")
    elif _STOP_Y > int(page_height):
        _STOP_Y = page_height
        print(f" - STOP Y greater than page height, _STOP_Y set to {_STOP_Y}")

    _SCROLL_STEP = int(_SCROLL_STEP)

    _DRIVER.execute_script(f"window.scrollTo(0, {_START_Y})")
    screenshot_list = [take_screenshot(num=0)]
    current_y = int(_START_Y)

    while current_y < _STOP_Y:
        current_y += _SCROLL_STEP
        _DRIVER.execute_script(f"window.scrollTo(0, {str(current_y)})")
        screenshot = take_screenshot(num=len(screenshot_list))
        screenshot_list.append(screenshot)

    print(f" - {str(len(screenshot_list))} screenshots taken")

    return screenshot_list


def start_driver():
    global _URL
    global _WINDOW_W
    global _WINDOW_H
    global _DRIVER

    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--width={_WINDOW_W}")
    options.add_argument(f"--height={_WINDOW_H}")
    _DRIVER = webdriver.Firefox(options=options, service_log_path="/app/geckodriver.log")
    _DRIVER.get(_URL)
    sleep(5)


def close_driver():
    global _DRIVER

    _DRIVER.close()
    _DRIVER.quit()


def create_gif(screenshots: list):
    global _GIF_NAME
    global _QUALITY

    fp_out = f"/app/{_GIF_NAME}.gif"
    img, *imgs = [Image.open(f).resize((int(_FINAL_W), int(_FINAL_H))) for f in screenshots]
    img.save(
        fp=fp_out,
        format="GIF",
        append_images=imgs,
        save_all=True,
        duration=int(_TIME_PER_FRAME),
        loop=0,
        optimize=True,
        quality=_QUALITY,
    )


start_driver()
screenshots = scroll_page()
close_driver()
create_gif(screenshots=screenshots)

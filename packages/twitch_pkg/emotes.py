from lxml import html
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
import warnings

warnings.filterwarnings("ignore")


def create_driver() -> webdriver.Remote:

    options = Options()

    # Run the script with a headless webdriver.
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--dns-prefetch-disable")

    # Prevent the webdriver from printing messages.
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Remote(
        "http://chrome:4444",
        desired_capabilities=DesiredCapabilities.CHROME,
        options=options,
    )

    sleep(0.5)

    return driver


def get_streamer_id(streamer: str, driver: webdriver.Remote) -> str:
    """
    This function obtains the broadcaster_id linked to a Twitch streamer.

    Parameters:
    ---------------
        streamer:
            The name of the Twitch streamer whose broadcaster_id is to be obtained.

    Returns:
    ---------------
        The broacaster_id linked to the provided Twitch streamer.
    """

    driver.get("https://twitchemotes.com")

    searchbox = driver.find_element(By.XPATH, "/html/body/nav/div/form/input[1]")

    searchbox.send_keys(streamer)

    searchbutton = driver.find_element(By.XPATH, "/html/body/nav/div/form/button")
    searchbutton.click()

    url = driver.current_url

    return url[re.search(r"\d", url).start() :]


def get_streamer_emotes(streamer: str, driver: webdriver.Remote) -> list:
    """
    This function obtains the emotes linked to a particular Twitch streamer.

    Parameters:
    ---------------
        streamer:
            The name of the Twitch streamer whose emotes are to be obtained.

    Returns:
    ---------------
        A list containing the particular Twitch streamer emotes.
    """

    streamer_id = get_streamer_id(streamer, driver)

    driver.get(f"https://twitchemotes.com/channels/{streamer_id}")

    sleep(0.5)

    tree = html.fromstring(driver.page_source)

    emotes = [
        emote.replace("\n", "").lower()
        for emote in tree.xpath("//div[@class='col-md-2']/center/text()")
        if emote.replace("\n", "")
    ]

    return [emote for emote in emotes if emote != " "]


def get_twitch_emotes(driver: webdriver.Remote) -> list:
    """
    This function obtains the global Twitch emotes.

    Returns:
    ---------------
        A list containing the global Twitch emotes.
    """

    driver.get("https://twitchemotes.com")

    sleep(0.5)

    tree = html.fromstring(driver.page_source)

    emotes = [
        emote.replace("\n", "").lower()
        for emote in tree.xpath("//div[@class='col-md-2']/center/text()")
        if emote.replace("\n", "")
    ]

    return [emote for emote in emotes if emote != " "]


def get_frankerfacez_emotes(pages_number: int, driver: webdriver.Remote) -> list:
    """
    This function obtains the third-party emotes from "FrankerFaceZ" (FFZ).

    Parameters:
    ---------------
        pages_number:
            Number of pages to go through.

    Returns:
    ---------------
        A list containing the FFZ emotes.
    """

    emotes = []

    for i in range(pages_number):

        driver.get(f"https://www.frankerfacez.com/emoticons/?page={i}")

        sleep(0.5)

        tree = html.fromstring(driver.page_source)

        emotes += [
            emote.replace("\n", "").lower()
            for emote in tree.xpath("//td[@class='emote-name text-left']/a/text()")
        ]

    return [emote for emote in emotes if emote != " "]


def get_betterttv_emotes(scrolls_number: int, driver: webdriver.Remote) -> list:
    """
    This function obtains the third-party emotes from "Better Twitch TV" (BTTV).

    Parameters:
    ---------------
        scrolls_number:
            Number of scrolls down to reproduce on each category page.

    Returns:
    ---------------
        A list containing the BTTV emotes.
    """

    categories = ["top", "trending", "global"]

    emotes = []

    for category in categories:

        driver.get(f"https://betterttv.com/emotes/{category}")

        sleep(0.5)

        # Set the last scroll height.
        last_height = driver.execute_script("return document.body.scrollHeight")

        for i in range(scrolls_number):

            # Scroll down to the bottom of the page.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for the page to load.
            sleep(0.5)

            # Set the new scroll height.
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

        tree = html.fromstring(driver.page_source)

        emotes += [
            emote.replace("\n", "").lower()
            for emote in tree.xpath(
                "//p[@class='chakra-text EmoteCards_emoteCardCode__BP2dI css-0']/text()"
            )
        ]

    return [emote for emote in emotes if emote != " "]


def get_labeled_emotes() -> dict:
    """
    This function returns a dictionary containing the manually
    labeled global emotes and their meaning.
    """

    files = ["twitch_emotes.txt", "frankerfacez_emotes.txt", "bettertv_emotes.txt"]

    emotes = {}

    for file in files:
        with open(f"packages/twitch_pkg/labeled_emotes/{file}", "r") as file:
            lines = file.readlines()

        for line in lines:
            if "#" in line:
                emote = line[:-1].split(sep="#")
                emotes[emote[0]] = emote[1]

    # Dictionary sorted by value name lenght.
    return {emote: emotes[emote] for emote in sorted(emotes, key=len, reverse=True)}


def get_global_emotes(
    pages_number: int, scrolls_number: int, driver: webdriver.Remote
) -> list:
    """
    This function obtains all the global Twitch global emotes from multiple sources

    Returns:
    ---------------
        A sorted list containing all the Twitch global emotes.
    """

    global_emotes = get_twitch_emotes(driver=driver)
    global_emotes += get_frankerfacez_emotes(pages_number=pages_number, driver=driver)
    global_emotes += get_betterttv_emotes(scrolls_number=scrolls_number, driver=driver)

    # List sorted by name lenght.
    return sorted(
        [
            *set(global_emotes),
        ],
        key=len,
        reverse=True,
    )

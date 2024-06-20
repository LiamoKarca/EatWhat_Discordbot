import time
import urllib.parse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError


def scroll_restaurants_list(page):
    """
    Scroll through the restaurant list on the page.

    Args:
        page (playwright.sync_api.Page): The page to scroll.
    """
    print("Scroll: Is at bottom:", is_at_page_bottom(page))
    if is_at_page_bottom(page):
        print("Scroll: Reached bottom.")
    else:
        print("Scroll: Not yet reached!!!")
    for _ in range(1):  # Can adjust scrolling times
        if page.is_closed():
            break
        html = page.inner_html('body')
        soup = BeautifulSoup(html, 'html.parser')
        categories = soup.select('.hfpxzc')
        if categories:
            last_category_in_page = categories[-1].get('aria-label')
            last_category_location = page.locator(f"text={last_category_in_page}")
            try:
                last_category_location.scroll_into_view_if_needed(timeout=10000)
            except TimeoutError:
                print("Timeout occurred while scrolling.")
                break


def get_restaurants(encoding_landmark):
    """
    Get a list of restaurants near the specified landmark.

    Args:
        encoding_landmark (str): The URL encoded landmark to search near.

    Returns:
        list: A list of dictionaries, each containing the name and link of a restaurant.
    """
    restaurants = []
    last_update_time = time.time()  # Initialize the last update time
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Launch browser
            context = browser.new_context(geolocation={"longitude": 120.5966694, "latitude": 22.6427084},
                                          permissions=["geolocation"])
            page = context.new_page()

            # Listen for dialogs and accept them
            page.on('dialog', lambda dialog: dialog.accept())

            # Open specified URL in Google Maps
            page.goto(
                f"https://www.google.com.tw/maps/search/{encoding_landmark}/@22.6427084,120.5966694,"
                "15.33z/data=!4m4!2m3!5m1!2e1!6e5?entry=ttu")

            count = 0

            while True:
                div_aifcqe = page.query_selector(
                    '.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd')  # Find div elements with class 'aIFcqe'
                hfpxzc_elements = div_aifcqe.query_selector_all(
                    '.hfpxzc')  # Find elements with specific class in that div

                for item in hfpxzc_elements:
                    link = item.get_attribute('href')
                    name = item.get_attribute('aria-label')

                    if not any(rest['link'] == link for rest in restaurants):
                        restaurants.append({'name': name, 'link': link})
                        last_update_time = time.time()  # Update the last update time

                        count += 1
                        print(f'Count {count}: {name}')

                # Check if more than 10 seconds have passed since the last update
                if time.time() - last_update_time > 10:
                    print("No new items for more than 10 seconds. Returning the list of restaurants.")
                    return restaurants

                if not is_at_page_bottom(page):
                    scroll_restaurants_list(page)

                if is_at_page_bottom(page):
                    for item in hfpxzc_elements:
                        link = item.get_attribute('href')
                        name = item.get_attribute('aria-label')
                        print(f'Count {count}: {name}')
                        if not any(rest['link'] == link for rest in restaurants):
                            restaurants.append({'name': name, 'link': link})
                            count += 1
                            print(f'Count {count}: {name}')

                    print("GetRest: Reached bottom.")
                    break

    except Exception as e:
        print("An error occurred:", e)
    finally:
        return restaurants



def is_at_page_bottom(page):
    """
    Check if the bottom of the page is reached.

    Args:
        page (playwright.sync_api.Page): The page to check.

    Returns:
        bool: True if the bottom is reached, False otherwise.
    """
    css_selector = 'p.fontBodyMedium:has-text("你已看完所有搜尋結果。")'
    elements = page.query_selector_all(css_selector)
    if len(elements) > 0:
        time.sleep(3)  # Wait for 3 seconds
        elements = page.query_selector_all(css_selector)
        return len(elements) > 0
    return False


def url_encoding(nearby_landmark):
    """
    URL encode the given nearby landmark.

    Args:
        nearby_landmark (str): The landmark to encode.

    Returns:
        str: The URL encoded landmark.
    """
    encoding_landmark = urllib.parse.quote(nearby_landmark)
    return encoding_landmark

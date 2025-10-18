import os
import re
import random
import platform

from playwright.sync_api import sync_playwright


match platform.system():
    case "Linux":
        os.environ["DISPLAY"] = ":99"

    case _:
        pass


def move_to(page, selector):
    element = page.locator(selector)
    if element.is_visible():
        element_position = element.bounding_box()
        if element_position:
            x_coordinate = element_position["x"] + element_position["width"] / 2
            y_coordinate = element_position["y"] + element_position["height"] / 2
            page.mouse.move(x_coordinate, y_coordinate, steps=20)


def mimic_action(page, selector, min=500, max=1000):
    page.wait_for_timeout(random.randrange(min, max))
    move_to(page, selector)
    page.wait_for_timeout(random.randrange(min, max))


def click_element(page, selector):
    if selector == "#NextButton":
        mimic_action(page, selector, 1000, 2000)
    else:
        mimic_action(page, selector)

    page.wait_for_selector(selector)
    element = page.locator(selector).first
    element.wait_for(state="visible")
    page.wait_for_timeout(random.randrange(500, 1000))
    element.click()
    page.wait_for_timeout(random.randrange(1000, 1500))


def fill_element(page, selector, value):
    # mimic_action(page, selector)
    page.wait_for_selector(selector)
    element = page.locator(selector).first
    element.wait_for(state="visible")
    page.wait_for_timeout(random.randrange(200, 500))
    element.fill(value)
    page.wait_for_timeout(random.randrange(200, 500))


def select_satisfy_option(page, element_id):
    if (
        page.query_selector(f"#FNSR{element_id} > td.Opt5.inputtyperbloption > label")
        is not None
    ):
        random_number = random.randint(1, 100)

        if random_number <= 30:
            click_element(
                page, f"#FNSR{element_id} > td.Opt2.inputtyperbloption > label"
            )
        elif random_number <= 60:
            click_element(
                page, f"#FNSR{element_id} > td.Opt3.inputtyperbloption > label"
            )
        else:
            click_element(
                page, f"#FNSR{element_id} > td.Opt4.inputtyperbloption > label"
            )


def progress(page):
    selectors = page.locator('[id^="textR"]')
    pattern = r"^textR\d{6}$"

    for index in range(selectors.count()):
        element_id = selectors.nth(index).get_attribute("id")
        if not re.match(pattern, element_id):
            continue

        element_id = element_id[-6:]
        # What was your visit type? Collected at counter to take away
        if element_id == "000005":
            click_element(page, r"#textR000005\.2")
        # Where did you place your order? Touch Screen Order Point
        elif element_id == "000006":
            click_element(page, r"#textR000006\.2")
        # Please rate your overall satisfaction. Neither Satisfied Nor Dissatisfied
        elif element_id == "000002":
            click_element(page, r"#FNSR000002 > td.Opt3.inputtyperbloption > label")
        # Did you experience a problem on this occasion? No
        elif element_id == "000026":
            click_element(page, r"#FNSR000026 > td.Opt2.inputtyperbloption > label")
        # Was your order accurate? Yes
        elif element_id == "000052":
            click_element(page, r"#FNSR000052 > td.Opt1.inputtyperbloption > label")
        # Did you use My McDonald's Rewards on this visit? Yes
        elif element_id == "000384":
            click_element(page, r"#FNSR000384 > td.Opt1.inputtyperbloption > label")
        # Would you like to answer a few more questions about your experience? No
        elif element_id == "000466":
            click_element(page, r"#FNSR000466 > td.Opt2.inputtyperbloption > label")
        else:
            select_satisfy_option(page, element_id)

    click_element(page, "#NextButton")


mcURL = r"https://www.mcdfoodforthoughts.com/"

with open("voucher.txt", "r") as f:
    lines = f.readlines()
code = lines[0]

price = f"{random.randint(3, 23)}9{random.randint(6, 9)}"
first_name = "First Name"
second_name = "Second Name"
email = "mcdonalds@example.com"


with sync_playwright() as p:
    browser = p.webkit.launch(slow_mo=100)
    # browser = p.webkit.launch(headless=False, slow_mo=100)
    context = browser.new_context(
        **p.devices["Desktop Chrome"],
        locale="en-GB",
        timezone_id="Europe/London",
        geolocation={
            "latitude": round(random.uniform(51.28, 51.70), 6),
            "longitude": round(random.uniform(-0.51, 0.33), 6),
        },
        permissions=["geolocation"],
    )
    page = context.new_page()

    try:
        page.goto(mcURL)

        click_element(page, "#NextButton")

        if (
            page.query_selector(
                "#surveyQuestions > fieldset > div > div:nth-child(1) > span > label"
            )
            is not None
        ):
            click_element(
                page,
                "#surveyQuestions > fieldset > div > div:nth-child(1) > span > label",
            )
            click_element(page, "#NextButton")

        fill_element(page, "#CN1", code[0:4])
        fill_element(page, "#CN2", code[5:9])
        fill_element(page, "#CN3", code[10:14])
        page.wait_for_timeout(random.randrange(1000, 1500))

        fill_element(page, "#AmountSpent1", price[:-2])
        fill_element(page, "#AmountSpent2", price[-2:])
        page.wait_for_timeout(random.randrange(1000, 1500))

        click_element(page, "#NextButton")
        page.wait_for_timeout(random.randrange(1000, 1500))

        while page.wait_for_selector("#ProgressPercentage").inner_text() != "97%":
            progress(page)

        click_element(page, r"#textR000383\.1")
        click_element(page, "#NextButton")
        page.wait_for_timeout(random.randrange(1000, 1500))

        fill_element(page, "#S000068", first_name)
        fill_element(page, "#S000073", second_name)
        fill_element(page, "#S000070", email)
        fill_element(page, "#S000071", email)
        page.wait_for_timeout(random.randrange(1000, 1500))

        click_element(page, "#NextButton")
        page.wait_for_timeout(random.randrange(20000, 25000))

        page.wait_for_selector("#finishIncentiveHolder > h2")

        # Update the remaining voucher
        with open("voucher.txt", "w") as f:
            f.write("".join(lines[1:]))

    except Exception as e:
        print("Mcdonald's promotion", f"failed with message {str(e)}")

    finally:
        browser.close()

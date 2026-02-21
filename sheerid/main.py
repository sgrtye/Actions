import os

import requests
from playwright.sync_api import sync_playwright

one_idkey: str | None = os.getenv("ONE_IDKEY")
telebot_user: str | None = os.getenv("TELEBOT_USER")
telebot_token: str | None = os.getenv("TELEBOT_TOKEN")

if one_idkey is None or telebot_user is None or telebot_token is None:
    print("Error: Missing one or more required secrets. Exiting.")
    raise SystemExit(1)
else:
    TIMEOUT: int = 5000
    ONE_IDKEY: str = one_idkey
    ONE_IDKEY_URL: str = "https://one.idkey.cc/"
    TELEBOT_USER: str = telebot_user
    TELEBOT_TOKEN: str = telebot_token


def ONE_IDKEY_login(page) -> None:
    page.goto(ONE_IDKEY_URL)

    page.wait_for_selector("#navLoginBtn").click()

    page.wait_for_selector("#loginUser").click()
    page.fill("#loginUser", ONE_IDKEY)

    page.wait_for_selector("#loginPass").click()
    page.fill("#loginPass", ONE_IDKEY)

    page.wait_for_selector("#form-login > button").click()

    page.wait_for_timeout(TIMEOUT)


def daily_checkin(page) -> None:
    page.wait_for_selector(
        "#navUserInfo > div.action-group > button:nth-child(1)"
    ).click()

    page.wait_for_timeout(TIMEOUT)


def failed_attempt(e: Exception) -> None:
    url: str = f"https://api.telegram.org/bot{TELEBOT_TOKEN}/sendMessage"
    payload: dict[str, str] = {"chat_id": TELEBOT_USER, "text": f"Error: {repr(e)}"}
    requests.post(url, json=payload)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**p.devices["Desktop Chrome"])
        page = context.new_page()

        try:
            ONE_IDKEY_login(page)

            daily_checkin(page)

        except Exception as e:
            failed_attempt(e)

        finally:
            browser.close()


if __name__ == "__main__":
    main()

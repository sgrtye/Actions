import os

import requests
from playwright.sync_api import sync_playwright


vpn_url: str | None = os.getenv("VPN_URL")
vpn_username: str | None = os.getenv("VPN_USERNAME")
vpn_password: str | None = os.getenv("VPN_PASSWORD")
telebot_user: str | None = os.getenv("TELEBOT_USER")
telebot_token: str | None = os.getenv("TELEBOT_TOKEN")

if (
    vpn_url is None
    or vpn_username is None
    or vpn_password is None
    or telebot_user is None
    or telebot_token is None
):
    print("Error: Missing one or more required secrets. Exiting.")
    raise SystemExit(1)
else:
    TIMEOUT: int = 5000
    VPN_URL: str = vpn_url
    VPN_USERNAME: str = vpn_username
    VPN_PASSWORD: str = vpn_password
    TELEBOT_USER: str = telebot_user
    TELEBOT_TOKEN: str = telebot_token


def VPN_login(page) -> None:
    page.goto(VPN_URL)

    page.wait_for_selector("#email").click()
    page.fill("#email", VPN_USERNAME)

    page.wait_for_selector("#password").click()
    page.fill("#password", VPN_PASSWORD)

    page.wait_for_selector(
        "#app > section > div > div > div > div.card.card-primary > form > div > div:nth-child(5) > button"
    ).click()
    page.wait_for_timeout(TIMEOUT)

    if (
        page.query_selector(
            "#popup-ann-modal > div > div > div.modal-footer.bg-whitesmoke.br > button"
        )
        is not None
    ):
        page.wait_for_selector(
            "#popup-ann-modal > div > div > div.modal-footer.bg-whitesmoke.br > button"
        ).click()
        page.wait_for_timeout(TIMEOUT)


def verify_status(page) -> bool:
    status = page.wait_for_selector("#checkin-div").inner_text()
    return status == " 明日再来"


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
            VPN_login(page)
            if verify_status(page):
                exit(0)

            page.wait_for_selector("#checkin-div > a")
            element = page.locator("#checkin-div > a")
            element.click()

            page.wait_for_timeout(TIMEOUT)

            verify_status(page)

        except Exception as e:
            failed_attempt(e)

        finally:
            browser.close()


if __name__ == "__main__":
    main()

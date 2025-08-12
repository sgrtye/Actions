from playwright.sync_api import sync_playwright


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto("https://www.wikipedia.org/")

        print(f"Page Title: {page.title()}")

        body_content = page.locator("body").inner_text()
        print("\n--- Page Body Content ---\n")
        print(body_content)

        browser.close()


if __name__ == "__main__":
    main()

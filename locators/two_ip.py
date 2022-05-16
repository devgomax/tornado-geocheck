from playwright.async_api._generated import Page


class Locators:
    def __init__(self, page: Page):
        self.page = page
        self.rows = self.page.locator("#compare-block >> tr")

from playwright.async_api._generated import Page


class Locators:
    def __init__(self, page: Page):
        self.page = page
        self.input = self.page.locator('input#host.input')
        self.submit_button = self.page.locator('button.btn-ping')
        self.rows = self.page.locator("div.card__row")

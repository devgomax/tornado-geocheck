from playwright.async_api._generated import Page


class Locators:
    def __init__(self, page: Page):
        self.page = page
        self.input_ip_textarea = self.page.locator('#searchIP')
        self.submit_button = self.page.locator('#searchIPButton')

import re
from django.core import mail
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest


TEST_EMAIL = 'skillcraba@gmail.com'
SUBJECT = 'Your login link for Lists-tdd'


class LoginTest(FunctionalTest):
    def test_can_get_email_link_to_login(self):
        # Edith goes to the awesome superlists site and notices a "Log in" section in the navbar for the first time
        # It's telling her to enter her email address, so she does
        self.browser.get(self.live_server_url)
        self.browser.find_element(by=By.NAME, value='email').send_keys(TEST_EMAIL)
        self.browser.find_element(by=By.NAME, value='email').send_keys(Keys.ENTER)

        # A message appears telling her an email has been sent
        self.wait_for(lambda: self.assertIn(
            'Check your email',
            self.browser.find_element(by=By.TAG_NAME, value='body').text
        ))

        # She checks her email and finds a message
        email = mail.outbox[0]
        self.assertIn(TEST_EMAIL, email.to)
        self.assertEqual(email.subject, SUBJECT)

        # It has a url link in it
        self.assertIn('Use this link to log in', email.body)
        url_search = re.search(r'http://.+/.+$', email.body)
        if not url_search:
            self.fail(f'Couldnt find url in email body:\n{email.body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # She clicks it
        self.browser.get(url)

        # She is logged in
        self.wait_for(
            lambda: self.browser.find_element(by=By.LINK_TEXT, value='Log out')
        )
        navbar = self.browser.find_element(by=By.CSS_SELECTOR, value='.navbar')
        self.assertIn(TEST_EMAIL, navbar.text)

        # Now she logs out
        self.browser.find_element(by=By.LINK_TEXT, value='Log out').click()

        # She is logged out
        self.wait_for(
            lambda: self.browser.find_element(by=By.NAME, value='email')
        )
        navbar = self.browser.find_element(by=By.CSS_SELECTOR, value='.navbar')
        self.assertNotIn(TEST_EMAIL, navbar.text)
from selenium.webdriver import ChromeOptions

class StealthChromeOptions(ChromeOptions):
    def __init__(self, headless: bool = True, timeout: int = 10):
        super().__init__()

        args = (
            "--no-sandbox",
            "--disable-gpu",
            "--disable-infobars",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-blink-features",
            "--disable-blink-features=AutomationControlled",
            "--disable-timezone-tracking-option",
            "--disable-fine-grained-time-zone-detection",
            "--enable-popup-blocking"
        )

        if headless:
            args += ("--headless=new")

        for arg in args:
            self.add_argument(arg)

        self.page_load_strategy = "eager"
        self.unhandled_prompt_behavior = "accept"
        self.accept_insecure_certs = True
        self.timeout = timeout
        self.add_experimental_option = {
            "excludeSwitches": ["enable-automation"],
            "useAutomationExtension": False
        }

    def build_user_agent():
    """Build a Mozilla/5.0 compatible User-Agent string"""

        ua_tuple = (
            'Mozilla/5.0',
            '(%s; U; %s; en-us)' % (platform.platform(),
                                    platform.architecture()[0]),
            'Python/%s' % platform.python_version(),
            '(KHTML, like Gecko)',
            'speedtest-cli/%s' % __version__
        )
        user_agent = ' '.join(ua_tuple)
        printer('User-Agent: %s' % user_agent, debug=True)
        return user_agent
from selenium.webdriver import ChromeOptions


selenium_args = ChromeOptions()
selenium_args.add_argument('--headless')
selenium_args.add_argument('--no-sandbox')
selenium_args.add_argument('--disable-setuid-sandbox')
selenium_args.add_argument('--hide-scrollbars')
selenium_args.add_experimental_option('excludeSwitches', ['enable-logging'])


pyppeteer_options = {'executablePath': '/usr/bin/google-chrome',
                     'args': ['--no-sandbox',
                              '--disable-setuid-sandbox',
                              '--autoplay-policy=user-gesture-required',
                              '--disable-background-networking',
                              '--disable-background-timer-throttling',
                              '--disable-backgrounding-occluded-windows',
                              '--disable-breakpad',
                              '--disable-client-side-phishing-detection',
                              '--disable-component-update',
                              '--disable-default-apps',
                              '--disable-dev-shm-usage',
                              '--disable-domain-reliability',
                              '--disable-extensions',
                              '--disable-features=AudioServiceOutOfProcess',
                              '--disable-hang-monitor',
                              '--disable-ipc-flooding-protection',
                              '--disable-notifications',
                              '--disable-offer-store-unmasked-wallet-cards',
                              '--disable-popup-blocking',
                              '--disable-print-preview',
                              '--disable-prompt-on-repost',
                              '--disable-speech-api',
                              '--disable-sync',
                              '--hide-scrollbars',
                              '--ignore-gpu-blacklist',
                              '--metrics-recording-only',
                              '--mute-audio',
                              '--no-default-browser-check',
                              '--no-first-run',
                              '--no-pings',
                              '--no-zygote',
                              '--password-store=basic',
                              '--use-mock-keychain'],

                     'userDataDir': './temp'}


pyppeteer_screenshot_options = {
    'width': 1920,
    'fullPage': True,
}

pyppeteer_goto_options = {
    'timeout': 0
}

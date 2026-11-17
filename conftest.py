import os
import pytest
from datetime import datetime
from playwright.sync_api import Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}}


@pytest.fixture
def page(browser: Browser, base_url: str):
    context: BrowserContext = browser.new_context(base_url=base_url)
    p: Page = context.new_page()
    yield p
    p.close()
    context.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page: Page = item.funcargs.get("page")
        if page is None:
            return

        feature = item.fspath.dirpath().basename
        timestamp = datetime.now().strftime("%d-%m-%Y_%H.%M")
        bug_dir = os.path.join("bug", feature, timestamp)
        os.makedirs(bug_dir, exist_ok=True)

        screenshot_path = os.path.join(bug_dir, "screenshot.png")
        page.screenshot(path=screenshot_path)

        log_path = os.path.join(bug_dir, "error.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(str(report.longrepr))

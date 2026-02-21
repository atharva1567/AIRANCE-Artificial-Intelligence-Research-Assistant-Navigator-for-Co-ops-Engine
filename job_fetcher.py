# job_fetcher.py

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

driver = None

# -----------------------------
# DRIVER INIT
# -----------------------------
def init_driver():
    global driver
    if driver is None:
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
    return driver

# -----------------------------
# OPEN ONLY LINKEDIN + INDEED
# -----------------------------
def open_source_tabs(field, location, job_type):
    init_driver()

    query = f"{field} {job_type}"

    urls = {
        "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}",
        "indeed": f"https://ca.indeed.com/jobs?q={query}&l={location}",
    }

    # Open LinkedIn first
    driver.get(urls["linkedin"])
    time.sleep(2)

    # Open Indeed
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(urls["indeed"])
    time.sleep(2)

    # Return to LinkedIn tab
    driver.switch_to.window(driver.window_handles[0])

# -----------------------------
# TAB SWITCHING
# -----------------------------
def _switch_to_domain(domain):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        try:
            if domain in driver.current_url:
                return True
        except:
            pass
    return False

def _scroll():
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
    except:
        pass

# -----------------------------
# UNIVERSAL HELPERS
# -----------------------------
def _extract(card, selectors):
    for sel in selectors:
        try:
            text = card.find_element(By.CSS_SELECTOR, sel).text.strip()
            if text:
                return text
        except:
            pass
    return ""

def _extract_link(card, selectors):
    for sel in selectors:
        try:
            link = card.find_element(By.CSS_SELECTOR, sel).get_attribute("href")
            if link:
                return link
        except:
            pass
    return ""

# -----------------------------
# LINKEDIN SCRAPER
# -----------------------------
def fetch_linkedin(field, location, job_type):
    init_driver()
    if not _switch_to_domain("linkedin.com"):
        return []

    time.sleep(2)

    # Close cookie or login popups
    for sel in [
        "button[aria-label='Dismiss']",
        "button.artdeco-modal__dismiss",
        "button[aria-label='Close']"
    ]:
        try:
            driver.find_element(By.CSS_SELECTOR, sel).click()
            time.sleep(1)
        except:
            pass

    # Scroll multiple times to force job cards to load
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1)

    jobs = []
    cards = driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")

    # If still empty, try fallback selector
    if not cards:
        cards = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list li")

    for card in cards[:5]:
        title = _extract(card, ["h3", ".base-search-card__title"])
        company = _extract(card, ["h4", ".base-search-card__subtitle"])
        loc = _extract(card, [".job-search-card__location"])
        link = _extract_link(card, ["a.base-card__full-link", "a"])

        if title:
            jobs.append({
                "title": title,
                "company": company,
                "location": loc,
                "source": "LinkedIn",
                "link": link
            })

    return jobs

# -----------------------------
# INDEED SCRAPER
# -----------------------------
def fetch_indeed(field, location, job_type):
    init_driver()
    if not _switch_to_domain("indeed.com"):
        return []

    time.sleep(1)
    _scroll()

    jobs = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon, a.tapItem")

    for card in cards[:5]:
        title = _extract(card, ["h2.jobTitle", "h2"])
        company = _extract(card, ["span.companyName", "span[data-testid='company-name']"])
        loc = _extract(card, ["div.companyLocation", "div[data-testid='text-location']"])
        link = _extract_link(card, ["a.jcs-JobTitle", "a.tapItem", "a"])

        if title:
            jobs.append({
                "title": title,
                "company": company,
                "location": loc,
                "source": "Indeed",
                "link": link
            })

    return jobs

# -----------------------------
# AGGREGATOR
# -----------------------------
def fetch_all_jobs(field, location, job_type):
    return (
        fetch_linkedin(field, location, job_type)
        + fetch_indeed(field, location, job_type)
    )

from flask import Flask, jsonify, request, send_file
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime

app = Flask(__name__)
DEBUG_FILE = "debug.html"

def parse_fuzzy_date(date_str: str) -> str:
    date_str = re.sub(r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b", "", date_str)
    date_str = re.sub(r"(\d{1,2})(st|nd|rd|th)?", r"\1", date_str).strip()

    try:
        parsed = datetime.strptime(date_str, "%d %B")
        year = datetime.now().year
        full_date = parsed.replace(year=year)
        if full_date.date() < datetime.now().date():
            full_date = full_date.replace(year=year + 1)
        return full_date.strftime("%Y-%m-%d")
    except Exception:
        return None

def extract_dates(soup, section_heading):
    section = soup.find("h2", string=re.compile(section_heading, re.IGNORECASE))
    if not section:
        return None, None

    # Search nearby <p> tags for "Next collections:"
    next_p = section.find_next("p")
    while next_p:
        if "Next collections:" in next_p.get_text():
            break
        next_p = next_p.find_next("p")

    if not next_p:
        return None, None

    matches = re.findall(r"(\d{1,2}(st|nd|rd|th)?\s+\w+)", next_p.get_text())
    dates = [parse_fuzzy_date(m[0]) for m in matches if parse_fuzzy_date(m[0])]

    first_date = dates[0] if len(dates) > 0 else None
    second_date = dates[1] if len(dates) > 1 else None
    return first_date, second_date

def fetch_bin_dates(uprn: str, save_html: bool = False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://www.adur-worthing.gov.uk/bin-day/?brlu-selected-address={uprn}"
        page.goto(url, timeout=20000)
        page.wait_for_selector("main", timeout=10000)

        html = page.content()

        if save_html:
            with open(DEBUG_FILE, "w", encoding="utf-8") as f:
                f.write(html)

        soup = BeautifulSoup(html, "html.parser")

        black1, black2 = extract_dates(soup, "General rubbish")
        blue1, blue2 = extract_dates(soup, "Recycling")
        garden1, garden2 = extract_dates(soup, "Garden waste")

        data = {
            "black_bin_next": black1,
            "black_bin_next2": black2,
            "blue_bin_next": blue1,
            "blue_bin_next2": blue2,
            "garden_bin_next": garden1,
            "garden_bin_next2": garden2
        }

        browser.close()
        return data

@app.route("/bin-dates")
def get_bin_dates():
    uprn = request.args.get("uprn")
    if not uprn:
        return jsonify({"error": "Missing 'uprn' parameter"}), 400
    try:
        data = fetch_bin_dates(uprn, save_html=True)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/debug")
def get_debug():
    if not os.path.exists(DEBUG_FILE):
        return "No debug file available", 404
    return send_file(DEBUG_FILE, mimetype="text/html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

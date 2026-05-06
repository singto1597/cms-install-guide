#!./venv/bin/python3

# Run selenium and chrome driver to scrape data from cloudbytes.dev
import sys
import time
import os
import os.path
import subprocess
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def main():
    login_url = sys.argv[1].split()[0].strip()
    u = sys.argv[2].strip()
    p = sys.argv[3].strip()
    contest_id = sys.argv[4].strip()
    dl_dir = sys.argv[5].strip()
    # print(sys.argv)
    get_csv(login_url, u, p, contest_id, dl_dir)


def get_csv(login_url, u, p, contest_id, dl_dir):
    from glob import glob

    # Setup chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.path.abspath(dl_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    # NEW: Updated headless mode for Chrome 109+
    chrome_options.add_argument("--headless=new")  # Changed from --headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Added for stability
    chrome_options.add_argument("--disable-gpu")  # Added for headless stability

    webdriver_service = Service(ChromeDriverManager().install())

    browser = webdriver.Chrome(
        service=webdriver_service, options=chrome_options)

    # NEW: Added explicit wait
    wait = WebDriverWait(browser, 10)

    try:
        browser.get(login_url)

        # NEW: Wait for elements to be present and use By.NAME
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = browser.find_element(By.NAME, "password")

        username_field.send_keys(u)
        password_field.send_keys(p)

        # NEW: Wait for button to be clickable
        login_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/form/div[3]/button[1]")
        ))
        login_button.click()

        # NEW: Wait a bit for login to complete
        time.sleep(3)

        browser.get(f"{login_url}/contest/{contest_id}/tasks")

        # browser.save_screenshot("debug_error.png")

        # NEW: Wait for table to be present
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "bordered")))

        # Extract headers
        headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]

        # Build in-memory list of dicts
        tasks = []
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # skip header
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                continue
            try:
                score_ = cells[3].text.strip()
            except IndexError:
                score_ = 0

            task_data = {
                "name": cells[1].text.strip(),
                # "title": cells[2].text.strip(),
                "score": score_
            }
            tasks.append(task_data)

        # print(tasks)  # Debug view

        # Get list of files before download
        files_before = set(os.listdir(dl_dir))

        # Trigger download
        browser.get(f"{login_url}/contest/{contest_id}/ranking/csv")

        # Wait for new file to appear and download to complete
        def get_new_files(path, old_files):
            current_files = set(os.listdir(path))
            new_files = current_files - old_files
            # Filter out only .crdownload (partial downloads)
            new_files = {f for f in new_files if not f.endswith('.crdownload')}
            return new_files

        def download_in_progress(path):
            files = os.listdir(path)
            return any(f.endswith('.crdownload') for f in files)

        timeout = 30  # seconds
        start_time = time.time()

        # Wait for download to start and complete
        while time.time() - start_time < timeout:
            if download_in_progress(dl_dir):
                # Download started, wait for it to finish
                while time.time() - start_time < timeout:
                    if not download_in_progress(dl_dir):
                        time.sleep(3)  # Extra wait for file to be written
                        break
                    time.sleep(0.5)
                break

            # Check if file already completed (fast download)
            new_files = get_new_files(dl_dir, files_before)
            if new_files:
                time.sleep(3)
                break

            time.sleep(0.5)

    finally:
        time.sleep(2)
        browser.quit()

    # Find the downloaded file (including .com.google.Chrome.* files)
    new_files = get_new_files(dl_dir, files_before)

    if new_files:
        # Get the most recent file
        downloaded_file = max([os.path.join(dl_dir, f) for f in new_files],
                            key=os.path.getmtime)

        # Rename to proper CSV name
        csv_path = os.path.join(dl_dir, f"ranking.csv")
        # csv_path = os.path.join(dl_dir, f"ranking_{contest_id}.csv")
        os.rename(downloaded_file, csv_path)
        print(f"Renamed {os.path.basename(downloaded_file)} -> {os.path.basename(csv_path)}")

        inject_max_score_row(csv_path, tasks)
        # Print first 10 lines
        print(f"\n=== First 10 lines of {csv_path} ===\n")
        subprocess.run(["/usr/bin/head", "-10", csv_path], check=True)
    else:
        print("No CSV file found for processing.")
        print(f"Files in {dl_dir}: {os.listdir(dl_dir)}")


def inject_max_score_row(csv_path, tasks):
    """
    Adds a row with max scores under the header in the given CSV file.
    Overwrites the same file.
    """
    task_score_map = {t['name']: t['score'] for t in tasks}
    task_score_map.update({'Username': 'Max Possible Score >>'})
    task_score_map.update({'User': 'Max Possible Score'})
    temp_path = csv_path + ".tmp"

    with open(csv_path, newline='', encoding='utf-8') as f_in, open(temp_path, "w", newline='', encoding='utf-8') as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)

        header = next(reader)
        writer.writerow(header)

        max_row = []
        for col in header:
            if col in task_score_map:
                max_row.append(task_score_map[col])
            else:
                max_row.append("")
        writer.writerow(max_row)

        rows = list(reader)  # Read all rows into memory

        # Sort by first column (index 0)
        rows.sort(key=lambda r: r[0])

        for row in rows:
            writer.writerow(row)

    os.replace(temp_path, csv_path)
    print(f"Injected max scores into {csv_path}")


if __name__ == '__main__':
    main()
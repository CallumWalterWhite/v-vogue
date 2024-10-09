from bs4 import BeautifulSoup
from fastapi import HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def search_similar_images_selenium(image_url: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        search_url = f"https://www.google.com/search?tbm=isch&q={image_url}"
        driver.get(search_url)
        time.sleep(3)  # Wait for the page to load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for the images to load
        soup = BeautifulSoup(driver.page_source, "html.parser")
        image_elements = soup.find_all("img")

        similar_images = []
        for img in image_elements:
            src = img.get("src")
            if src and src.startswith("http"):
                similar_images.append(src)
            if len(similar_images) >= 10:
                break

        if not similar_images:
            raise HTTPException(status_code=404, detail="No similar images found.")

        return similar_images

    finally:
        driver.quit()

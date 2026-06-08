from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import os


category = "clocks"
url = f'https://www.flipkart.com/search?q={category}'
headers = {
   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}
excel_file = "flipkartreviews1.xlsx"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')


product_links = soup.find_all('a', class_=['CGtC98', 'wjcEIp'])


results = []


for tag in product_links:
   href = tag.get('href')
   full_link = 'https://www.flipkart.com' + href if href else None
   name = None


   if 'CGtC98' in tag.get('class', []):
       name_tag = tag.find('div', class_='KzDlHZ')
       name = name_tag.text.strip() if name_tag else None
   elif 'wjcEIp' in tag.get('class', []):
       name = tag.get('title')


   if name and full_link:
       results.append({'name': name, 'link': full_link, 'category': category})


for product in results:
   try:
       response = requests.get(product['link'], headers=headers)
       soup = BeautifulSoup(response.text, 'html.parser')


       review_tags = soup.find_all('div', class_='ZmyHeo')


       reviews = []
       for tag in review_tags:
           review_text_div = tag.find('div')
           if review_text_div and review_text_div.text.strip():
               reviews.append(review_text_div.text.strip())


       product['review'] = " | ".join(reviews) if reviews else "No reviews found"


       print(f"Name: {product['name']}")
       print(f"Review: {product['review']}")
       print(f"Link: {product['link']}")
       print(f"Category: {product['category']}\n")


       time.sleep(1)


   except Exception as e:
       product['review'] = "Error"
       print(f"Error fetching review for {product['name']}: {e}")


new_data = pd.DataFrame(results, columns=["name", "review", "category", "link"])


if os.path.exists(excel_file):
   existing_data = pd.read_excel(excel_file)
   combined = pd.concat([existing_data, new_data], ignore_index=True).drop_duplicates(subset=["name", "link"])
else:
   combined = new_data


combined.to_excel(excel_file, index=False)
print(f"Data written to '{excel_file}' successfully.")

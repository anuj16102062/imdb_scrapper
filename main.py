import requests
from bs4 import BeautifulSoup
import csv
import logging

logging.basicConfig(filename='imdb_scraper.log', level=logging.INFO)

def get_movie_details(movie_url):
    response = requests.get(movie_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1').text.strip()
        year = soup.find('span', class_='TitleBlockMetaData__ListItemText-sc-12ein40-2 jedhex').text.strip()
        rating = soup.find('span', itemprop='ratingValue').text.strip()
        directors = [director.text.strip() for director in soup.find_all('a', attrs={'data-testid': 'title-pc-principal-credit'})]
        cast = [actor.text.strip() for actor in soup.find_all('a', attrs={'data-testid': 'title-cast-item__actor'})]
        plot_summary = soup.find('span', itemprop='description').text.strip()
        return {'Title': title, 'Release Year': year, 'IMDb Rating': rating, 'Directors': directors, 'Cast': cast, 'Plot Summary': plot_summary}
    else:
        logging.error(f"Failed to retrieve data from {movie_url}")
        return None

def scrape_imdb_search(keyword):
    base_url = 'https://www.imdb.com'
    if keyword:
        search_url = f'{base_url}/search/title/?genres={keyword}'
    all_movies = []
    response = requests.get("https://www.imdb.com/search/title/?genres=thriller")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        movie_links = soup.find_all('a', class_='result_text')
        for link in movie_links:
            movie_url = f"{base_url}{link['href']}"
            movie_details = get_movie_details(movie_url)
            if movie_details:
                all_movies.append(movie_details)
    else:
        logging.error(f"Failed to retrieve data from {search_url}")

    return all_movies

def save_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    keyword = input("Enter genre to search: ")
    output_file = input("Enter output filename (e.g., data.csv): ")

    try:
        movies_data = scrape_imdb_search(keyword)
        print(f"Scraping completed successfully. Data saved to {output_file}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        print("An error occurred. Please check the log file for details.")

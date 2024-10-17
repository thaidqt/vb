import pytz
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import os

class ScrapeService:

    @staticmethod
    def scrape_matches():
        target_url = 'https://live.thapcam72.net/football'
        response = requests.get(target_url)
        html = response.content

        if html:
            soup = BeautifulSoup(html, 'html.parser')

            # For today
            today_div = soup.select('.tag_content')[1]
            today_matches = []
            tournaments = today_div.select('.tourz')

            for tour in tournaments:
                league_title = tour.select_one('.league_title').get_text()
                matches = tour.select('.match')

                for match in matches:
                    date = match.select_one('.grid-match__date').get_text()
                    href = match['href']
                    id = href.split('-')[-1]  # Get the last part of the href
                    home = match.select_one('.team--home')
                    if home is None:
                        continue
                    home_logo = home.select_one('.team__logo')['data-src']
                    home_name = home.select_one('.team__name').get_text()
                    away = match.select_one('.team--away')
                    if away is None:
                        continue
                    away_logo = away.select_one('.team__logo')['data-src']
                    away_name = away.select_one('.team__name').get_text()
                    video_links = ScrapeService.get_video_links(id)

                    today_matches.append({
                        'video_links': video_links,
                        'date': ScrapeService.format_date(date),
                        'league': league_title.strip(),
                        'home': {
                            'name': home_name,
                            'logo': home_logo
                        },
                        'away': {
                            'name': away_name,
                            'logo': away_logo
                        }
                    })

            # For tomorrow
            tomorrow_div = soup.select('.tag_content')[2]
            tomorrow_matches = []
            tournaments = tomorrow_div.select('.tourz')

            for tour in tournaments:
                league_title = tour.select_one('.league_title').get_text()
                matches = tour.select('.match')

                for match in matches:
                    date = match.select_one('.grid-match__date').get_text()
                    href = match['href']
                    id = href.split('-')[-1]
                    home = match.select_one('.team--home')
                    if home is None:
                        continue
                    home_logo = home.select_one('.team__logo')['data-src']
                    home_name = home.select_one('.team__name').get_text()
                    away = match.select_one('.team--away')
                    if away is None:
                        continue
                    away_logo = away.select_one('.team__logo')['data-src']
                    away_name = away.select_one('.team__name').get_text()
                    video_links = ScrapeService.get_video_links(id)

                    tomorrow_matches.append({
                        'video_links': video_links,
                        'date': ScrapeService.format_date(date),
                        'league': league_title.strip(),
                        'home': {
                            'name': home_name,
                            'logo': home_logo
                        },
                        'away': {
                            'name': away_name,
                            'logo': away_logo
                        }
                    })

            # Merge today and tomorrow matches
            merged_array = today_matches + tomorrow_matches
            json_data = json.dumps(merged_array, indent=4)
            # Define the path to the Laravel storage directory
            storage_path = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'app', 'data', 'scrape.json')

            # Ensure the directory exists
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)

            # Write to the JSON file
            with open(storage_path, 'w') as json_file:
                json_file.write(json_data)

    @staticmethod
    def get_scraped_matches():
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'app', 'data', 'scrape.json')
        with open(path, 'r') as json_file:
            data = json.load(json_file)
        return data if data else []

    @staticmethod
    def get_video_links(id):
        match_data = requests.get(f'https://api.thapcam.xyz/api/match/tc/{id}/no/meta').json()

        if match_data['status'] == 1:
            video_links = match_data['data']['play_urls']
            if video_links is None:
                return []
            referer = 'https://i.fdcdn.xyz/'

            for link in video_links:
                link['referer'] = referer
            return video_links
        return match_data

    @staticmethod
    def format_date(input):
        # Return empty string if input is empty
        if not input.strip():
            return ''

        current_year = datetime.now().year
        formatted_input = f"{input} {current_year}"

        try:
            date_time = datetime.strptime(formatted_input, '%H:%M %d/%m %Y')
            myanmar_timezone = pytz.timezone('Asia/Yangon')
            date_time_myanmar = pytz.utc.localize(date_time).astimezone(myanmar_timezone)

            # Return formatted date in Myanmar Time
            return date_time_myanmar.strftime('%Y-%m-%d %H:%M:%S')
            # return date_time.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            print(f"Error parsing date '{formatted_input}': {e}")
            return ''  # Return an empty string on error


if __name__ == '__main__':
    ScrapeService.scrape_matches()
    matches = ScrapeService.get_scraped_matches()
    print(matches)

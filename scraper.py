import requests
from bs4 import BeautifulSoup

def google_movie_search(query):
    """
    Scrape Google search results for movie download/streaming links.
    Return a list of dicts with title, link, and source.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    search_url = f"https://www.google.com/search?q={query}+movie+download+links"
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    results = []
    for a in soup.select('a'):
        href = a.get('href')
        text = a.get_text()
        if href and "http" in href:
            # naive filter, you want to do better checks here for legit links
            if any(ext in href for ext in ['.mp4', '.mkv', 'torrent', 'stream']):
                results.append({
                    "title": text[:50],
                    "link": href,
                    "source": "Google"
                })
    return results


def torrent_site_search(query):
    """
    Example scraping from a torrent site (e.g., 1337x.to).
    Update selectors if site structure changes.
    """
    url = f"https://1337x.to/search/{query}/1/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    # Note: Make sure this selector matches the actual site layout
    for row in soup.select("table.table-list tr")[1:6]:  # top 5 results
        link_tag = row.select_one("td.coll-1 a")
        if link_tag:
            title = link_tag.text.strip()
            link = "https://1337x.to" + link_tag.get("href")
            results.append({"title": title, "link": link, "source": "1337x"})
    return results


def tmdb_api_search(query, tmdb_api_key):
    """
    Search The Movie DB API for movie info & trailers.
    Requires TMDB API key.
    """
    api_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={query}"
    res = requests.get(api_url)
    if res.status_code != 200:
        return []
    data = res.json()
    results = []
    for movie in data.get("results", [])[:5]:
        title = movie.get("title")
        link = f"https://www.themoviedb.org/movie/{movie.get('id')}"
        results.append({"title": title, "link": link, "source": "TMDB"})
    return results


def aggregate_search(query, tmdb_api_key=None):
    results = []
    results.extend(google_movie_search(query))
    results.extend(torrent_site_search(query))
    if tmdb_api_key:
        results.extend(tmdb_api_search(query, tmdb_api_key))
    # Optional: remove duplicates or sort by relevance here
    return results

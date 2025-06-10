import requests
from bs4 import BeautifulSoup

def google_movie_search(query):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        )
    }
    search_url = f"https://www.google.com/search?q={query}+movie+download+links"
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    results = []
    for a in soup.select('a'):
        href = a.get('href')
        text = a.get_text()
        if href and "http" in href:
            if any(ext in href.lower() for ext in ['.mp4', '.mkv', 'torrent', 'stream']):
                results.append({
                    "title": text[:50] or "Unnamed Link",
                    "link": href,
                    "source": "Google"
                })
    return results

def torrent_site_search(query):
    url = f"https://1337x.to/search/{query}/1/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    for row in soup.select("table.table-list tr")[1:6]:
        link_tag = row.select_one("td.coll-1 a")
        if link_tag:
            title = link_tag.text.strip()
            link = "https://1337x.to" + link_tag.get("href")
            results.append({"title": title, "link": link, "source": "1337x"})
    return results

def tmdb_api_search(query, tmdb_api_key):
    api_url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": tmdb_api_key, "query": query}
    res = requests.get(api_url, params=params)
    if res.status_code != 200:
        return []
    data = res.json()
    results = []
    for movie in data.get("results", [])[:5]:
        title = movie.get("title")
        link = f"https://www.themoviedb.org/movie/{movie.get('id')}"
        results.append({"title": title, "link": link, "source": "TMDB"})
    return results

def youtube_search(query, max_results=3, youtube_api_key=None):
    if not youtube_api_key:
        return []
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query + " trailer",
        "key": youtube_api_key,
        "maxResults": max_results,
        "type": "video"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    items = response.json().get("items", [])
    results = []
    for item in items:
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        results.append({
            "title": snippet["title"],
            "url": f"https://youtu.be/{video_id}",
            "channel": snippet.get("channelTitle", "Unknown"),
            "thumbnail": snippet["thumbnails"]["high"]["url"]
        })
    return results

def aggregate_search(query, tmdb_api_key=None):
    """
    Aggregate movie search from multiple sources:
    - Google (search for direct download/stream links)
    - Torrent site (1337x)
    - TMDB API (official movie database)
    Returns a combined list of dicts with keys: title, link, source
    """
    results = []

    try:
        results.extend(google_movie_search(query))
    except Exception as e:
        print(f"Google search failed: {e}")

    try:
        results.extend(torrent_site_search(query))
    except Exception as e:
        print(f"Torrent search failed: {e}")

    if tmdb_api_key:
        try:
            results.extend(tmdb_api_search(query, tmdb_api_key))
        except Exception as e:
            print(f"TMDB search failed: {e}")

    return results
# scraper.py

def fetch_movie_details(title):
    """
    Dummy movie fetcher - replace this with real scraping or API logic.
    """
    title_lower = title.strip().lower().replace(" ", "-")
    fake_link = f"https://example.com/movies/{title_lower}"
    return {
        "title": title.title(),
        "link": fake_link,
        "trailer": f"https://youtube.com/watch?v=dQw4w9WgXcQ"  # 😏
    }

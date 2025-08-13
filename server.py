import cloudscraper
from flask import Flask, render_template_string, request
from bs4 import BeautifulSoup
import logging
import re

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# HTML template with integrated CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anicute</title>
    <style>
        body {
            font-family: 'Anime Ace', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #1a1a1a;
            color: #ffffff;
        }
        h1 {
            color: #ff6b6b;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        header {
            background: linear-gradient(135deg, #ff6b6b, #ff5252);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        header .logo img {
            height: 50px;
            border-radius: 8px;
        }
        nav {
            display: flex;
            align-items: center;
        }
        nav a {
            color: #ffffff;
            text-decoration: none;
            font-weight: bold;
            margin: 0 10px;
            transition: color 0.3s;
        }
        nav a:hover {
            color: #ffdede;
        }
        .search-bar {
            display: flex;
            align-items: center;
        }
        .search-bar input {
            padding: 8px;
            border-radius: 5px 0 0 5px;
            border: none;
            background-color: rgba(255,255,255,0.1);
            color: #ffffff;
            backdrop-filter: blur(10px);
        }
        .search-bar button {
            padding: 8px 12px;
            border-radius: 0 5px 5px 0;
            border: none;
            background-color: rgba(255,255,255,0.2);
            color: white;
            cursor: pointer;
            transition: background-color 0.2s;
            backdrop-filter: blur(10px);
        }
        .search-bar button:hover {
            background-color: rgba(255,255,255,0.3);
        }
        .hero-image {
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .hero-image img {
            width: 100%;
            height: auto;
            border-radius: 10px;
        }
        .results {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }
        .anime-card {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .anime-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }
        .anime-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-bottom: 3px solid #ff6b6b;
        }
        .anime-info {
            padding: 15px;
        }
        .anime-title {
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 1.1em;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .anime-episode {
            color: #aaaaaa;
            font-size: 0.85em;
            margin-bottom: 8px;
        }
        .anime-genres {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 10px;
        }
        .genre-tag {
            background-color: #ff6b6b;
            color: white;
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 500;
        }
        .watch-btn {
            display: block;
            background-color: #ff6b6b;
            color: white;
            padding: 8px 0;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            text-align: center;
            transition: background-color 0.2s;
            margin-top: 10px;
        }
        .watch-btn:hover {
            background-color: #ff5252;
        }
        .description {
            color: #cccccc;
            font-size: 0.85em;
            margin-bottom: 10px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .loading {
            text-align: center;
            font-size: 1.1em;
            color: #aaaaaa;
            padding: 40px;
        }
        .error {
            text-align: center;
            font-size: 1.1em;
            color: #ff6b6b;
            padding: 40px;
        }
        .pagination {
            text-align: center;
            margin: 20px 0;
        }
        .pagination a {
            color: #ff6b6b;
            text-decoration: none;
            margin: 0 10px;
            font-weight: bold;
        }
        .pagination a:hover {
            color: #ff5252;
        }
        .episode-list {
            margin-top: 20px;
        }
        .episode-list h2 {
            color: #ff6b6b;
        }
        .episode-item {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .episode-item a {
            color: #ff6b6b;
            text-decoration: none;
        }
        .episode-item a:hover {
            color: #ff5252;
        }
        .embed-container {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            max-width: 100%;
            margin-top: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .embed-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        .download-btn, .episode-nav-btn {
            display: inline-block;
            background-color: #6b6bff;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            text-align: center;
            transition: background-color 0.2s;
            margin: 10px 5px;
        }
        .download-btn:hover, .episode-nav-btn:hover {
            background-color: #5252ff;
        }
        footer {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            text-align: center;
            margin-top: 40px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        footer p {
            margin: 5px 0;
            color: #aaaaaa;
            font-size: 0.9em;
        }
        .socials a {
            color: #ff6b6b;
            margin: 0 10px;
            text-decoration: none;
        }
        .socials a:hover {
            color: #ff5252;
        }
        @media (max-width: 768px) {
            header {
                flex-direction: column;
                align-items: flex-start;
            }
            nav {
                flex-direction: column;
                align-items: flex-start;
                margin: 10px 0;
            }
            nav a {
                margin: 5px 0;
            }
            .search-bar {
                width: 100%;
            }
            .search-bar input {
                width: 70%;
            }
            .search-bar button {
                width: 30%;
            }
            .results {
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            }
            .anime-image {
                height: 180px;
            }
            .hero-image img {
                height: 250px;
            }
        }
        @media (max-width: 480px) {
            .results {
                grid-template-columns: 1fr;
            }
            .anime-image {
                height: 160px;
            }
            .hero-image img {
                height: 200px;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <img src="https://i.pinimg.com/736x/83/c3/44/83c344c68b92ac98c4c1451d4d0478e6.jpg" alt="Anicute Logo">
        </div>
        <nav>
            <a href="/">Home</a>
            <a href="/new">New Releases</a>
            <a href="/trending">Trending</a>
        </nav>
        <div class="search-bar">
            <form action="/search" method="GET">
                <input type="text" name="q" placeholder="Search anime..." required>
                <button type="submit">Search</button>
            </form>
        </div>
    </header>

    <h1>{{ page_title }}</h1>

    {% if is_home %}
    <div class="hero-image">
        <img src="https://i.pinimg.com/1200x/44/39/9d/44399dc0ccdb2c2ea605dc7490d0c6f9.jpg" alt="Hero Image">
    </div>
    {% endif %}

    {% if embed_url %}
    <div class="embed-container">
        <iframe src="{{ embed_url }}" frameborder="0" scrolling="no" allowfullscreen></iframe>
    </div>
    {% if video_src %}
    <a href="{{ video_src }}" class="download-btn" download>Download Video</a>
    {% endif %}
    {% if episode_nav %}
    <div>
        {% if episode_nav.prev %}
        <a href="/watch/{{ episode_nav.prev }}" class="episode-nav-btn">Previous Episode</a>
        {% endif %}
        {% if episode_nav.next %}
        <a href="/watch/{{ episode_nav.next }}" class="episode-nav-btn">Next Episode</a>
        {% endif %}
    </div>
    {% endif %}
    {% endif %}

    {% if error %}
    <div class="error">
        {{ error }}
        {% if debug_info %}
        <div style="margin-top: 20px; color: #aaa; font-size: 0.8em;">
            Debug Info: {{ debug_info }}
        </div>
        {% endif %}
    </div>
    {% elif not anime_list %}
    <div class="loading">
        Loading anime...
    </div>
    {% else %}
    <div class="results">
        {% for anime in anime_list %}
        <div class="anime-card">
            <img src="{{ anime.thumbnail_url }}" alt="{{ anime.title }}" class="anime-image" onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
            <div class="anime-info">
                <div class="anime-title">{{ anime.title }}</div>
                <div class="anime-episode">Episode {{ anime.episode }} • {{ anime.year }}</div>
                <div class="anime-genres">
                    {% for genre in anime.genres.split(', ') %}
                    <span class="genre-tag">{{ genre }}</span>
                    {% endfor %}
                </div>
                <div class="description">{{ anime.description }}</div>
                <a href="/watch/{{ anime.link_url }}" class="watch-btn">Watch Episode {{ anime.episode }}</a>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if pagination %}
    <div class="pagination">
        {% if page > 1 %}
        <a href="{{ pagination.prev_url }}">Previous</a>
        {% endif %}
        <span>Page {{ page }}</span>
        {% if pagination.has_next %}
        <a href="{{ pagination.next_url }}">Next</a>
        {% endif %}
    </div>
    {% endif %}

    <footer>
        <p>DMCA Regulation: This website complies with DMCA regulations. If you are a copyright holder and believe your content is used without permission, please contact us.</p>
        <p>We do not own the media and data on this website; it is served by third-party API.</p>
        <div class="socials">
            <a href="https://twitter.com">Twitter</a>
            <a href="https://facebook.com">Facebook</a>
            <a href="https://instagram.com">Instagram</a>
        </div>
    </footer>
</body>
</html>
"""

def fetch_api_data(url):
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        logger.debug(f"Making request to: {url}")
        response = scraper.get(url, timeout=15)
        logger.debug(f"Response status: {response.status_code}")
        
        if response.status_code == 403:
            logger.error("Cloudflare challenge failed")
            return None
        try:
            data = response.json()
            logger.debug(f"Received {len(data) if data else 0} items")
            return data
        except ValueError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Response content: {response.text[:200]}...")
            return None
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None

def get_fallback_data():
    return [
        {
            "title": "One Piece",
            "title_jp": "ワンピース",
            "episode": "1139",
            "year": "1999",
            "genres": "Action, Adventure, Comedy, Fantasy, Shounen, Super Power",
            "link_url": "one-piece-episode-1139",
            "embed_url": "https://2anime.xyz/embed/one-piece-episode-1139",
            "thumbnail_url": "https://cdn.myanimelist.net/images/anime/1244/138851.jpg",
            "description": "Monkey D. Luffy wants to become the King of the Pirates."
        },
        {
            "title": "Demon Slayer",
            "title_jp": "鬼滅の刃",
            "episode": "26",
            "year": "2019",
            "genres": "Action, Demons, Historical, Shounen, Supernatural",
            "link_url": "demon-slayer-episode-26",
            "embed_url": "https://2anime.xyz/embed/demon-slayer-episode-26",
            "thumbnail_url": "https://cdn.myanimelist.net/images/anime/1286/99889.jpg",
            "description": "Tanjiro Kamado fights demons to turn his sister back into a human."
        }
    ]

def extract_video_src(embed_url):
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        response = scraper.get(embed_url, timeout=15)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        video = soup.find('video')
        if video:
            source = video.find('source')
            if source and 'src' in source.attrs:
                return source['src']
        return None
    except Exception as e:
        logger.error(f"Failed to extract video src: {e}")
        return None

def get_episode_navigation(link_url):
    try:
        match = re.match(r"(.+)-episode-(\d+)", link_url)
        if not match:
            return None
        title, episode = match.groups()
        episode_num = int(episode)
        nav = {}
        if episode_num > 1:
            nav['prev'] = f"{title}-episode-{episode_num-1}"
        nav['next'] = f"{title}-episode-{episode_num+1}"
        return nav
    except Exception as e:
        logger.error(f"Failed to generate episode navigation: {e}")
        return None

@app.route('/')
def home():
    anime_list = fetch_api_data("https://animeapi.skin/trending")
    error = None
    debug_info = None
    if anime_list is None:
        error = "Failed to load trending anime. Cloudflare protection may be active."
        debug_info = {
            "solution": "Try again later or use a VPN/proxy",
            "note": "The cloudscraper library may need updates to bypass current Cloudflare challenges"
        }
        anime_list = get_fallback_data()
    return render_template_string(HTML_TEMPLATE, 
                               page_title="Welcome to Anicute",
                               anime_list=anime_list,
                               error=error,
                               debug_info=debug_info,
                               is_home=True)

@app.route('/new')
def new_releases():
    page = request.args.get('page', 1, type=int)
    anime_list = fetch_api_data(f"https://animeapi.skin/new?page={page}")
    error = None
    debug_info = None
    if anime_list is None:
        error = "Failed to load new releases. Cloudflare protection may be active."
        debug_info = {
            "solution": "Try again later or use a VPN/proxy",
            "note": "The cloudscraper library may need updates to bypass current Cloudflare challenges"
        }
        anime_list = get_fallback_data()
    pagination = {
        'prev_url': f'/new?page={page-1}' if page > 1 else None,
        'next_url': f'/new?page={page+1}',
        'has_next': True
    }
    return render_template_string(HTML_TEMPLATE, 
                               page_title="New Anime Releases",
                               anime_list=anime_list,
                               error=error,
                               debug_info=debug_info,
                               pagination=pagination,
                               page=page,
                               is_home=False)

@app.route('/trending')
def trending():
    anime_list = fetch_api_data("https://animeapi.skin/trending")
    error = None
    debug_info = None
    if anime_list is None:
        error = "Failed to load trending anime. Cloudflare protection may be active."
        debug_info = {
            "solution": "Try again later or use a VPN/proxy",
            "note": "The cloudscraper library may need updates to bypass current Cloudflare challenges"
        }
        anime_list = get_fallback_data()
    return render_template_string(HTML_TEMPLATE, 
                               page_title="Trending Anime This Week",
                               anime_list=anime_list,
                               error=error,
                               debug_info=debug_info,
                               is_home=False)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    anime_list = fetch_api_data(f"https://animeapi.skin/search?q={query}&page={page}")
    error = None
    debug_info = None
    if anime_list is None:
        error = f"No results found for '{query}'. Cloudflare protection may be active."
        debug_info = {
            "solution": "Try again later or use a VPN/proxy",
            "note": "The cloudscraper library may need updates to bypass current Cloudflare challenges"
        }
        anime_list = get_fallback_data()
    pagination = {
        'prev_url': f'/search?q={query}&page={page-1}' if page > 1 else None,
        'next_url': f'/search?q={query}&page={page+1}',
        'has_next': True
    }
    return render_template_string(HTML_TEMPLATE, 
                               page_title=f"Search Results for '{query}'",
                               anime_list=anime_list,
                               error=error,
                               debug_info=debug_info,
                               pagination=pagination,
                               page=page,
                               is_home=False)

@app.route('/watch/<path:link_url>')
def watch(link_url):
    embed_url = f"https://2anime.xyz/embed/{link_url}"
    video_src = extract_video_src(embed_url)
    episode_nav = get_episode_navigation(link_url)
    return render_template_string(HTML_TEMPLATE, 
                               page_title="Watch Anime",
                               embed_url=embed_url,
                               video_src=video_src,
                               episode_nav=episode_nav,
                               is_home=False)

if __name__ == '__main__':
    logger.info("Testing API connection with cloudscraper...")
    test_data = fetch_api_data("https://animeapi.skin/trending")
    if test_data:
        logger.info(f"Successfully retrieved {len(test_data)} anime items")
    else:
        logger.warning("Failed to retrieve anime data during startup test")
    app.run(debug=True, host='0.0.0.0', port=5000)

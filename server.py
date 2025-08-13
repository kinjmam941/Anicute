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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Anicute</title>
    <style>
        :root {
            --primary-color: #ff6b6b;
            --secondary-color: #ff5252;
            --bg-color: #1a1a1a;
            --card-bg: rgba(255,255,255,0.1);
            --text-color: #ffffff;
            --text-secondary: #cccccc;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.5;
            padding: 0;
            margin: 0;
            min-height: 100vh;
        }
        
        .container {
            width: 100%;
            max-width: 100%;
            padding: 15px;
            margin: 0 auto;
        }
        
        h1 {
            color: var(--primary-color);
            text-align: center;
            margin: 15px 0;
            font-size: 1.5rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            padding: 12px 15px;
            display: flex;
            flex-direction: column;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
        }
        
        .logo img {
            height: 40px;
            border-radius: 5px;
        }
        
        nav {
            display: none; /* Hidden by default on mobile */
        }
        
        .mobile-menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        .search-bar {
            width: 100%;
            margin-top: 10px;
            display: flex;
        }
        
        .search-bar input {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 5px 0 0 5px;
            background-color: rgba(255,255,255,0.2);
            color: white;
            font-size: 1rem;
        }
        
        .search-bar input::placeholder {
            color: rgba(255,255,255,0.7);
        }
        
        .search-bar button {
            padding: 0 15px;
            border: none;
            border-radius: 0 5px 5px 0;
            background-color: rgba(0,0,0,0.2);
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        
        .hero-image {
            width: 100%;
            margin: 10px 0;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .hero-image img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .results {
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
            margin: 15px 0;
        }
        
        .anime-card {
            background: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 3px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .anime-card:hover {
            transform: translateY(-3px);
        }
        
        .anime-image {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-bottom: 3px solid var(--primary-color);
        }
        
        .anime-info {
            padding: 12px;
        }
        
        .anime-title {
            font-weight: bold;
            font-size: 1rem;
            margin-bottom: 5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .anime-episode {
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-bottom: 8px;
        }
        
        .anime-genres {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 10px;
        }
        
        .genre-tag {
            background-color: var(--primary-color);
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 500;
        }
        
        .description {
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-bottom: 10px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .watch-btn {
            display: block;
            background-color: var(--primary-color);
            color: white;
            padding: 8px 0;
            border-radius: 5px;
            text-align: center;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.9rem;
            transition: background-color 0.2s;
        }
        
        .watch-btn:hover {
            background-color: var(--secondary-color);
        }
        
        .embed-container {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            margin: 15px 0;
            border-radius: 8px;
            overflow: hidden;
            background: #000;
        }
        
        .embed-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }
        
        .player-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
            justify-content: center;
        }
        
        .player-btn {
            padding: 8px 15px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.9rem;
            transition: opacity 0.2s;
            text-align: center;
        }
        
        .download-btn {
            background-color: #6b6bff;
            color: white;
        }
        
        .episode-nav-btn {
            background-color: var(--primary-color);
            color: white;
        }
        
        .episode-selector {
            width: 100%;
            margin: 15px 0;
        }
        
        .episode-selector select {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            background-color: var(--card-bg);
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
        }
        
        .pagination a {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 5px;
            background-color: var(--card-bg);
        }
        
        .loading, .error {
            text-align: center;
            padding: 40px 0;
            font-size: 1.1rem;
        }
        
        .error {
            color: var(--primary-color);
        }
        
        footer {
            background: var(--card-bg);
            padding: 15px;
            text-align: center;
            margin-top: 30px;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }
        
        .socials {
            margin-top: 10px;
            display: flex;
            justify-content: center;
            gap: 15px;
        }
        
        .socials a {
            color: var(--primary-color);
            text-decoration: none;
        }
        
        /* Mobile menu styles */
        .mobile-menu {
            display: none;
            background: rgba(0,0,0,0.9);
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1000;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .mobile-menu.active {
            display: flex;
        }
        
        .mobile-menu a {
            color: white;
            text-decoration: none;
            font-size: 1.2rem;
            margin: 15px 0;
            padding: 10px 20px;
            border-radius: 5px;
            background: rgba(255,255,255,0.1);
        }
        
        .close-menu {
            position: absolute;
            top: 20px;
            right: 20px;
            color: white;
            font-size: 1.5rem;
            background: none;
            border: none;
            cursor: pointer;
        }
        
        /* Tablet and larger screens */
        @media (min-width: 768px) {
            .container {
                max-width: 750px;
                padding: 20px;
            }
            
            .results {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .mobile-menu-btn {
                display: none;
            }
            
            nav {
                display: flex;
                gap: 15px;
            }
            
            nav a {
                color: white;
                text-decoration: none;
                font-weight: 500;
            }
            
            .search-bar {
                width: auto;
                margin-top: 0;
                margin-left: 15px;
            }
            
            .header-top {
                flex-direction: row;
            }
            
            .hero-image img {
                height: 250px;
                object-fit: cover;
            }
        }
        
        /* Desktop screens */
        @media (min-width: 992px) {
            .container {
                max-width: 1000px;
            }
            
            .results {
                grid-template-columns: repeat(3, 1fr);
            }
            
            .anime-image {
                height: 220px;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-top">
            <div class="logo">
                <img src="https://i.pinimg.com/736x/83/c3/44/83c344c68b92ac98c4c1451d4d0478e6.jpg" alt="Anicute Logo">
            </div>
            <button class="mobile-menu-btn">☰</button>
        </div>
        <div class="search-bar">
            <form action="/search" method="GET">
                <input type="text" name="q" placeholder="Search anime..." required>
                <button type="submit">Go</button>
            </form>
        </div>
    </header>
    
    <div class="mobile-menu">
        <button class="close-menu">×</button>
        <a href="/">Home</a>
        <a href="/new">New Releases</a>
        <a href="/trending">Trending</a>
    </div>

    <div class="container">
        <h1>{{ page_title }}</h1>

        {% if is_home %}
        <div class="hero-image">
            <img src="https://i.pinimg.com/1200x/44/39/9d/44399dc0ccdb2c2ea605dc7490d0c6f9.jpg" alt="Hero Image">
        </div>
        {% endif %}

        {% if embed_url %}
        <div class="embed-container">
            <iframe src="{{ embed_url }}" frameborder="0" allowfullscreen></iframe>
        </div>
        
        <div class="player-actions">
            {% if video_src %}
            <a href="{{ video_src }}" class="player-btn download-btn" download>Download</a>
            {% endif %}
            {% if episode_nav %}
                {% if episode_nav.prev %}
                <a href="/watch/{{ episode_nav.prev }}" class="player-btn episode-nav-btn">← Previous</a>
                {% endif %}
                
                {% if current_episode %}
                <div class="episode-selector">
                    <select onchange="location.href='/watch/'+this.value">
                        {% for ep in episode_range %}
                            <option value="{{ title_slug }}-episode-{{ ep }}" {% if ep == current_episode %}selected{% endif %}>
                                Episode {{ ep }}
                            </option>
                        {% endfor %}
                    </select>
                </div>
                {% endif %}
                
                {% if episode_nav.next %}
                <a href="/watch/{{ episode_nav.next }}" class="player-btn episode-nav-btn">Next →</a>
                {% endif %}
            {% endif %}
        </div>
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
                    <a href="/watch/{{ anime.link_url }}" class="watch-btn">Watch Now</a>
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
    </div>

    <footer>
        <p>DMCA Regulation: This website complies with DMCA regulations.</p>
        <p>We do not own the media and data on this website.</p>
        <div class="socials">
            <a href="https://twitter.com">Twitter</a>
            <a href="https://facebook.com">Facebook</a>
            <a href="https://instagram.com">Instagram</a>
        </div>
    </footer>

    <script>
        // Mobile menu toggle
        const menuBtn = document.querySelector('.mobile-menu-btn');
        const closeBtn = document.querySelector('.close-menu');
        const mobileMenu = document.querySelector('.mobile-menu');
        
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.add('active');
        });
        
        closeBtn.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
        });
        
        // Close menu when clicking outside
        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) {
                mobileMenu.classList.remove('active');
            }
        });
        
        // Auto-focus search input on desktop
        if (window.innerWidth > 768) {
            document.querySelector('.search-bar input').focus();
        }
    </script>
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
        
        # Generate episode range (current episode ±5)
        start_ep = max(1, episode_num - 5)
        end_ep = episode_num + 5  # In a real app, you'd want to get the total episodes
        
        episode_range = list(range(start_ep, end_ep + 1))
        
        nav = {
            'prev': f"{title}-episode-{episode_num-1}" if episode_num > 1 else None,
            'next': f"{title}-episode-{episode_num+1}",
            'title_slug': title,
            'current_episode': episode_num,
            'episode_range': episode_range
        }
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
                               title_slug=episode_nav['title_slug'] if episode_nav else None,
                               current_episode=episode_nav['current_episode'] if episode_nav else None,
                               episode_range=episode_nav['episode_range'] if episode_nav else None,
                               is_home=False)

if __name__ == '__main__':
    logger.info("Testing API connection with cloudscraper...")
    test_data = fetch_api_data("https://animeapi.skin/trending")
    if test_data:
        logger.info(f"Successfully retrieved {len(test_data)} anime items")
    else:
        logger.warning("Failed to retrieve anime data during startup test")
    app.run(debug=True, host='0.0.0.0', port=5000)

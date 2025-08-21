import cloudscraper
from flask import Flask, render_template_string, request
from bs4 import BeautifulSoup
import logging
import re
import concurrent.futures
import time
from functools import lru_cache

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# HTML template with premium black and white design (Zara-inspired) + Dark Mode
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Anicute - Watch Anime Online</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-black: #000000;
            --primary-white: #ffffff;
            --light-gray: #f5f5f5;
            --medium-gray: #e5e5e5;
            --dark-gray: #333333;
            --text-gray: #666666;
            --hover-gray: #f0f0f0;
            --border-color: #e0e0e0;
            --shadow-subtle: 0 2px 10px rgba(0,0,0,0.05);
            --shadow-hover: 0 4px 20px rgba(0,0,0,0.1);
            --transition: all 0.3s ease;
        }

        [data-theme="dark"] {
            --primary-black: #ffffff;
            --primary-white: #0a0a0a;
            --light-gray: #1a1a1a;
            --medium-gray: #2a2a2a;
            --dark-gray: #cccccc;
            --text-gray: #999999;
            --hover-gray: #2a2a2a;
            --border-color: #333333;
            --shadow-subtle: 0 2px 10px rgba(255,255,255,0.05);
            --shadow-hover: 0 4px 20px rgba(255,255,255,0.1);
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--primary-white);
            color: var(--primary-black);
            line-height: 1.6;
            min-height: 100vh;
            font-weight: 400;
            transition: var(--transition);
        }
        
        /* Header Styles */
        header {
            background: var(--primary-white);
            border-bottom: 1px solid var(--border-color);
            padding: 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            backdrop-filter: blur(10px);
            transition: var(--transition);
        }
        
        .header-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 30px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: var(--primary-black);
            font-weight: 700;
            font-size: 1.8rem;
            letter-spacing: -0.02em;
            transition: var(--transition);
            order: 1;
        }
        
        .logo:hover {
            opacity: 0.7;
            color: var(--primary-black);
        }
        
        .logo img {
            height: 40px;
            width: 40px;
            border-radius: 50%;
            margin-right: 12px;
            object-fit: cover;
        }
        
        .logo-text {
            font-weight: 700;
            letter-spacing: -0.01em;
        }

        /* Dark Mode Toggle */
        .theme-toggle {
            background: var(--primary-white);
            border: 1px solid var(--border-color);
            color: var(--primary-black);
            padding: 10px 16px;
            cursor: pointer;
            transition: var(--transition);
            font-size: 0.9rem;
            font-weight: 500;
            letter-spacing: 0.02em;
            border-radius: 0;
            order: 2;
        }

        .theme-toggle:hover {
            background: var(--hover-gray);
        }
        
        nav {
            display: none;
            gap: 40px;
            order: 4;
        }
        
        nav a {
            color: var(--primary-black);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            letter-spacing: 0.02em;
            transition: var(--transition);
            position: relative;
            padding: 8px 0;
        }
        
        nav a::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 0;
            height: 1px;
            background: var(--primary-black);
            transition: width 0.3s ease;
        }
        
        nav a:hover::after {
            width: 100%;
        }
        
        nav a:hover {
            color: var(--primary-black);
        }
        
        .mobile-menu-btn {
            background: none;
            border: none;
            color: var(--primary-black);
            font-size: 1.2rem;
            font-weight: 500;
            padding: 10px 0;
            cursor: pointer;
            transition: var(--transition);
            order: 3;
            letter-spacing: 0.05em;
        }
        
        .mobile-menu-btn:hover {
            opacity: 0.7;
        }
        
        .search-container {
            position: relative;
            width: 100%;
            order: 5;
        }
        
        .search-bar {
            display: flex;
            background: var(--primary-white);
            border: 1px solid var(--border-color);
            overflow: hidden;
            transition: var(--transition);
        }
        
        .search-bar:focus-within {
            border-color: var(--primary-black);
            box-shadow: var(--shadow-subtle);
        }
        
        .search-bar input {
            flex: 1;
            padding: 16px 20px;
            border: none;
            background: transparent;
            color: var(--primary-black);
            font-size: 0.95rem;
            font-weight: 400;
            outline: none;
            font-family: inherit;
            transition: var(--transition);
        }
        
        .search-bar input::placeholder {
            color: var(--text-gray);
            font-weight: 400;
        }
        
        .search-bar button {
            padding: 16px 24px;
            border: none;
            border-left: 1px solid var(--border-color);
            background: var(--primary-black);
            color: var(--primary-white);
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
            font-size: 0.9rem;
            letter-spacing: 0.02em;
            font-family: inherit;
        }
        
        .search-bar button:hover {
            background: var(--dark-gray);
        }
        
        /* Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 30px;
        }

        /* Netflix-style Trending Slider */
        .trending-section {
            margin: 60px 0;
        }

        .section-title {
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 30px;
            color: var(--primary-black);
            letter-spacing: -0.01em;
        }

        .slider-container {
            position: relative;
            overflow: hidden;
            margin: 0 -30px;
            padding: 0 30px;
        }

        .slider-wrapper {
            display: flex;
            transition: transform 0.5s ease;
            gap: 20px;
        }

        .slider-item {
            min-width: 280px;
            flex-shrink: 0;
            background: var(--primary-white);
            border: 1px solid var(--border-color);
            overflow: hidden;
            transition: var(--transition);
            position: relative;
        }

        .slider-item:hover {
            transform: scale(1.05);
            box-shadow: var(--shadow-hover);
            z-index: 2;
        }

        .slider-item img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            transition: var(--transition);
        }

        .slider-item:hover img {
            opacity: 0.9;
        }

        .slider-info {
            padding: 20px;
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(transparent, rgba(0,0,0,0.8));
            color: white;
            transform: translateY(100%);
            transition: var(--transition);
        }

        .slider-item:hover .slider-info {
            transform: translateY(0);
        }

        [data-theme="dark"] .slider-info {
            background: linear-gradient(transparent, rgba(255,255,255,0.9));
            color: var(--primary-black);
        }

        .slider-title {
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 8px;
            line-height: 1.2;
        }

        .slider-episode {
            font-size: 0.8rem;
            opacity: 0.9;
            margin-bottom: 8px;
        }

        .slider-genres {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-bottom: 12px;
        }

        .slider-genre {
            background: rgba(255,255,255,0.2);
            padding: 2px 6px;
            font-size: 0.7rem;
            border: 1px solid rgba(255,255,255,0.3);
        }

        [data-theme="dark"] .slider-genre {
            background: rgba(0,0,0,0.2);
            border-color: rgba(0,0,0,0.3);
        }

        .slider-watch-btn {
            display: inline-block;
            background: var(--primary-black);
            color: var(--primary-white);
            padding: 8px 16px;
            text-decoration: none;
            font-size: 0.8rem;
            font-weight: 500;
            transition: var(--transition);
        }

        .slider-watch-btn:hover {
            background: var(--dark-gray);
            color: var(--primary-white);
        }

        .slider-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: var(--primary-black);
            color: var(--primary-white);
            border: none;
            padding: 15px 20px;
            cursor: pointer;
            font-size: 1.2rem;
            transition: var(--transition);
            z-index: 3;
        }

        .slider-nav:hover {
            background: var(--dark-gray);
        }

        .slider-nav.prev {
            left: 0;
        }

        .slider-nav.next {
            right: 0;
        }

        /* Latest Episodes Section */
        .latest-episodes-section {
            margin: 60px 0;
        }

        .latest-episodes-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .view-more-btn {
            background: var(--primary-black);
            color: var(--primary-white);
            padding: 12px 24px;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
            transition: var(--transition);
            letter-spacing: 0.02em;
            border: 1px solid var(--primary-black);
        }

        .view-more-btn:hover {
            background: var(--dark-gray);
            color: var(--primary-white);
        }
        
        /* Page Title */
        .page-title {
            color: var(--primary-black);
            text-align: center;
            margin: 0 0 60px 0;
            font-size: 2.5rem;
            font-weight: 300;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }
        
        /* Episode Info Section */
        .episode-info-card {
            background: var(--primary-white);
            border: 1px solid var(--border-color);
            padding: 40px;
            margin: 40px 0;
            box-shadow: var(--shadow-subtle);
            transition: var(--transition);
        }
        
        .anime-details {
            display: flex;
            flex-direction: column;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .anime-title-section {
            text-align: center;
            padding: 30px;
            background: var(--light-gray);
            border: 1px solid var(--border-color);
            transition: var(--transition);
        }
        
        .anime-title-main {
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--primary-black);
            letter-spacing: -0.01em;
        }
        
        .current-episode {
            font-size: 1rem;
            font-weight: 400;
            color: var(--text-gray);
            letter-spacing: 0.02em;
        }
        
        .episode-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        
        .stat-item {
            background: var(--primary-white);
            padding: 30px;
            text-align: center;
            border: 1px solid var(--border-color);
            transition: var(--transition);
        }
        
        .stat-item:hover {
            box-shadow: var(--shadow-hover);
            transform: translateY(-2px);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 600;
            color: var(--primary-black);
            margin-bottom: 8px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: var(--text-gray);
            font-weight: 400;
            letter-spacing: 0.02em;
        }
        
        .discovery-status {
            text-align: center;
            padding: 20px;
            margin: 30px 0;
            font-weight: 500;
            border: 1px solid var(--border-color);
            background: var(--light-gray);
            color: var(--primary-black);
            transition: var(--transition);
        }
        
        .discovery-loading {
            background: var(--hover-gray);
        }
        
        .discovery-complete {
            background: var(--light-gray);
        }
        
        .discovery-error {
            background: var(--medium-gray);
        }
        
        .episode-message {
            text-align: center;
            color: var(--text-gray);
            font-size: 0.9rem;
            margin: 20px 0;
            padding: 20px;
            background: var(--light-gray);
            border: 1px solid var(--border-color);
            font-weight: 400;
            line-height: 1.6;
            transition: var(--transition);
        }
        
        /* Video Player */
        .video-section {
            margin: 50px 0;
        }
        
        .embed-container {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            background: var(--primary-black);
            margin-bottom: 40px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-subtle);
        }
        
        .embed-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }
        
        /* Episode Controls */
        .episode-controls {
            background: var(--primary-white);
            border: 1px solid var(--border-color);
            padding: 40px;
            margin: 40px 0;
            box-shadow: var(--shadow-subtle);
            transition: var(--transition);
        }
        
        .episode-input-section {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .episode-input-container {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .episode-input {
            flex: 1;
            padding: 16px 20px;
            background: var(--primary-white);
            border: 1px solid var(--border-color);
            color: var(--primary-black);
            font-size: 0.95rem;
            font-weight: 400;
            outline: none;
            transition: var(--transition);
            font-family: inherit;
        }
        
        .episode-input:focus {
            border-color: var(--primary-black);
            box-shadow: var(--shadow-subtle);
        }
        
        .episode-input::placeholder {
            color: var(--text-gray);
            font-weight: 400;
        }
        
        .load-episode-btn, .discover-btn {
            padding: 16px 24px;
            background: var(--primary-black);
            border: 1px solid var(--primary-black);
            color: var(--primary-white);
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
            white-space: nowrap;
            font-size: 0.9rem;
            letter-spacing: 0.02em;
            font-family: inherit;
        }
        
        .discover-btn {
            background: var(--primary-white);
            color: var(--primary-black);
            border: 1px solid var(--border-color);
            display: none;
        }
        
        .load-episode-btn:hover {
            background: var(--dark-gray);
        }
        
        .discover-btn:hover {
            background: var(--light-gray);
        }
        
        .episode-navigation {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .nav-btn {
            padding: 16px 24px;
            border: 1px solid var(--border-color);
            font-weight: 500;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: var(--transition);
            font-size: 0.9rem;
            letter-spacing: 0.02em;
            background: var(--primary-white);
            color: var(--primary-black);
        }
        
        .prev-btn, .next-btn {
            background: var(--primary-black);
            color: var(--primary-white);
            border-color: var(--primary-black);
        }
        
        .prev-btn:hover, .next-btn:hover {
            background: var(--dark-gray);
            color: var(--primary-white);
        }
        
        .download-btn:hover {
            background: var(--light-gray);
            color: var(--primary-black);
        }
        
        /* Episode Grid */
        .episode-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
            gap: 10px;
            margin: 40px 0;
            padding: 30px;
            background: var(--light-gray);
            border: 1px solid var(--border-color);
            max-height: 400px;
            overflow-y: auto;
            transition: var(--transition);
        }
        
        .episode-item {
            padding: 12px;
            text-align: center;
            text-decoration: none;
            color: var(--primary-black);
            border: 1px solid var(--border-color);
            transition: var(--transition);
            font-size: 0.9rem;
            font-weight: 500;
            background: var(--primary-white);
        }
        
        .episode-item.available:hover {
            background: var(--primary-black);
            color: var(--primary-white);
        }
        
        .episode-item.current {
            background: var(--primary-black);
            color: var(--primary-white);
        }
        
        .episode-item.unavailable {
            background: var(--hover-gray);
            color: var(--text-gray);
            cursor: not-allowed;
            border-color: var(--medium-gray);
        }
        
        /* Mobile Menu */
        .mobile-menu {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--primary-white);
            border: 1px solid var(--border-color);
            border-top: none;
            box-shadow: var(--shadow-hover);
            z-index: 999;
            transition: var(--transition);
        }
        
        .mobile-menu.active {
            display: block;
        }
        
        .mobile-menu a {
            display: block;
            color: var(--primary-black);
            text-decoration: none;
            padding: 20px 30px;
            font-weight: 500;
            border-bottom: 1px solid var(--border-color);
            transition: var(--transition);
        }
        
        .mobile-menu a:hover {
            background: var(--light-gray);
        }
        
        .mobile-menu a:last-child {
            border-bottom: none;
        }
        
        /* Anime Grid */
        .anime-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 30px;
            margin: 60px 0;
        }
        
        .anime-card {
            background: var(--primary-white);
            border: 1px solid var(--border-color);
            overflow: hidden;
            transition: var(--transition);
            position: relative;
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .anime-card:hover {
            box-shadow: var(--shadow-hover);
            transform: translateY(-4px);
        }
        
        .anime-image {
            width: 100%;
            height: 220px;
            object-fit: cover;
            object-position: center;
            transition: var(--transition);
            flex-shrink: 0;
        }
        
        .anime-card:hover .anime-image {
            opacity: 0.9;
        }
        
        .anime-info {
            padding: 25px;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }
        
        .anime-title {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 12px;
            color: var(--primary-black);
            line-height: 1.3;
            height: 2.6em;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            letter-spacing: -0.01em;
        }
        
        .anime-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-size: 0.85rem;
            color: var(--text-gray);
            font-weight: 500;
        }
        
        .episode-info {
            background: var(--primary-black);
            color: var(--primary-white);
            padding: 4px 10px;
            font-weight: 500;
            font-size: 0.75rem;
            letter-spacing: 0.02em;
        }
        
        .anime-genres {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 15px;
        }
        
        .genre-tag {
            background: var(--light-gray);
            color: var(--text-gray);
            padding: 4px 8px;
            font-size: 0.7rem;
            font-weight: 500;
            border: 1px solid var(--border-color);
            letter-spacing: 0.02em;
            transition: var(--transition);
        }
        
        .anime-description {
            color: var(--text-gray);
            font-size: 0.9rem;
            margin-bottom: auto;
            height: 4.5em;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.5;
            font-weight: 400;
        }
        
        .watch-btn {
            display: block;
            background: var(--primary-black);
            color: var(--primary-white);
            padding: 16px 0;
            text-align: center;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
            transition: var(--transition);
            letter-spacing: 0.02em;
            margin-top: 20px;
            flex-shrink: 0;
        }
        
        .watch-btn:hover {
            background: var(--dark-gray);
            color: var(--primary-white);
        }
        
        /* Loading Spinner */
        .loading-spinner {
            border: 2px solid var(--border-color);
            border-top: 2px solid var(--primary-black);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Error and loading styles */
        .loading {
            text-align: center;
            font-size: 1.2rem;
            font-weight: 400;
            color: var(--text-gray);
            padding: 60px;
            background: var(--light-gray);
            border: 1px solid var(--border-color);
            transition: var(--transition);
        }
        
        .error {
            text-align: center;
            font-size: 1.2rem;
            font-weight: 500;
            color: var(--primary-black);
            padding: 60px;
            background: var(--light-gray);
            border: 1px solid var(--border-color);
            margin: 40px 0;
            line-height: 1.6;
            transition: var(--transition);
        }
        
        /* Pagination */
        .pagination {
            text-align: center;
            margin: 60px 0;
        }
        
        .pagination a {
            color: var(--primary-black);
            text-decoration: none;
            margin: 0 15px;
            font-weight: 500;
            padding: 12px 24px;
            background: var(--primary-white);
            border: 1px solid var(--border-color);
            transition: var(--transition);
            display: inline-block;
            letter-spacing: 0.02em;
        }
        
        .pagination a:hover {
            background: var(--primary-black);
            color: var(--primary-white);
        }
        
        /* Footer Styles */
        footer {
            background: var(--light-gray);
            color: var(--primary-black);
            padding: 50px 30px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            font-size: 0.85rem;
            font-weight: 400;
            margin-top: 60px;
            line-height: 1.6;
            transition: var(--transition);
        }
        
        footer p {
            margin: 15px 0;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        
        footer a {
            color: var(--primary-black);
            text-decoration: underline;
            font-weight: 500;
        }
        
        footer a:hover {
            opacity: 0.7;
        }
        
        /* Responsive Design */
        @media (min-width: 480px) {
            .anime-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 30px;
            }
            
            .anime-image {
                height: 240px;
            }

            .slider-item {
                min-width: 250px;
            }
        }
        
        @media (min-width: 768px) {
            .header-container {
                flex-wrap: nowrap;
                gap: 40px;
            }
            
            .search-container {
                flex-grow: 1;
                order: 4;
                width: auto;
                max-width: 500px;
            }
            
            .mobile-menu-btn {
                display: none;
            }
            
            nav {
                display: flex;
                order: 3;
            }

            .theme-toggle {
                order: 2;
            }
            
            .anime-grid {
                grid-template-columns: repeat(3, 1fr);
                gap: 30px;
            }
            
            .anime-image {
                height: 280px;
            }
            
            .anime-info {
                padding: 30px;
            }
            
            .episode-input-section {
                flex-direction: row;
                align-items: center;
            }
            
            .episode-input-container {
                flex: 1;
                max-width: 400px;
            }
            
            .anime-details {
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            }
            
            .episode-grid {
                grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
                gap: 8px;
            }

            .slider-item {
                min-width: 280px;
            }
        }
        
        @media (min-width: 1024px) {
            .anime-grid {
                grid-template-columns: repeat(4, 1fr);
            }
            
            .anime-image {
                height: 300px;
            }
            
            .episode-stats {
                grid-template-columns: repeat(4, 1fr);
            }

            .slider-item {
                min-width: 320px;
            }
        }
        
        @media (min-width: 1200px) {
            .anime-grid {
                grid-template-columns: repeat(5, 1fr);
            }

            .slider-item {
                min-width: 350px;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-container">
            <a href="/" class="logo">
                <img src="https://i.pinimg.com/736x/83/c3/44/83c344c68b92ac98c4c1451d4d0478e6.jpg" alt="Anicute Logo">
                <span class="logo-text">ANICUTE</span>
            </a>

            <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle dark mode">
                <span id="themeToggleText">🌙 DARK</span>
            </button>
            
            <div class="search-container">
                <form class="search-bar" action="/search" method="GET">
                    <input type="text" name="q" placeholder="Search anime..." required>
                    <button type="submit" aria-label="Search">SEARCH</button>
                </form>
            </div>
            
            <nav>
                <a href="/">Home</a>
                <a href="/new">Latest</a>
                <a href="/trending">Trending</a>
            </nav>
            
            <button class="mobile-menu-btn" aria-label="Open menu" onclick="toggleMobileMenu()">MENU</button>
            
            <!-- Mobile Menu -->
            <div class="mobile-menu" id="mobileMenu">
                <a href="/">Home</a>
                <a href="/new">Latest Episodes</a>
                <a href="/trending">Trending</a>
            </div>
        </div>
    </header>

    <div class="container">
        {% if is_home %}
        <h1 class="page-title">{{ page_title }}</h1>

        <!-- Netflix-style Trending Slider -->
        {% if trending_anime %}
        <div class="trending-section">
            <h2 class="section-title">🔥 Trending This Week</h2>
            <div class="slider-container" id="trendingSlider">
                <button class="slider-nav prev" onclick="slideLeft('trendingSlider')">‹</button>
                <div class="slider-wrapper" id="trendingWrapper">
                    {% for anime in trending_anime %}
                    <div class="slider-item">
                        <img src="{{ anime.thumbnail_url }}" alt="{{ anime.title }}" 
                             onerror="this.src='https://via.placeholder.com/350x200/f5f5f5/666666?text=NO+IMAGE'">
                        <div class="slider-info">
                            <div class="slider-title">{{ anime.title }}</div>
                            <div class="slider-episode">Episode {{ anime.episode }}</div>
                            <div class="slider-genres">
                                {% for genre in anime.genres.split(', ')[:3] %}
                                <span class="slider-genre">{{ genre }}</span>
                                {% endfor %}
                            </div>
                            <a href="/watch/{{ anime.link_url }}" class="slider-watch-btn">Watch Now</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                <button class="slider-nav next" onclick="slideRight('trendingSlider')">›</button>
            </div>
        </div>
        {% endif %}

        <!-- Latest Episodes Section -->
        {% if latest_episodes %}
        <div class="latest-episodes-section">
            <div class="latest-episodes-header">
                <h2 class="section-title">📺 Latest Episodes</h2>
                <a href="/new" class="view-more-btn">View More Recent Episodes</a>
            </div>
            <div class="anime-grid">
                {% for anime in latest_episodes %}
                <div class="anime-card">
                    <img src="{{ anime.thumbnail_url }}" alt="{{ anime.title }}" class="anime-image" 
                         onerror="this.src='https://via.placeholder.com/400x300/f5f5f5/666666?text=NO+IMAGE'">
                    <div class="anime-info">
                        <div class="anime-title">{{ anime.title }}</div>
                        <div class="anime-meta">
                            <div class="episode-info">EP {{ anime.episode }}</div>
                            <div>{{ anime.year }}</div>
                        </div>
                        <div class="anime-genres">
                            {% for genre in anime.genres.split(', ')[:3] %}
                            <span class="genre-tag">{{ genre }}</span>
                            {% endfor %}
                        </div>
                        <div class="anime-description">{{ anime.description }}</div>
                        <a href="/watch/{{ anime.link_url }}" class="watch-btn">Watch Now</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% else %}
        <h1 class="page-title">{{ page_title }}</h1>

        {% if embed_url %}
        <!-- Episode Information Card -->
        <div class="episode-info-card">
            <div class="anime-details">
                <div class="anime-title-section">
                    <div class="anime-title-main">{{ anime_title }}</div>
                    <div class="current-episode">Episode {{ current_episode }}</div>
                </div>
            </div>
            
            {% if episode_discovery %}
            <div class="episode-stats">
                <div class="stat-item">
                    <div class="stat-value">{{ episode_discovery.time_taken }}s</div>
                    <div class="stat-label">Discovery Time</div>
                </div>
            </div>
            
            <div class="discovery-status discovery-complete">
                Episode discovery completed! Found {{ episode_discovery.available_episodes }} available episodes.
            </div>
            
            <!-- Episode Grid -->
            <div class="episode-grid" id="episodeGrid">
                {% for ep_num in range(1, episode_discovery.total_episodes + 1) %}
                <a href="/watch/{{ title_slug }}-episode-{{ ep_num }}" 
                   class="episode-item {{ 'current' if ep_num == current_episode else ('available' if ep_num in episode_discovery.available_list else 'unavailable') }}"
                   {% if ep_num not in episode_discovery.available_list and ep_num != current_episode %}onclick="return false;"{% endif %}>
                    {{ ep_num }}
                </a>
                {% endfor %}
            </div>
            {% endif %}
        </div>

        <!-- Video Player -->
        <div class="video-section">
            <div class="embed-container">
                <iframe src="{{ embed_url }}" frameborder="0" allowfullscreen></iframe>
            </div>
            
            <div class="episode-controls">
                <div class="episode-input-section">
                    <div class="episode-input-container">
                        <input 
                            type="number" 
                            id="episodeNumber" 
                            class="episode-input" 
                            placeholder="Enter episode number..."
                            min="1"
                            max="{{ episode_discovery.total_episodes if episode_discovery else 2000 }}"
                            value="{{ current_episode }}"
                        >
                        <button class="load-episode-btn" onclick="loadEpisode()">Load Episode</button>
                    </div>
                    <button class="discover-btn" onclick="discoverEpisodes()">Discover All Episodes</button>
                </div>
                
                <div class="episode-message">
                    Sometimes episode counts are not loaded properly. Try entering the latest episode number.
                </div>
                
                <div class="episode-navigation">
                    {% if video_src %}
                    <a href="{{ video_src }}" class="nav-btn download-btn" download>Download</a>
                    {% endif %}
                    
                    {% if episode_nav %}
                        {% if episode_nav.prev %}
                        <a href="/watch/{{ episode_nav.prev }}" class="nav-btn prev-btn">← Previous</a>
                        {% endif %}
                        
                        {% if episode_nav.next %}
                        <a href="/watch/{{ episode_nav.next }}" class="nav-btn next-btn">Next →</a>
                        {% endif %}
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Discovery Status (for AJAX updates) -->
        <div id="discoveryStatus" style="display: none;"></div>
        {% endif %}

        {% if error %}
        <div class="error">
            <h3>{{ error }}</h3>
            {% if debug_info %}
            <div style="margin-top: 20px; color: var(--text-gray); font-size: 0.9rem;">
                Debug Info: {{ debug_info }}
            </div>
            {% endif %}
        </div>
        {% elif not anime_list and not embed_url and not is_home %}
        <div class="loading">
            <div class="loading-spinner"></div>
            Loading anime...
        </div>
        {% endif %}
        
        {% if anime_list %}
        <div class="anime-grid">
            {% for anime in anime_list %}
            <div class="anime-card">
                <img src="{{ anime.thumbnail_url }}" alt="{{ anime.title }}" class="anime-image" 
                     onerror="this.src='https://via.placeholder.com/400x300/f5f5f5/666666?text=NO+IMAGE'">
                <div class="anime-info">
                    <div class="anime-title">{{ anime.title }}</div>
                    <div class="anime-meta">
                        <div class="episode-info">EP {{ anime.episode }}</div>
                        <div>{{ anime.year }}</div>
                    </div>
                    <div class="anime-genres">
                        {% for genre in anime.genres.split(', ')[:3] %}
                        <span class="genre-tag">{{ genre }}</span>
                        {% endfor %}
                    </div>
                    <div class="anime-description">{{ anime.description }}</div>
                    <a href="/watch/{{ anime.link_url }}" class="watch-btn">Watch Now</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if pagination %}
        <div class="pagination">
            {% if pagination.prev_url %}
            <a href="{{ pagination.prev_url }}">← Previous</a>
            {% endif %}
            <span style="font-weight: 500; color: var(--primary-black); margin: 0 20px;">Page {{ page }}</span>
            {% if pagination.has_next %}
            <a href="{{ pagination.next_url }}">Next →</a>
            {% endif %}
        </div>
        {% endif %}
        {% endif %}
    </div>

    <footer>
        <p>&copy; 2025 Anicute. All rights reserved.</p>
        <p>DMCA Compliance: We respect the intellectual property rights of others. All media content on this site is served by third-party providers, and we do not claim ownership of any media displayed. Anicute acts solely as a platform to aggregate and serve this content.</p>
        <p>For DMCA complaints or content removal requests, please contact us at <a href="mailto:02qttt@gmail.com">02qttt@gmail.com</a>.</p>
    </footer>

    <script>
        // Dark Mode Toggle
        function toggleTheme() {
            const body = document.body;
            const themeToggleText = document.getElementById('themeToggleText');
            
            if (body.getAttribute('data-theme') === 'dark') {
                body.removeAttribute('data-theme');
                themeToggleText.textContent = '🌙 DARK';
                localStorage.setItem('theme', 'light');
            } else {
                body.setAttribute('data-theme', 'dark');
                themeToggleText.textContent = '☀️ LIGHT';
                localStorage.setItem('theme', 'dark');
            }
        }

        // Load saved theme on page load
        document.addEventListener('DOMContentLoaded', function() {
            const savedTheme = localStorage.getItem('theme');
            const themeToggleText = document.getElementById('themeToggleText');
            
            if (savedTheme === 'dark') {
                document.body.setAttribute('data-theme', 'dark');
                themeToggleText.textContent = '☀️ LIGHT';
            } else {
                themeToggleText.textContent = '🌙 DARK';
            }
        });

        // Netflix-style Slider functionality
        function slideLeft(sliderId) {
            const slider = document.getElementById(sliderId);
            const wrapper = slider.querySelector('.slider-wrapper');
            const itemWidth = wrapper.querySelector('.slider-item').offsetWidth + 20; // including gap
            const currentTransform = getTranslateX(wrapper);
            
            wrapper.style.transform = `translateX(${Math.min(currentTransform + itemWidth * 3, 0)}px)`;
        }

        function slideRight(sliderId) {
            const slider = document.getElementById(sliderId);
            const wrapper = slider.querySelector('.slider-wrapper');
            const itemWidth = wrapper.querySelector('.slider-item').offsetWidth + 20; // including gap
            const maxScroll = -(wrapper.scrollWidth - slider.offsetWidth);
            const currentTransform = getTranslateX(wrapper);
            
            wrapper.style.transform = `translateX(${Math.max(currentTransform - itemWidth * 3, maxScroll)}px)`;
        }

        function getTranslateX(element) {
            const style = window.getComputedStyle(element);
            const matrix = new DOMMatrix(style.transform);
            return matrix.m41;
        }

        function toggleMobileMenu() {
            const mobileMenu = document.getElementById('mobileMenu');
            const menuBtn = document.querySelector('.mobile-menu-btn');
            
            mobileMenu.classList.toggle('active');
            
            if (mobileMenu.classList.contains('active')) {
                menuBtn.textContent = 'CLOSE';
            } else {
                menuBtn.textContent = 'MENU';
            }
        }
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            const mobileMenu = document.getElementById('mobileMenu');
            const menuBtn = document.querySelector('.mobile-menu-btn');
            
            if (!menuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.remove('active');
                menuBtn.textContent = 'MENU';
            }
        });
        
        function loadEpisode() {
            const episodeNumber = document.getElementById('episodeNumber').value;
            if (!episodeNumber) {
                alert('Please enter an episode number!');
                return;
            }
            
            const currentPath = window.location.pathname;
            const pathParts = currentPath.split('/');
            
            if (pathParts[1] === 'watch' && pathParts[2]) {
                const currentEpisodeUrl = pathParts[2];
                const titleMatch = currentEpisodeUrl.match(/^(.+)-episode-\d+$/);
                
                if (titleMatch) {
                    const animeTitle = titleMatch[1];
                    const newEpisodeUrl = `${animeTitle}-episode-${episodeNumber}`;
                    window.location.href = `/watch/${newEpisodeUrl}`;
                } else {
                    alert('Could not determine anime title from current URL!');
                }
            } else {
                alert('Please navigate to an anime episode page first!');
            }
        }
        
        function discoverEpisodes() {
            const currentPath = window.location.pathname;
            const pathParts = currentPath.split('/');
            
            if (pathParts[1] === 'watch' && pathParts[2]) {
                const currentEpisodeUrl = pathParts[2];
                const titleMatch = currentEpisodeUrl.match(/^(.+)-episode-\d+$/);
                
                if (titleMatch) {
                    const animeTitle = titleMatch[1];
                    
                    // Show loading status
                    const statusDiv = document.getElementById('discoveryStatus');
                    statusDiv.style.display = 'block';
                    statusDiv.innerHTML = `
                        <div class="discovery-status discovery-loading">
                            <div class="loading-spinner"></div>
                            Discovering episodes for ${animeTitle.replace(/-/g, ' ')}... This may take a few minutes.
                        </div>
                    `;
                    
                    window.location.href = `/discover/${currentEpisodeUrl}`;
                } else {
                    alert('Could not determine anime title from current URL!');
                }
            } else {
                alert('Please navigate to an anime episode page first!');
            }
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (document.querySelector('.embed-container')) {
                if (e.key === 'ArrowLeft') {
                    const prevBtn = document.querySelector('.prev-btn');
                    if (prevBtn) prevBtn.click();
                } else if (e.key === 'ArrowRight') {
                    const nextBtn = document.querySelector('.next-btn');
                    if (nextBtn) nextBtn.click();
                } else if (e.key === 'Enter' && e.target.id === 'episodeNumber') {
                    loadEpisode();
                }
            }
            
            // Dark mode toggle with 'D' key
            if (e.key === 'd' || e.key === 'D') {
                if (!e.target.matches('input, textarea')) {
                    toggleTheme();
                }
            }
        });
        
        // Smooth scrolling for better UX
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });

        // Touch support for slider
        let startX, currentX;
        let sliderContainer = null;

        document.querySelectorAll('.slider-container').forEach(slider => {
            slider.addEventListener('touchstart', handleTouchStart, {passive: true});
            slider.addEventListener('touchmove', handleTouchMove, {passive: true});
            slider.addEventListener('touchend', handleTouchEnd, {passive: true});
        });

        function handleTouchStart(e) {
            startX = e.touches[0].clientX;
            sliderContainer = e.currentTarget;
        }

        function handleTouchMove(e) {
            if (!startX) return;
            currentX = e.touches[0].clientX;
        }

        function handleTouchEnd(e) {
            if (!startX || !currentX) return;

            const diffX = startX - currentX;
            const threshold = 50;

            if (Math.abs(diffX) > threshold) {
                if (diffX > 0) {
                    // Swipe left - slide right
                    slideRight(sliderContainer.id);
                } else {
                    // Swipe right - slide left
                    slideLeft(sliderContainer.id);
                }
            }

            startX = null;
            currentX = null;
            sliderContainer = null;
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
            "description": "Monkey D. Luffy wants to become the King of the Pirates. Follow his adventures as he explores the Grand Line with his diverse crew of Straw Hat Pirates."
        },
        {
            "title": "Demon Slayer: Kimetsu no Yaiba",
            "title_jp": "鬼滅の刃",
            "episode": "44",
            "year": "2019",
            "genres": "Action, Demons, Historical, Shounen, Supernatural",
            "link_url": "demon-slayer-episode-44",
            "embed_url": "https://2anime.xyz/embed/demon-slayer-episode-44",
            "thumbnail_url": "https://cdn.myanimelist.net/images/anime/1286/99889.jpg",
            "description": "Tanjiro Kamado fights demons to turn his sister Nezuko back into a human after their family was attacked by demons."
        }
    ]

def get_latest_episode(title_slug):
    query = title_slug.replace('-', '+')
    data = fetch_api_data(f"https://animeapi.skin/search?q={query}")
    if not data:
        return None
    for anime in data:
        slug_base = anime['link_url'].rsplit('-episode-', 1)[0]
        if slug_base == title_slug:
            try:
                return int(anime['episode'])
            except:
                pass
    return None

def check_episode_exists(title_slug, episode_num, scraper):
    """Check if a specific episode exists by checking for video source"""
    try:
        embed_url = f"https://2anime.xyz/embed/{title_slug}-episode-{episode_num}"
        response = scraper.get(embed_url, timeout=10)
        if response.status_code != 200:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        video = soup.find('video')
        if video:
            source = video.find('source')
            if source and 'src' in source.attrs and source['src']:
                return True
        # Check for error indicators
        content_lower = response.text.lower()
        if any(error in content_lower for error in ['not found', '404', 'error', 'no episode', 'no video']):
            return False
        return False  # If no video source found, assume unavailable
    except Exception as e:
        logger.debug(f"Episode {episode_num} check failed: {e}")
        return False

@lru_cache(maxsize=100)
def discover_episodes(title_slug, max_episodes=2000, batch_size=50):
    """
    Discover available episodes for an anime by checking up to max_episodes
    Uses threading for faster discovery with batching for efficiency
    """
    logger.info(f"Starting episode discovery for {title_slug} (max: {max_episodes})")
    start_time = time.time()
    
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    # Get latest episode from API to set accurate max
    latest = get_latest_episode(title_slug)
    if latest:
        max_episodes = latest + 50  # Buffer for ongoing series or errors
        logger.info(f"Set max_episodes to {max_episodes} based on API data")
    
    available_episodes = set()
    checked_episodes = 0
    
    def check_batch(episode_range):
        """Check a batch of episodes"""
        batch_available = []
        for ep_num in episode_range:
            if check_episode_exists(title_slug, ep_num, scraper):
                batch_available.append(ep_num)
        return batch_available
    
    # Process episodes in batches using thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Create batches
        batches = []
        for i in range(1, max_episodes + 1, batch_size):
            batch_end = min(i + batch_size - 1, max_episodes)
            batches.append(range(i, batch_end + 1))
        
        # Submit all batches
        future_to_batch = {executor.submit(check_batch, batch): batch for batch in batches}
        
        # Process completed batches
        consecutive_empty_batches = 0
        for future in concurrent.futures.as_completed(future_to_batch):
            batch_result = future.result()
            available_episodes.update(batch_result)
            
            batch_range = future_to_batch[future]
            checked_episodes += len(batch_range)
            
            # Log progress
            if len(batch_result) == 0:
                consecutive_empty_batches += 1
            else:
                consecutive_empty_batches = 0
                
            logger.info(f"Batch {batch_range[0]}-{batch_range[-1]}: Found {len(batch_result)} episodes "
                        f"(Total: {len(available_episodes)}/{checked_episodes})")
            
            # Early termination if we find too many consecutive empty batches
            if consecutive_empty_batches >= 3 and len(available_episodes) > 0:  # Reduced to 3 for faster stopping
                logger.info("Stopping early - found consecutive empty batches")
                break
    
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)
    
    # Use API latest as total if available, else max available
    total_episodes = latest or max(available_episodes) if available_episodes else checked_episodes
    available_count = len(available_episodes)
    success_rate = round((available_count / total_episodes) * 100, 1) if total_episodes > 0 else 0
    
    discovery_info = {
        'total_episodes': total_episodes,
        'available_episodes': available_count,
        'available_list': sorted(list(available_episodes)),
        'success_rate': success_rate,
        'time_taken': time_taken,
        'checked_episodes': checked_episodes
    }
    
    logger.info(f"Discovery complete for {title_slug}: {available_count} episodes found in {time_taken}s")
    return discovery_info

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
        
        nav = {
            'prev': f"{title}-episode-{episode_num-1}" if episode_num > 1 else None,
            'next': f"{title}-episode-{episode_num+1}",
            'title_slug': title,
            'current_episode': episode_num
        }
        return nav
    except Exception as e:
        logger.error(f"Failed to generate episode navigation: {e}")
        return None

@app.route('/')
def home():
    # Fetch both trending and latest episodes for home page
    trending_anime = fetch_api_data("https://animeapi.skin/trending")
    latest_episodes = fetch_api_data("https://animeapi.skin/new?page=1")
    
    error = None
    debug_info = None
    
    # Handle fallbacks
    if trending_anime is None:
        error = "Failed to load trending anime. Using fallback content."
        debug_info = "Cloudflare protection may be active. Try again later or use a VPN/proxy."
        trending_anime = get_fallback_data()
    
    if latest_episodes is None:
        if not error:  # Only set if not already set
            error = "Failed to load latest episodes. Using fallback content."
            debug_info = "Cloudflare protection may be active. Try again later or use a VPN/proxy."
        latest_episodes = get_fallback_data()
    
    # Limit latest episodes to 20 for home page
    if latest_episodes and len(latest_episodes) > 20:
        latest_episodes = latest_episodes[:20]
    
    return render_template_string(HTML_TEMPLATE, 
                               page_title="Welcome to Anicute",
                               trending_anime=trending_anime,
                               latest_episodes=latest_episodes,
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
        error = "Failed to load new releases. Using fallback content."
        debug_info = "Cloudflare protection may be active. Try again later or use a VPN/proxy."
        anime_list = get_fallback_data()
    pagination = {
        'prev_url': f'/new?page={page-1}' if page > 1 else None,
        'next_url': f'/new?page={page+1}',
        'has_next': len(anime_list) > 0 if anime_list else True
    }
    return render_template_string(HTML_TEMPLATE, 
                               page_title="Latest Episodes",
                               anime_list=anime_list,
                               error=error,
                               debug_info=debug_info,
                               pagination=pagination,
                               page=page)

@app.route('/trending')
def trending():
    anime_list = fetch_api_data("https://animeapi.skin/trending")
    error = None
    debug_info = None
    if anime_list is None:
        error = "Failed to load trending anime. Using fallback content."
        debug_info = "Cloudflare protection may be active. Try again later or use a VPN/proxy."
        anime_list = get_fallback_data()
    return render_template_string(HTML_TEMPLATE, 
                               page_title="Trending Anime This Week",
                               anime_list=anime_list,
                               error=error,
                               debug_info=debug_info)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    anime_list = fetch_api_data(f"https://animeapi.skin/search?q={query}&page={page}")
    error = None
    debug_info = None
    if anime_list is None:
        error = f"No results found for '{query}'. Try a different search term."
        debug_info = "Cloudflare protection may be active. Try again later or use a VPN/proxy."
        anime_list = []
    elif len(anime_list) == 0:
        error = f"No results found for '{query}'. Try a different search term."
        
    pagination = {
        'prev_url': f'/search?q={query}&page={page-1}' if page > 1 else None,
        'next_url': f'/search?q={query}&page={page+1}',
        'has_next': len(anime_list) > 0 if anime_list else False
    }
    return render_template_string(HTML_TEMPLATE, 
                               page_title=f"Search Results for '{query}'",
                               anime_list=anime_list,
                               error=error,
                               debug_info=debug_info,
                               pagination=pagination,
                               page=page)

@app.route('/watch/<path:link_url>')
def watch(link_url):
    embed_url = f"https://2anime.xyz/embed/{link_url}"
    video_src = extract_video_src(embed_url)
    episode_nav = get_episode_navigation(link_url)
    
    # Extract anime title for better page title
    page_title = "Watch Anime"
    anime_title = "Unknown Anime"
    title_slug = None
    current_episode = None
    latest_episode = None
    if episode_nav:
        title_slug = episode_nav['title_slug']
        anime_title = title_slug.replace('-', ' ').title()
        current_episode = episode_nav['current_episode']
        page_title = f"Watch {anime_title} - Episode {current_episode}"
        latest_episode = get_latest_episode(title_slug)
    
    return render_template_string(HTML_TEMPLATE, 
                               page_title=page_title,
                               anime_title=anime_title,
                               embed_url=embed_url,
                               video_src=video_src,
                               episode_nav=episode_nav,
                               title_slug=title_slug,
                               current_episode=current_episode,
                               episode_discovery=None,
                               latest_episode=latest_episode)

@app.route('/discover/<path:link_url>')
def discover_anime_episodes(link_url):
    """Discover all available episodes for an anime"""
    episode_nav = get_episode_navigation(link_url)
    
    if not episode_nav:
        return render_template_string(HTML_TEMPLATE, 
                                   page_title="Error",
                                   error="Invalid episode URL format")
    
    title_slug = episode_nav['title_slug']
    
    # Check if we already have cached discovery data
    discovery_info = discover_episodes(title_slug, max_episodes=2000)
    
    embed_url = f"https://2anime.xyz/embed/{link_url}"
    video_src = extract_video_src(embed_url)
    
    # Extract anime title for better page title
    anime_title = title_slug.replace('-', ' ').title()
    episode_num = episode_nav['current_episode']
    page_title = f"Watch {anime_title} - Episode {episode_num}"
    latest_episode = get_latest_episode(title_slug)
    
    return render_template_string(HTML_TEMPLATE, 
                               page_title=page_title,
                               anime_title=anime_title,
                               embed_url=embed_url,
                               video_src=video_src,
                               episode_nav=episode_nav,
                               title_slug=title_slug,
                               current_episode=episode_num,
                               episode_discovery=discovery_info,
                               latest_episode=latest_episode)

if __name__ == '__main__':
    logger.info("Starting Premium Anicute anime streaming server...")
    logger.info("🚀 Server starting on http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

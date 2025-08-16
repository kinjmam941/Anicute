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

# HTML template with brutalist design
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Anicute - Watch Anime Online</title>
    <style>
        :root {
            --primary-color: #ff4757;
            --secondary-color: #2f3542;
            --accent-color: #5ad641;
            --warning-color: #ffa502;
            --bg-color: #f1f2f6;
            --text-color: #000000;
            --white: #ffffff;
            --border-width: 4px;
            --shadow-offset: 8px;
            --hover-shadow-offset: 12px;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Arial Black', Arial, sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.4;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Brutalist Card Base */
        .brutal-card {
            background: var(--white);
            border: var(--border-width) solid var(--text-color);
            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-color);
            transition: transform 0.3s, box-shadow 0.3s;
            position: relative;
        }
        
        .brutal-card:hover {
            transform: translate(-3px, -3px);
            box-shadow: var(--hover-shadow-offset) var(--hover-shadow-offset) 0 var(--text-color);
        }
        
        /* Header Styles */
        header {
            background: var(--primary-color);
            border-bottom: var(--border-width) solid var(--text-color);
            box-shadow: 0 var(--shadow-offset) 0 var(--text-color);
            padding: 0;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .header-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 20px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: var(--white);
            font-weight: 900;
            font-size: 2rem;
            text-transform: uppercase;
            transition: transform 0.3s ease;
            order: 1;
        }
        
        .logo:hover {
            transform: scale(1.05);
            color: var(--white);
            animation: glitch 0.3s;
        }
        
        .logo img {
            height: 50px;
            width: 50px;
            border: 3px solid var(--text-color);
            margin-right: 15px;
            object-fit: cover;
            background: var(--white);
        }
        
        .logo-text {
            text-shadow: 3px 3px 0 var(--text-color);
        }
        
        nav {
            display: none;
            gap: 10px;
            order: 3;
        }
        
        nav a {
            color: var(--white);
            text-decoration: none;
            padding: 12px 20px;
            font-weight: 900;
            text-transform: uppercase;
            transition: all 0.3s ease;
            background: var(--secondary-color);
            border: 3px solid var(--text-color);
            box-shadow: 4px 4px 0 var(--text-color);
        }
        
        nav a:hover {
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0 var(--text-color);
            background: var(--accent-color);
            color: var(--text-color);
        }
        
        .mobile-menu-btn {
            background: var(--secondary-color);
            border: 3px solid var(--text-color);
            color: var(--white);
            font-size: 1.5rem;
            font-weight: 900;
            padding: 12px 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            order: 2;
            box-shadow: 4px 4px 0 var(--text-color);
            text-transform: uppercase;
        }
        
        .mobile-menu-btn:hover {
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0 var(--text-color);
            background: var(--accent-color);
            color: var(--text-color);
        }
        
        .search-container {
            position: relative;
            width: 100%;
            order: 4;
        }
        
        .search-bar {
            display: flex;
            background: var(--white);
            border: var(--border-width) solid var(--text-color);
            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-color);
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .search-bar:focus-within {
            transform: translate(-2px, -2px);
            box-shadow: 10px 10px 0 var(--text-color);
        }
        
        .search-bar input {
            flex: 1;
            padding: 15px 20px;
            border: none;
            background: transparent;
            color: var(--text-color);
            font-size: 1.1rem;
            font-weight: 700;
            outline: none;
        }
        
        .search-bar input::placeholder {
            color: #666;
            font-weight: 600;
        }
        
        .search-bar input:focus {
            background: var(--accent-color);
        }
        
        .search-bar button {
            padding: 15px 25px;
            border: none;
            border-left: 3px solid var(--text-color);
            background: var(--primary-color);
            color: var(--white);
            font-weight: 900;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-size: 1.1rem;
        }
        
        .search-bar button:hover {
            background: var(--secondary-color);
        }
        
        /* Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        
        /* Page Title */
        .page-title {
            color: var(--text-color);
            text-align: center;
            margin: 30px 0 50px 0;
            font-size: 3rem;
            font-weight: 900;
            text-transform: uppercase;
            text-shadow: 4px 4px 0 var(--primary-color);
            position: relative;
            overflow: hidden;
        }
        
        .page-title::after {
            content: "";
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 6px;
            background-color: var(--accent-color);
            border: 2px solid var(--text-color);
        }
        
        /* Episode Info Section */
        .episode-info-card {
            background: var(--white);
            border: var(--border-width) solid var(--text-color);
            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-color);
            padding: 30px;
            margin: 30px 0;
        }
        
        .anime-details {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .anime-title-section {
            text-align: center;
            padding: 20px;
            background: var(--primary-color);
            border: 3px solid var(--text-color);
            color: var(--white);
        }
        
        .anime-title-main {
            font-size: 2rem;
            font-weight: 900;
            text-transform: uppercase;
            margin-bottom: 10px;
            text-shadow: 2px 2px 0 var(--text-color);
        }
        
        .current-episode {
            font-size: 1.3rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        
        .episode-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .stat-item {
            background: var(--accent-color);
            padding: 20px;
            text-align: center;
            border: var(--border-width) solid var(--text-color);
            box-shadow: 6px 6px 0 var(--text-color);
            transition: transform 0.3s;
        }
        
        .stat-item:hover {
            transform: translate(-3px, -3px);
            box-shadow: 9px 9px 0 var(--text-color);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 900;
            color: var(--text-color);
        }
        
        .stat-label {
            font-size: 1rem;
            color: var(--text-color);
            margin-top: 8px;
            font-weight: 700;
            text-transform: uppercase;
        }
        
        .discovery-status {
            text-align: center;
            padding: 20px;
            margin: 20px 0;
            font-weight: 900;
            text-transform: uppercase;
            border: var(--border-width) solid var(--text-color);
        }
        
        .discovery-loading {
            background: var(--warning-color);
            color: var(--text-color);
            box-shadow: 6px 6px 0 var(--text-color);
        }
        
        .discovery-complete {
            background: var(--accent-color);
            color: var(--text-color);
            box-shadow: 6px 6px 0 var(--text-color);
        }
        
        .discovery-error {
            background: var(--primary-color);
            color: var(--white);
            box-shadow: 6px 6px 0 var(--text-color);
        }
        
        .episode-message {
            text-align: center;
            color: var(--text-color);
            font-size: 1rem;
            margin: 20px 0;
            padding: 15px;
            background: var(--warning-color);
            border: 3px solid var(--text-color);
            font-weight: 700;
        }
        
        /* Video Player */
        .video-section {
            margin: 40px 0;
        }
        
        .embed-container {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            background: var(--text-color);
            margin-bottom: 30px;
            border: var(--border-width) solid var(--text-color);
            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-color);
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
            background: var(--white);
            border: var(--border-width) solid var(--text-color);
            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-color);
            padding: 30px;
            margin: 30px 0;
        }
        
        .episode-input-section {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .episode-input-container {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .episode-input {
            flex: 1;
            padding: 15px 20px;
            background: var(--white);
            border: var(--border-width) solid var(--text-color);
            color: var(--text-color);
            font-size: 1.1rem;
            font-weight: 700;
            outline: none;
            transition: all 0.3s ease;
            box-shadow: 4px 4px 0 var(--text-color);
        }
        
        .episode-input:focus {
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0 var(--text-color);
            background: var(--accent-color);
        }
        
        .episode-input::placeholder {
            color: #666;
            font-weight: 600;
        }
        
        .load-episode-btn, .discover-btn {
            padding: 15px 25px;
            background: var(--primary-color);
            border: var(--border-width) solid var(--text-color);
            color: var(--white);
            font-weight: 900;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
            text-transform: uppercase;
            box-shadow: 4px 4px 0 var(--text-color);
            position: relative;
            overflow: hidden;
        }
        
        .discover-btn {
            background: var(--secondary-color);
            display: none;
        }
        
        .load-episode-btn::before, .discover-btn::before {
            content: "SURE?";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: var(--accent-color);
            color: var(--text-color);
            display: flex;
            align-items: center;
            justify-content: center;
            transform: translateY(100%);
            transition: transform 0.3s;
            font-weight: 900;
        }
        
        .load-episode-btn:hover::before, .discover-btn:hover::before {
            transform: translateY(0);
        }
        
        .load-episode-btn:hover, .discover-btn:hover {
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0 var(--text-color);
        }
        
        .load-episode-btn:active, .discover-btn:active {
            transform: scale(0.95);
        }
        
        .episode-navigation {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .nav-btn {
            padding: 15px 25px;
            border: var(--border-width) solid var(--text-color);
            font-weight: 900;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s ease;
            font-size: 1rem;
            text-transform: uppercase;
            box-shadow: 4px 4px 0 var(--text-color);
            position: relative;
            overflow: hidden;
        }
        
        .prev-btn, .next-btn {
            background: var(--primary-color);
            color: var(--white);
        }
        
        .download-btn {
            background: var(--accent-color);
            color: var(--text-color);
        }
        
        .nav-btn::before {
            content: "GO!";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: var(--secondary-color);
            color: var(--white);
            display: flex;
            align-items: center;
            justify-content: center;
            transform: translateY(100%);
            transition: transform 0.3s;
            font-weight: 900;
        }
        
        .download-btn::before {
            background-color: var(--warning-color);
            color: var(--text-color);
        }
        
        .nav-btn:hover::before {
            transform: translateY(0);
        }
        
        .nav-btn:hover {
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0 var(--text-color);
        }
        
        /* Episode Grid */
        .episode-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            gap: 15px;
            margin: 30px 0;
            padding: 20px;
            background: var(--bg-color);
            border: var(--border-width) solid var(--text-color);
            max-height: 400px;
            overflow-y: auto;
        }
        
        .episode-item {
            padding: 15px;
            text-align: center;
            text-decoration: none;
            color: var(--text-color);
            border: 3px solid var(--text-color);
            transition: all 0.3s ease;
            font-size: 1rem;
            font-weight: 900;
            text-transform: uppercase;
            box-shadow: 3px 3px 0 var(--text-color);
        }
        
        .episode-item.available {
            background: var(--accent-color);
        }
        
        .episode-item.current {
            background: var(--primary-color);
            color: var(--white);
        }
        
        .episode-item.unavailable {
            background: #ccc;
            color: #666;
            cursor: not-allowed;
        }
        
        .episode-item.available:hover {
            transform: translate(-2px, -2px);
            box-shadow: 5px 5px 0 var(--text-color);
        }
        
        /* Mobile Menu */
        .mobile-menu {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--secondary-color);
            border: var(--border-width) solid var(--text-color);
            border-top: none;
            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-color);
            z-index: 999;
        }
        
        .mobile-menu.active {
            display: block;
        }
        
        .mobile-menu a {
            display: block;
            color: var(--white);
            text-decoration: none;
            padding: 15px 20px;
            font-weight: 900;
            text-transform: uppercase;
            border-bottom: 2px solid var(--text-color);
            transition: all 0.3s ease;
        }
        
        .mobile-menu a:hover {
            background: var(--accent-color);
            color: var(--text-color);
        }
        
        /* Anime Grid */
        .anime-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 50px 0;
        }
        
        .anime-card {
            background: var(--white);
            border: var(--border-width) solid var(--text-color);
            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-color);
            overflow: hidden;
            transition: all 0.4s ease;
            position: relative;
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .anime-card:hover {
            transform: translate(-5px, -5px);
            box-shadow: 15px 15px 0 var(--text-color);
        }
        
        .anime-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            object-position: center;
            border-bottom: var(--border-width) solid var(--text-color);
            transition: transform 0.4s ease;
            flex-shrink: 0;
        }
        
        .anime-card:hover .anime-image {
            transform: scale(1.05);
        }
        
        .anime-info {
            padding: 20px;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }
        
        .anime-title {
            font-weight: 900;
            font-size: 1.1rem;
            margin-bottom: 12px;
            color: var(--text-color);
            line-height: 1.2;
            text-transform: uppercase;
            height: 2.4em;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .anime-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-size: 0.9rem;
            color: var(--text-color);
            font-weight: 700;
        }
        
        .episode-info {
            background: var(--primary-color);
            color: var(--white);
            padding: 6px 12px;
            border: 2px solid var(--text-color);
            font-weight: 900;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        
        .anime-genres {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }
        
        .genre-tag {
            background: var(--accent-color);
            color: var(--text-color);
            padding: 4px 10px;
            font-size: 0.7rem;
            font-weight: 700;
            border: 2px solid var(--text-color);
            text-transform: uppercase;
        }
        
        .anime-description {
            color: var(--text-color);
            font-size: 0.9rem;
            margin-bottom: auto;
            height: 4.2em;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.4;
            font-weight: 600;
        }
        
        .watch-btn {
            display: block;
            background: var(--primary-color);
            color: var(--white);
            padding: 15px 0;
            text-align: center;
            text-decoration: none;
            font-weight: 900;
            font-size: 1rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            border: 3px solid var(--text-color);
            text-transform: uppercase;
            box-shadow: 4px 4px 0 var(--text-color);
            margin-top: 20px;
            flex-shrink: 0;
        }
        
        .watch-btn::before {
            content: 'WATCH NOW!';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--accent-color);
            color: var(--text-color);
            display: flex;
            align-items: center;
            justify-content: center;
            transform: translateY(100%);
            transition: transform 0.3s;
            font-weight: 900;
        }
        
        .watch-btn:hover::before {
            transform: translateY(0);
        }
        
        .watch-btn:hover {
            transform: translate(-3px, -3px);
            box-shadow: 7px 7px 0 var(--text-color);
        }
        
        /* Loading Spinner */
        .loading-spinner {
            border: 4px solid var(--bg-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes glitch {
            0% { transform: translate(2px, 2px); }
            25% { transform: translate(-2px, -2px); }
            50% { transform: translate(-2px, 2px); }
            75% { transform: translate(2px, -2px); }
            100% { transform: translate(2px, 2px); }
        }
        
        .glitch {
            animation: glitch 0.3s infinite;
        }
        
        /* Error and loading styles */
        .loading {
            text-align: center;
            font-size: 1.5rem;
            font-weight: 900;
            color: var(--text-color);
            padding: 50px;
            background: var(--warning-color);
            border: var(--border-width) solid var(--text-color);
            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-color);
            text-transform: uppercase;
        }
        
        .error {
            text-align: center;
            font-size: 1.5rem;
            font-weight: 900;
            color: var(--white);
            padding: 50px;
            background: var(--primary-color);
            border: var(--border-width) solid var(--text-color);
            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-color);
            margin: 30px 0;
            text-transform: uppercase;
        }
        
        /* Pagination */
        .pagination {
            text-align: center;
            margin: 40px 0;
        }
        
        .pagination a {
            color: var(--white);
            text-decoration: none;
            margin: 0 10px;
            font-weight: 900;
            padding: 15px 25px;
            background: var(--primary-color);
            border: var(--border-width) solid var(--text-color);
            transition: all 0.3s ease;
            text-transform: uppercase;
            box-shadow: 4px 4px 0 var(--text-color);
            display: inline-block;
        }
        
        .pagination a:hover {
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0 var(--text-color);
            background: var(--accent-color);
            color: var(--text-color);
        }
        
        /* Footer Styles */
        footer {
            background: var(--secondary-color);
            color: var(--white);
            padding: 30px 20px;
            border-top: var(--border-width) solid var(--text-color);
            box-shadow: 0 -var(--shadow-offset) 0 var(--text-color);
            text-align: center;
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-top: 40px;
        }
        
        footer p {
            margin: 10px 0;
        }
        
        footer a {
            color: var(--accent-color);
            text-decoration: none;
            font-weight: 900;
        }
        
        footer a:hover {
            color: var(--warning-color);
        }
        
        /* Responsive Design */
        @media (min-width: 480px) {
            .anime-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 25px;
            }
            
            .anime-image {
                height: 220px;
            }
            
            .anime-title {
                font-size: 1.2rem;
            }
        }
        
        @media (min-width: 768px) {
            .header-container {
                flex-wrap: nowrap;
                gap: 25px;
            }
            
            .search-container {
                flex-grow: 1;
                order: 2;
                width: auto;
                max-width: 600px;
            }
            
            .mobile-menu-btn {
                display: none;
            }
            
            nav {
                display: flex;
                order: 3;
            }
            
            .anime-grid {
                grid-template-columns: repeat(3, 1fr);
                gap: 30px;
            }
            
            .anime-image {
                height: 250px;
            }
            
            .anime-info {
                padding: 25px;
            }
            
            .anime-title {
                font-size: 1.3rem;
                margin-bottom: 15px;
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
                grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
            }
        }
        
        @media (min-width: 1024px) {
            .anime-grid {
                grid-template-columns: repeat(4, 1fr);
            }
            
            .anime-image {
                height: 280px;
            }
            
            .episode-stats {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        @media (min-width: 1200px) {
            .anime-grid {
                grid-template-columns: repeat(5, 1fr);
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-container">
            <a href="/" class="logo">
                <img src="https://i.pinimg.com/736x/83/c3/44/83c344c68b92ac98c4c1451d4d0478e6.jpg" alt="Anicute Logo">
                <span class="logo-text">Anicute</span>
            </a>
            
            <div class="search-container">
                <form class="search-bar" action="/search" method="GET">
                    <input type="text" name="q" placeholder="SEARCH ANIME..." required>
                    <button type="submit" aria-label="Search">SEARCH</button>
                </form>
            </div>
            
            <nav>
                <a href="/">Home</a>
                <a href="/new">New</a>
                <a href="/trending">Trending</a>
            </nav>
            
            <button class="mobile-menu-btn" aria-label="Open menu" onclick="toggleMobileMenu()">MENU</button>
            
            <!-- Mobile Menu -->
            <div class="mobile-menu" id="mobileMenu">
                <a href="/">Home</a>
                <a href="/new">New Releases</a>
                <a href="/trending">Trending</a>
            </div>
        </div>
    </header>

    <div class="container">
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
                ✅ EPISODE DISCOVERY COMPLETED! FOUND {{ episode_discovery.available_episodes }} AVAILABLE EPISODES.
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
                            placeholder="ENTER EPISODE NUMBER..."
                            min="1"
                            max="{{ episode_discovery.total_episodes if episode_discovery else 2000 }}"
                            value="{{ current_episode }}"
                        >
                        <button class="load-episode-btn" onclick="loadEpisode()">LOAD EPISODE</button>
                    </div>
                    <button class="discover-btn" onclick="discoverEpisodes()">🔍 DISCOVER ALL EPISODES</button>
                </div>
                
                <div class="episode-message">
                    SOMETIMES EPISODE COUNTS ARE NOT LOADED PROPERLY. TRY ENTERING THE LATEST EPISODE NUMBER.
                </div>
                
                <div class="episode-navigation">
                    {% if video_src %}
                    <a href="{{ video_src }}" class="nav-btn download-btn" download>📥 DOWNLOAD</a>
                    {% endif %}
                    
                    {% if episode_nav %}
                        {% if episode_nav.prev %}
                        <a href="/watch/{{ episode_nav.prev }}" class="nav-btn prev-btn">← PREVIOUS</a>
                        {% endif %}
                        
                        {% if episode_nav.next %}
                        <a href="/watch/{{ episode_nav.next }}" class="nav-btn next-btn">NEXT →</a>
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
            <h3>⚠️ {{ error }}</h3>
            {% if debug_info %}
            <div style="margin-top: 20px; color: #fff; font-size: 0.9rem; font-weight: 600;">
                DEBUG INFO: {{ debug_info }}
            </div>
            {% endif %}
        </div>
        {% elif not anime_list and not embed_url %}
        <div class="loading">
            <div class="loading-spinner"></div>
            LOADING ANIME...
        </div>
        {% endif %}
        
        {% if anime_list %}
        <div class="anime-grid">
            {% for anime in anime_list %}
            <div class="anime-card">
                <img src="{{ anime.thumbnail_url }}" alt="{{ anime.title }}" class="anime-image" 
                     onerror="this.src='https://via.placeholder.com/400x300/f1f2f6/000000?text=NO+IMAGE'">
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
                    <a href="/watch/{{ anime.link_url }}" class="watch-btn">▶️ WATCH NOW</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if pagination %}
        <div class="pagination">
            {% if pagination.prev_url %}
            <a href="{{ pagination.prev_url }}">← PREVIOUS</a>
            {% endif %}
            <span style="font-weight: 900; color: var(--text-color); text-transform: uppercase; margin: 0 15px;">PAGE {{ page }}</span>
            {% if pagination.has_next %}
            <a href="{{ pagination.next_url }}">NEXT →</a>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <footer>
        <p>&copy; 2025 Anicute. All rights reserved.</p>
        <p>DMCA Compliance: We respect the intellectual property rights of others. All media content on this site is served by third-party providers, and we do not claim ownership of any media displayed. Anicute acts solely as a platform to aggregate and serve this content.</p>
        <p>For DMCA complaints or content removal requests, please contact us at <a href="mailto:02qttt@gmail.com">02qttt@gmail.com</a>.</p>
    </footer>

    <script>
        function toggleMobileMenu() {
            const mobileMenu = document.getElementById('mobileMenu');
            const menuBtn = document.querySelector('.mobile-menu-btn');
            
            mobileMenu.classList.toggle('active');
            
            if (mobileMenu.classList.contains('active')) {
                menuBtn.textContent = 'CLOSE';
                menuBtn.classList.add('glitch');
            } else {
                menuBtn.textContent = 'MENU';
                menuBtn.classList.remove('glitch');
            }
        }
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            const mobileMenu = document.getElementById('mobileMenu');
            const menuBtn = document.querySelector('.mobile-menu-btn');
            
            if (!menuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.remove('active');
                menuBtn.textContent = 'MENU';
                menuBtn.classList.remove('glitch');
            }
        });
        
        function loadEpisode() {
            const episodeNumber = document.getElementById('episodeNumber').value;
            if (!episodeNumber) {
                alert('PLEASE ENTER AN EPISODE NUMBER!');
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
                    
                    // Add glitch effect to button
                    const btn = document.querySelector('.load-episode-btn');
                    btn.classList.add('glitch');
                    
                    setTimeout(() => {
                        window.location.href = `/watch/${newEpisodeUrl}`;
                    }, 300);
                } else {
                    alert('COULD NOT DETERMINE ANIME TITLE FROM CURRENT URL!');
                }
            } else {
                alert('PLEASE NAVIGATE TO AN ANIME EPISODE PAGE FIRST!');
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
                            🔍 DISCOVERING EPISODES FOR ${animeTitle.replace(/-/g, ' ').toUpperCase()}... THIS MAY TAKE A FEW MINUTES.
                        </div>
                    `;
                    
                    // Add glitch effect
                    const btn = document.querySelector('.discover-btn');
                    btn.classList.add('glitch');
                    
                    setTimeout(() => {
                        window.location.href = `/discover/${currentEpisodeUrl}`;
                    }, 500);
                } else {
                    alert('COULD NOT DETERMINE ANIME TITLE FROM CURRENT URL!');
                }
            } else {
                alert('PLEASE NAVIGATE TO AN ANIME EPISODE PAGE FIRST!');
            }
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (document.querySelector('.embed-container')) {
                if (e.key === 'ArrowLeft') {
                    const prevBtn = document.querySelector('.prev-btn');
                    if (prevBtn) {
                        prevBtn.classList.add('glitch');
                        setTimeout(() => prevBtn.click(), 100);
                    }
                } else if (e.key === 'ArrowRight') {
                    const nextBtn = document.querySelector('.next-btn');
                    if (nextBtn) {
                        nextBtn.classList.add('glitch');
                        setTimeout(() => nextBtn.click(), 100);
                    }
                } else if (e.key === 'Enter' && e.target.id === 'episodeNumber') {
                    loadEpisode();
                }
            }
        });
        
        // Episode grid enhancements
        document.querySelectorAll('.episode-item.available').forEach(item => {
            item.addEventListener('click', function(e) {
                if (this.classList.contains('current')) {
                    e.preventDefault();
                    return false;
                }
                this.classList.add('glitch');
            });
        });
        
        // Add hover effects for brutalist feel
        document.querySelectorAll('.brutal-card, .anime-card, .nav-btn, .watch-btn').forEach(el => {
            el.addEventListener('mouseenter', function() {
                if (Math.random() > 0.8) {
                    this.classList.add('glitch');
                    setTimeout(() => this.classList.remove('glitch'), 300);
                }
            });
        });
        
        // Logo click effect
        document.querySelector('.logo').addEventListener('click', function(e) {
            this.classList.add('glitch');
            setTimeout(() => this.classList.remove('glitch'), 300);
        });
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
    anime_list = fetch_api_data("https://animeapi.skin/trending")
    error = None
    debug_info = None
    if anime_list is None:
        error = "FAILED TO LOAD TRENDING ANIME. USING FALLBACK CONTENT."
        debug_info = "CLOUDFLARE PROTECTION MAY BE ACTIVE. TRY AGAIN LATER OR USE A VPN/PROXY."
        anime_list = get_fallback_data()
    return render_template_string(HTML_TEMPLATE, 
                               page_title="WELCOME TO ANICUTE",
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
        error = "FAILED TO LOAD NEW RELEASES. USING FALLBACK CONTENT."
        debug_info = "CLOUDFLARE PROTECTION MAY BE ACTIVE. TRY AGAIN LATER OR USE A VPN/PROXY."
        anime_list = get_fallback_data()
    pagination = {
        'prev_url': f'/new?page={page-1}' if page > 1 else None,
        'next_url': f'/new?page={page+1}',
        'has_next': len(anime_list) > 0 if anime_list else True
    }
    return render_template_string(HTML_TEMPLATE, 
                               page_title="NEW ANIME RELEASES",
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
        error = "FAILED TO LOAD TRENDING ANIME. USING FALLBACK CONTENT."
        debug_info = "CLOUDFLARE PROTECTION MAY BE ACTIVE. TRY AGAIN LATER OR USE A VPN/PROXY."
        anime_list = get_fallback_data()
    return render_template_string(HTML_TEMPLATE, 
                               page_title="TRENDING ANIME THIS WEEK",
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
        error = f"NO RESULTS FOUND FOR '{query.upper()}'. TRY A DIFFERENT SEARCH TERM."
        debug_info = "CLOUDFLARE PROTECTION MAY BE ACTIVE. TRY AGAIN LATER OR USE A VPN/PROXY."
        anime_list = []
    elif len(anime_list) == 0:
        error = f"NO RESULTS FOUND FOR '{query.upper()}'. TRY A DIFFERENT SEARCH TERM."
        
    pagination = {
        'prev_url': f'/search?q={query}&page={page-1}' if page > 1 else None,
        'next_url': f'/search?q={query}&page={page+1}',
        'has_next': len(anime_list) > 0 if anime_list else False
    }
    return render_template_string(HTML_TEMPLATE, 
                               page_title=f"SEARCH RESULTS FOR '{query.upper()}'",
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
    page_title = "WATCH ANIME"
    anime_title = "UNKNOWN ANIME"
    title_slug = None
    current_episode = None
    latest_episode = None
    if episode_nav:
        title_slug = episode_nav['title_slug']
        anime_title = title_slug.replace('-', ' ').upper()
        current_episode = episode_nav['current_episode']
        page_title = f"WATCH {anime_title} - EPISODE {current_episode}"
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
                                   page_title="ERROR",
                                   error="INVALID EPISODE URL FORMAT")
    
    title_slug = episode_nav['title_slug']
    
    # Check if we already have cached discovery data
    discovery_info = discover_episodes(title_slug, max_episodes=2000)
    
    embed_url = f"https://2anime.xyz/embed/{link_url}"
    video_src = extract_video_src(embed_url)
    
    # Extract anime title for better page title
    anime_title = title_slug.replace('-', ' ').upper()
    episode_num = episode_nav['current_episode']
    page_title = f"WATCH {anime_title} - EPISODE {episode_num}"
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
    logger.info("Starting Enhanced Brutalist Anicute anime streaming server...")
    logger.info("🚀 Server starting on http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

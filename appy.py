import asyncio
import time
import httpx
import pandas as pd
import streamlit as st
from datetime import datetime
from collections import deque
import nest_asyncio

nest_asyncio.apply()

# --- PAGE CONFIG ---
st.set_page_config(page_title="⚡ Extreme Load Tester", page_icon="⚡", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #FF0080 0%, #FF8C00 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .extreme-mode {
        background: linear-gradient(135deg, #FF0000 0%, #8B0000 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- TITLE ---
st.markdown("""
    <div class="main-header">
        <h1>⚡ EXTREME SPEED LOAD TESTER</h1>
        <p>Maximum Performance | Zero Overhead | Blazing Fast</p>
    </div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "stop_event" not in st.session_state:
    st.session_state.stop_event = asyncio.Event()
if "test_history" not in st.session_state:
    st.session_state.test_history = []

# --- SPEED MODE SELECTOR ---
st.markdown("### ⚙️ Speed Configuration")
speed_mode = st.radio(
    "Select Mode:",
    ["🟢 Normal (Safe)", "🟡 Fast (Aggressive)", "🔴 EXTREME (Maximum Speed)", "💀 INSANE (Use at your own risk)"],
    horizontal=True
)

# Pre-configured settings based on mode
if speed_mode == "🟢 Normal (Safe)":
    default_requests = 1000
    default_concurrency = 100
    default_timeout = 10
    max_concurrency = 500
    max_requests = 10000
elif speed_mode == "🟡 Fast (Aggressive)":
    default_requests = 5000
    default_concurrency = 500
    default_timeout = 5
    max_concurrency = 2000
    max_requests = 50000
elif speed_mode == "🔴 EXTREME (Maximum Speed)":
    default_requests = 20000
    default_concurrency = 2000
    default_timeout = 3
    max_concurrency = 10000
    max_requests = 200000
else:  # INSANE
    default_requests = 100000
    default_concurrency = 5000
    default_timeout = 2
    max_concurrency = 50000
    max_requests = 1000000

if speed_mode in ["🔴 EXTREME (Maximum Speed)", "💀 INSANE (Use at your own risk)"]:
    st.markdown("""
        <div class="extreme-mode">
            ⚠️ EXTREME MODE ACTIVATED ⚠️<br>
            This will generate MASSIVE traffic. Server may crash. Use ONLY on test environments!
        </div>
    """, unsafe_allow_html=True)

# --- INPUTS ---
url = st.text_input("🎯 Target URL", placeholder="https://your-test-server.com")

col1, col2, col3 = st.columns(3)
with col1:
    req_total = st.number_input(
        "📦 Total Requests",
        min_value=1,
        max_value=max_requests,
        value=default_requests,
        step=1000
    )
with col2:
    concurrency = st.slider(
        "🚀 Concurrency",
        min_value=1,
        max_value=max_concurrency,
        value=default_concurrency
    )
with col3:
    timeout = st.number_input(
        "⏰ Timeout (s)",
        min_value=1,
        max_value=30,
        value=default_timeout
    )

# Advanced options
with st.expander("⚙️ Advanced Settings"):
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        keep_alive = st.checkbox("Keep-Alive Connections", value=True)
        http2 = st.checkbox("Enable HTTP/2", value=True)
    with col_a2:
        follow_redirects = st.checkbox("Follow Redirects", value=False)
        verify_ssl = st.checkbox("Verify SSL", value=True)
    with col_a3:
        update_interval = st.number_input("Update Interval", 100, 10000, 2000, 500)
        collect_response = st.checkbox("Collect Response Body", value=False)

st.warning("⚠️ **CRITICAL:** Only test YOUR OWN servers or with explicit written permission!", icon="🔥")

# --- OPTIMIZED WORKER ---
async def ultra_fast_worker(client, semaphore, url, results_queue, error_count):
    """Extremely optimized worker - minimal overhead"""
    try:
        async with semaphore:
            start = time.perf_counter()
            resp = await client.get(url)
            latency = time.perf_counter() - start
            
            # Minimal data collection for speed
            results_queue.append({
                "l": latency,  # shortened key
                "s": resp.status_code
            })
    except:
        error_count[0] += 1  # Use array for atomic increment


async def run_extreme_load(url, req_total, concurrency, timeout_val, http2_enabled, 
                           keep_alive_enabled, follow_redirects_enabled, verify_ssl_enabled,
                           update_interval_val, progress_bar, status_placeholder):
    """Extreme performance load testing"""
    
    results_queue = deque(maxlen=100000)  # Efficient ring buffer
    error_count = [0]  # Mutable container for errors
    
    # Ultra-optimized client configuration
    limits = httpx.Limits(
        max_connections=concurrency * 2,  # Double for better throughput
        max_keepalive_connections=concurrency * 2 if keep_alive_enabled else 0,
        keepalive_expiry=60 if keep_alive_enabled else 0
    )
    
    timeout_config = httpx.Timeout(
        timeout_val, 
        connect=min(2.0, timeout_val/2),  # Faster connect timeout
        pool=1.0  # Quick pool timeout
    )
    
    async with httpx.AsyncClient(
        http2=http2_enabled,
        limits=limits,
        timeout=timeout_config,
        follow_redirects=follow_redirects_enabled,
        verify=verify_ssl_enabled
    ) as client:
        
        # Create semaphore - this controls actual concurrency
        semaphore = asyncio.Semaphore(concurrency)
        
        # Create all tasks at once for maximum speed
        tasks = [
            ultra_fast_worker(client, semaphore, url, results_queue, error_count)
            for _ in range(req_total)
        ]
        
        start_time = time.time()
        completed = 0
        
        # Process tasks as they complete
        for coro in asyncio.as_completed(tasks):
            if st.session_state.stop_event.is_set():
                break
            
            await coro
            completed += 1
            
            # Update UI less frequently for speed
            if completed % update_interval_val == 0 or completed == req_total:
                elapsed = time.time() - start_time
                rps = completed / elapsed if elapsed > 0 else 0
                
                progress_bar.progress(min(completed / req_total, 1.0))
                
                status_placeholder.markdown(f"""
                ### ⚡ Live Stats
                - **Completed:** {completed:,} / {req_total:,}
                - **RPS:** {rps:,.0f} requests/sec
                - **Errors:** {error_count[0]:,}
                - **Success Rate:** {((completed - error_count[0]) / completed * 100):.1f}%
                - **Elapsed:** {elapsed:.2f}s
                """)
        
        total_time = time.time() - start_time
        
    return list(results_queue), error_count[0], total_time


# --- UI BUTTONS ---
col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
with col_btn1:
    start_btn = st.button("⚡ START EXTREME TEST", use_container_width=True, type="primary")
with col_btn2:
    stop_btn = st.button("🛑 EMERGENCY STOP", use_container_width=True)
with col_btn3:
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.test_history = []
        st.rerun()

if stop_btn:
    st.session_state.stop_event.set()
    st.error("🛑 EMERGENCY STOP ACTIVATED!", icon="🚨")

# --- RUN TEST ---
if start_btn:
    if not url or not url.startswith("http"):
        st.error("❌ Enter a valid URL (http:// or https://)")
        st.stop()
    
    # Safety confirmation for extreme modes
    if speed_mode in ["🔴 EXTREME (Maximum Speed)", "💀 INSANE (Use at your own risk)"]:
        st.error(f"⚠️ You are about to send {req_total:,} requests with {concurrency:,} concurrent connections!")
        if not st.checkbox("✅ I understand the risks and have permission to test this server"):
            st.stop()
    
    st.session_state.stop_event.clear()
    
    st.markdown("---")
    st.subheader("🔥 EXTREME LOAD TEST IN PROGRESS")
    
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    
    # Run the extreme test
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        results, error_count, duration = loop.run_until_complete(
            run_extreme_load(
                url, req_total, concurrency, timeout, http2, keep_alive,
                follow_redirects, verify_ssl, update_interval,
                progress_bar, status_placeholder
            )
        )
        
        loop.close()
        
    except Exception as e:
        st.error(f"💥 Test failed: {str(e)}")
        st.stop()
    
    if not results:
        st.warning("⚠️ No results collected")
        st.stop()
    
    # Process results
    df = pd.DataFrame(results)
    df.columns = ['latency', 'status']
    
    successful = len(results)
    total_attempted = req_total
    success_rate = (successful / total_attempted) * 100
    error_rate = (error_count / total_attempted) * 100
    throughput = successful / duration
    
    # Calculate percentiles
    latencies = df['latency'].values
    p50 = float(pd.Series(latencies).quantile(0.5))
    p90 = float(pd.Series(latencies).quantile(0.9))
    p95 = float(pd.Series(latencies).quantile(0.95))
    p99 = float(pd.Series(latencies).quantile(0.99))
    avg_latency = float(df['latency'].mean())
    min_latency = float(df['latency'].min())
    max_latency = float(df['latency'].max())
    
    # Save to history
    st.session_state.test_history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": speed_mode,
        "url": url,
        "requests": successful,
        "concurrency": concurrency,
        "duration": duration,
        "throughput": throughput,
        "errors": error_count,
        "p50": p50
    })
    
    # Display results
    st.markdown("---")
    st.success(f"✅ Test completed in {duration:.2f} seconds!")
    
    st.markdown("## 📊 Performance Metrics")
    
    # Top metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("⚡ Throughput", f"{throughput:,.0f} RPS")
    col2.metric("⏱️ Duration", f"{duration:.2f}s")
    col3.metric("✅ Success", f"{success_rate:.1f}%")
    col4.metric("📦 Completed", f"{successful:,}")
    col5.metric("❌ Errors", f"{error_count:,}")
    
    # Latency metrics
    st.markdown("### ⏱️ Latency Analysis")
    lat_col1, lat_col2, lat_col3, lat_col4, lat_col5, lat_col6, lat_col7 = st.columns(7)
    lat_col1.metric("Min", f"{min_latency*1000:.1f}ms")
    lat_col2.metric("Avg", f"{avg_latency*1000:.1f}ms")
    lat_col3.metric("p50", f"{p50*1000:.1f}ms")
    lat_col4.metric("p90", f"{p90*1000:.1f}ms")
    lat_col5.metric("p95", f"{p95*1000:.1f}ms")
    lat_col6.metric("p99", f"{p99*1000:.1f}ms")
    lat_col7.metric("Max", f"{max_latency*1000:.1f}ms")
    
    # Performance rating
    if throughput > 10000:
        perf_rating = "🔥 EXTREME PERFORMANCE"
        perf_color = "#FF0000"
    elif throughput > 5000:
        perf_rating = "⚡ EXCELLENT"
        perf_color = "#FF8C00"
    elif throughput > 1000:
        perf_rating = "✅ GOOD"
        perf_color = "#00AA00"
    else:
        perf_rating = "⚠️ NORMAL"
        perf_color = "#0066CC"
    
    st.markdown(f"""
        <div style="background: {perf_color}; color: white; padding: 1rem; 
                    border-radius: 8px; text-align: center; font-size: 1.5rem; 
                    font-weight: bold; margin: 1rem 0;">
            {perf_rating}
        </div>
    """, unsafe_allow_html=True)
    
    # Charts
    st.markdown("### 📈 Visual Analysis")
    tab1, tab2, tab3 = st.tabs(["Latency Distribution", "Status Codes", "Time Series"])
    
    with tab1:
        st.bar_chart(df['latency'].value_counts().sort_index().head(50))
    
    with tab2:
        status_counts = df['status'].value_counts()
        st.bar_chart(status_counts)
    
    with tab3:
        # Sample data for visualization if too many points
        if len(df) > 10000:
            sample_df = df.sample(n=10000)
            st.caption("(Showing 10,000 random samples for performance)")
        else:
            sample_df = df
        st.line_chart(sample_df['latency'])
    
    # Download
    st.markdown("### 💾 Export")
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Download Results (CSV)",
        csv,
        f"extreme_load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv"
    )

# Test History
if st.session_state.test_history:
    st.markdown("---")
    st.subheader("📜 Test History")
    history_df = pd.DataFrame(st.session_state.test_history)
    st.dataframe(history_df, use_container_width=True)

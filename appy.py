import asyncio
import time
import httpx
import pandas as pd
import streamlit as st
from prometheus_client import Histogram, CollectorRegistry
import nest_asyncio
from datetime import datetime

nest_asyncio.apply()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Premium Load Tester", page_icon="🚀", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    </style>
""", unsafe_allow_html=True)

# --- TITLE ---
st.markdown("""
    <div class="main-header">
        <h1>🚀 Premium Load Tester</h1>
        <p>Advanced Async Load Testing with Real-time Analytics</p>
    </div>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "registry" not in st.session_state:
    st.session_state.registry = CollectorRegistry()
    st.session_state.latency_hist = Histogram(
        "request_latency",
        "Latency histogram",
        buckets=[0.05, 0.1, 0.2, 0.4, 0.8, 1, 2, 5],
        registry=st.session_state.registry,
    )

if "stop_event" not in st.session_state:
    st.session_state.stop_event = asyncio.Event()

if "test_history" not in st.session_state:
    st.session_state.test_history = []

latency_hist = st.session_state.latency_hist

# --- INPUTS ---
with st.container():
    url = st.text_input(
        "🔗 Target HTTPS URL",
        placeholder="https://example.com",
        help="Enter the full URL including https://"
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        req_total = st.number_input(
            "📦 Total Requests",
            min_value=1,
            max_value=200000,
            value=5000,
            step=500,
            help="Total number of requests to send"
        )
    with col2:
        concurrency = st.slider(
            "👥 Concurrent Users",
            min_value=1,
            max_value=5000,
            value=500,
            help="Number of concurrent connections"
        )
    with col3:
        delay_ms = st.slider(
            "⏱ Rate Delay (ms)",
            min_value=0,
            max_value=500,
            value=0,
            help="Delay between requests"
        )

    col4, col5 = st.columns(2)
    with col4:
        timeout = st.number_input(
            "⏰ Timeout (seconds)",
            min_value=1,
            max_value=60,
            value=10,
            help="Request timeout"
        )
    with col5:
        update_interval = st.number_input(
            "📊 Update Interval",
            min_value=10,
            max_value=1000,
            value=50,
            help="Progress update frequency"
        )

st.warning("⚠️ **Important:** Use this tool ONLY for testing your own domain or with explicit permission.", icon="🔒")


# --- HELPER FUNCTIONS ---
async def detect_server_protocol(test_url: str, timeout_val: int):
    """Detect HTTP version and server information"""
    try:
        async with httpx.AsyncClient(http2=True) as client:
            r = await client.get(test_url, timeout=timeout_val)
            version = r.http_version
            server = r.headers.get("server", "Unknown")
            alt_svc = r.headers.get("alt-svc", "")
            http3 = "quic" in alt_svc.lower() or "h3" in alt_svc.lower()
            return {
                "version": version,
                "server": server,
                "http3": http3,
                "status": r.status_code,
                "headers_count": len(r.headers)
            }
    except Exception as e:
        return {"error": str(e)}


async def bounded_worker(client, results, errors, semaphore, url, delay_ms, timeout_val):
    """Worker coroutine with error handling"""
    try:
        async with semaphore:
            if delay_ms > 0:
                await asyncio.sleep(delay_ms / 1000)
            
            if st.session_state.stop_event.is_set():
                return
            
            start = time.perf_counter()
            resp = await client.get(url, timeout=timeout_val)
            latency = time.perf_counter() - start
            
            latency_hist.observe(latency)
            results.append({
                "latency": latency,
                "status": resp.status_code,
                "size": len(resp.content)
            })
    except Exception as e:
        errors.append(str(e))


async def run_load(progress, log_area, status_area, url, req_total, concurrency, delay_ms, timeout_val, update_interval):
    """Main load testing function with real-time updates"""
    results = []
    errors = []
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(http2=True, limits=httpx.Limits(max_connections=concurrency)) as client:
        tasks = [
            bounded_worker(client, results, errors, semaphore, url, delay_ms, timeout_val)
            for _ in range(req_total)
        ]
        
        done = 0
        start_time = time.time()
        
        for coro in asyncio.as_completed(tasks):
            if st.session_state.stop_event.is_set():
                break
            
            await coro
            done += 1
            
            if done % update_interval == 0 or done == req_total:
                progress.progress(done / req_total)
                elapsed = time.time() - start_time
                rps = done / elapsed if elapsed > 0 else 0
                
                log_area.markdown(f"""
                    **Progress:** {done}/{req_total} requests  
                    **RPS:** {rps:.2f} req/s  
                    **Errors:** {len(errors)}
                """)
                
                # Real-time metrics
                if results:
                    recent = [r["latency"] for r in results[-100:]]
                    avg_latency = sum(recent) / len(recent)
                    status_area.metric(
                        "Avg Latency (last 100)",
                        f"{avg_latency:.4f}s",
                        delta=f"{rps:.1f} RPS"
                    )

    return results, errors


# --- UI BUTTONS ---
col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
with col_btn1:
    start_btn = st.button("🚀 Start Test", use_container_width=True, type="primary")
with col_btn2:
    stop_btn = st.button("🛑 Stop Test", use_container_width=True)
with col_btn3:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.test_history = []
        st.rerun()


if stop_btn:
    st.session_state.stop_event.set()
    st.warning("⚠️ Test stopped by user", icon="🛑")


if start_btn:
    if not url.startswith("https://"):
        st.error("❌ HTTPS protocol required", icon="🔒")
        st.stop()

    # Detect protocol
    with st.spinner("🔍 Analyzing server..."):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            server_info = loop.run_until_complete(detect_server_protocol(url, timeout))
            loop.close()
        except Exception as e:
            st.error(f"❌ Failed to connect: {str(e)}")
            st.stop()

    if "error" in server_info:
        st.error(f"❌ Connection error: {server_info['error']}")
        st.stop()

    # Display server info
    with st.expander("🛰 Server Information", expanded=True):
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.metric("Server", server_info["server"])
        with info_col2:
            protocol = "HTTP/3 🔥" if server_info["http3"] else server_info["version"]
            st.metric("Protocol", protocol)
        with info_col3:
            st.metric("Status Code", server_info["status"])

    # Reset stop event
    st.session_state.stop_event.clear()

    # Test UI
    st.markdown("---")
    st.subheader("🏃 Running Load Test...")
    
    progress = st.progress(0)
    log_area = st.empty()
    status_area = st.empty()

    # Run test
    t0 = time.time()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results, errors = loop.run_until_complete(
        run_load(progress, log_area, status_area, url, req_total, concurrency, delay_ms, timeout, update_interval)
    )
    loop.close()
    duration = time.time() - t0

    if not results:
        st.warning("⚠️ No results collected (test may have been stopped)")
        st.stop()

    # Process results
    df = pd.DataFrame(results)
    
    success_rate = (len(results) / req_total) * 100
    error_rate = (len(errors) / req_total) * 100
    
    p50 = df.latency.quantile(0.5)
    p90 = df.latency.quantile(0.9)
    p95 = df.latency.quantile(0.95)
    p99 = df.latency.quantile(0.99)
    avg_latency = df.latency.mean()
    total_data = df['size'].sum() / (1024 * 1024)  # MB
    throughput = len(results) / duration

    # Save to history
    st.session_state.test_history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "requests": len(results),
        "duration": duration,
        "throughput": throughput,
        "p50": p50
    })

    # Display results
    st.markdown("---")
    st.subheader("📊 Test Results")

    # Metrics
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    metric_col1.metric("⏳ Duration", f"{duration:.2f}s")
    metric_col2.metric("✅ Success Rate", f"{success_rate:.1f}%")
    metric_col3.metric("🚀 Throughput", f"{throughput:.1f} RPS")
    metric_col4.metric("📦 Data Transfer", f"{total_data:.2f} MB")
    metric_col5.metric("❌ Errors", len(errors))

    st.markdown("### Latency Percentiles")
    perc_col1, perc_col2, perc_col3, perc_col4, perc_col5 = st.columns(5)
    perc_col1.metric("Average", f"{avg_latency:.4f}s")
    perc_col2.metric("p50 (Median)", f"{p50:.4f}s")
    perc_col3.metric("p90", f"{p90:.4f}s")
    perc_col4.metric("p95", f"{p95:.4f}s")
    perc_col5.metric("p99", f"{p99:.4f}s")

    # Charts
    st.markdown("### 📈 Latency Analysis")
    
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Time Series", "Distribution", "Status Codes"])
    
    with chart_tab1:
        st.line_chart(df.latency, use_container_width=True)
    
    with chart_tab2:
        st.bar_chart(df.latency.value_counts().sort_index(), use_container_width=True)
    
    with chart_tab3:
        if 'status' in df.columns:
            status_counts = df['status'].value_counts()
            st.bar_chart(status_counts, use_container_width=True)

    # Errors
    if errors:
        with st.expander(f"❌ Errors ({len(errors)})", expanded=False):
            error_df = pd.DataFrame(errors, columns=["Error"])
            st.dataframe(error_df, use_container_width=True)

    # Download results
    st.markdown("### 💾 Export Results")
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# Test History
if st.session_state.test_history:
    st.markdown("---")
    st.subheader("📜 Test History")
    history_df = pd.DataFrame(st.session_state.test_history)
    st.dataframe(history_df, use_container_width=True)

import asyncio
import time
import httpx
import pandas as pd
import streamlit as st
from prometheus_client import Histogram, CollectorRegistry

# --- TITLE ---
st.markdown("""
    <h1 style="text-align:center;">🚀 Premium Load Tester</h1>
    <p style="text-align:center;">Async Load Testing on Your Own Domain</p>
""", unsafe_allow_html=True)

# --- INPUTS ---
url = st.text_input("🔗 Target HTTPS URL", placeholder="https://example.com")
col1, col2 = st.columns(2)
with col1:
    req_total = st.number_input("📦 Total Requests", 1, 200000, 5000)
with col2:
    concurrency = st.slider("👥 Concurrent Users", 1, 5000, 500)

delay_ms = st.slider("⏱ Rate Delay (ms)", 0, 500, 0)

st.info("⚠️ Use this tool ONLY for testing your own domain.", icon="🔒")


# --- METRICS REGISTRY ---
if "registry" not in st.session_state:
    st.session_state.registry = CollectorRegistry()
    st.session_state.latency_hist = Histogram(
        "request_latency",
        "Latency histogram",
        buckets=[0.05,0.1,0.2,0.4,0.8,1,2,5],
        registry=st.session_state.registry,
    )

latency_hist = st.session_state.latency_hist


# --- STOP EVENT ---
if "stop_event" not in st.session_state:
    st.session_state.stop_event = asyncio.Event()


async def worker(client, results):
    await asyncio.sleep(delay_ms/1000)
    if st.session_state.stop_event.is_set():
        return
    start = time.perf_counter()
    resp = await client.get(url, timeout=5.0)
    latency = time.perf_counter() - start
    latency_hist.observe(latency)
    results.append(latency)


async def run(progress, log_area):
    results = []
    async with httpx.AsyncClient() as client:
        tasks = [worker(client, results) for _ in range(req_total)]
        done = 0

        for coro in asyncio.as_completed(tasks):
            if st.session_state.stop_event.is_set():
                break
            await coro
            done += 1
            if done % 50 == 0:
                progress.progress(done/req_total)
                log_area.write(f"▶ {done}/{req_total} processed")
    return results


# --- UI BUTTONS ---
start_btn = st.button("🚀 Start Test", use_container_width=True)
stop_btn = st.button("🛑 Stop", use_container_width=True)


if stop_btn:
    st.session_state.stop_event.set()
    st.warning("Stopped!", icon="🛑")


if start_btn:
    if not url.startswith("https://"):
        st.error("HTTPS only")
        st.stop()

    # reset stop
    st.session_state.stop_event.clear()

    progress = st.progress(0)
    log_area = st.empty()

    st.write("Running load test...")
    t0 = time.time()
    results = asyncio.run(run(progress, log_area))
    duration = time.time() - t0

    if not results:
        st.write("No results (Stopped)")
        st.stop()

    df = pd.DataFrame(results, columns=["latency"])

    p50 = df.latency.quantile(0.5)
    p90 = df.latency.quantile(0.9)
    p99 = df.latency.quantile(0.99)

    st.markdown("---")

    # CARD STYLE
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⏳ Total Time", f"{duration:.2f}s")
    c2.metric("p50", f"{p50:.4f}s")
    c3.metric("p90", f"{p90:.4f}s")
    c4.metric("p99", f"{p99:.4f}s")

    st.subheader("📊 Latency Chart")
    st.line_chart(df.latency)

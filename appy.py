import asyncio
import time
import httpx
import pandas as pd
import streamlit as st
from prometheus_client import Histogram
registry = CollectorRegistry()
latency_hist = Histogram(
    "request_latency",
    "Latency histogram",
    buckets=[0.05,0.1,0.2,0.4,0.8,1,2,5],
    registry=registry
)
st.title("Premium Load Testing Suite (Async - Safe Testing)")

url = st.text_input("Target HTTPS Website")
req_total = st.number_input("Total Requests", 1, 200000, 5000)
concurrency = st.slider("Concurrent Users", 1, 5000, 500)
delay_ms = st.slider("Rate Delay ms", 0, 500, 0)

st.write("This tool is intended ONLY for testing your own domain.")

latency_hist = Histogram(
    "request_latency",
    "Latency histogram",
    buckets=[0.05,0.1,0.2,0.4,0.8,1,2,5]
)

async def worker(client, results):
    await asyncio.sleep(delay_ms/1000)
    start = time.perf_counter()
    resp = await client.get(url, timeout=5.0)
    latency = time.perf_counter() - start
    latency_hist.observe(latency)
    results.append(latency)

async def run():
    results = []
    async with httpx.AsyncClient(http2=True) as client:
        tasks = [worker(client, results) for _ in range(req_total)]
        for i, f in enumerate(asyncio.as_completed(tasks)):
            await f
            if i % 100 == 0:
                st.write(f"... processed {i}")
    return results

if st.button("Start Test"):
    if not url.startswith("https://"):
        st.error("https only")
        st.stop()

    st.write("Running...")
    start = time.time()
    results = asyncio.run(run())
    total = time.time() - start

    df = pd.DataFrame(results, columns=["latency"])

    p50 = df.latency.quantile(0.5)
    p90 = df.latency.quantile(0.9)
    p99 = df.latency.quantile(0.99)

    st.subheader("Metrics")
    st.write(f"Total time: {total:.2f}s")
    st.write(f"p50: {p50:.4f}s")
    st.write(f"p90: {p90:.4f}s")
    st.write(f"p99: {p99:.4f}s")

    st.line_chart(df.latency)

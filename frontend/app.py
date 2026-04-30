import streamlit as st
import httpx
import pandas as pd

API = "http://localhost:8000/api/v1"

st.set_page_config(page_title="LLM Eval Platform", layout="wide")
st.title("LLM Evaluation Platform")

# 🔥 Check backend is running
try:
    httpx.get("http://localhost:8000/health", timeout=2)
except:
    st.error("⚠️ Backend not running. Start FastAPI server first.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Evaluate", "Logs", "Metrics"])

# =========================
# 🔹 TAB 1: EVALUATE
# =========================
with tab1:
    st.subheader("Submit a prompt")

    prompt = st.text_area("Prompt", height=120)
    reference = st.text_input("Reference (optional)")
    max_tokens = st.slider("Max tokens", 64, 1024, 512)

    if st.button("Run evaluation"):
        if not prompt.strip():
            st.error("Prompt cannot be empty")
        else:
            with st.spinner("Evaluating..."):
                try:
                    r = httpx.post(
                        f"{API}/evaluate",
                        json={
                            "prompt": prompt,
                            "reference": reference,
                            "max_tokens": max_tokens,
                        },
                        timeout=60,
                    )
                    r.raise_for_status()
                    data = r.json()

                    col1, col2 = st.columns(2)

                    # Response
                    with col1:
                        st.subheader("Response")
                        st.write(data["response"])
                        st.caption(
                            f"{data['model']} | {data['latency_ms']:.0f} ms"
                        )

                    # Scores
                    with col2:
                        st.subheader("Scores")
                        s = data["scores"]
                        st.metric("Overall", f"{s['overall_score']:.1f}")
                        st.metric("ROUGE-1", f"{s['rouge1_score']:.2f}")
                        st.metric("Length", f"{s['length_score']:.2f}")
                        st.metric(
                            "Toxicity",
                            "🔴 Toxic" if s["is_toxic"] else "🟢 Clean"
                        )

                except Exception as e:
                    st.error(str(e))


# =========================
# 🔹 TAB 2: LOGS
# =========================
with tab2:
    st.subheader("Logs")

    page = st.number_input("Page", 1, 100, 1)
    page_size = st.selectbox("Page size", [10, 20, 50], 1)

    try:
        r = httpx.get(
            f"{API}/logs",
            params={"page": page, "page_size": page_size},
        )
        r.raise_for_status()
        data = r.json()

        st.write(f"Total: {data['total']}")

        for item in data["items"]:
            with st.expander(item["prompt"][:80]):
                st.write("Response:", item["response"])
                st.write("Score:", item["overall_score"])
                st.write("Latency:", item["latency_ms"])

    except Exception as e:
        st.error(str(e))


# =========================
# 🔹 TAB 3: METRICS
# =========================
with tab3:
    st.subheader("Metrics")

    try:
        r = httpx.get(f"{API}/metrics")
        r.raise_for_status()
        m = r.json()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", m["total_evaluations"])
        col2.metric("Avg Score", f"{m['avg_overall_score']:.1f}")
        col3.metric("Avg Latency", f"{m['avg_latency_ms']:.0f}")

        st.write("Toxic Rate:", f"{m['toxic_rate']*100:.1f}%")

        df = pd.DataFrame.from_dict(
            m["score_distribution"],
            orient="index",
            columns=["count"]
        )
        st.bar_chart(df)

    except Exception as e:
        st.error(str(e))
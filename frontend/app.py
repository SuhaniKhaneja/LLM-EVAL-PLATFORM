
import os

import httpx
import pandas as pd
import streamlit as st

API_URL = os.getenv(
    "API_URL",
    "https://llm-eval-platform-lfg1.onrender.com",
).rstrip("/")
API = f"{API_URL}/api/v1"

st.set_page_config(
    page_title="LLM Evaluation Platform",
    layout="wide",
)

st.title("LLM Evaluation Platform")
st.caption(
    "Evaluate LLM responses using reference-based metrics, "
    "length scoring, and toxicity checks."
)


def api_get(path: str, params: dict | None = None) -> dict:
    response = httpx.get(
        f"{API}{path}",
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def show_optional_score(label: str, value: float | None) -> None:
    st.metric(
        label,
        "N/A" if value is None else f"{value:.4f}",
    )


# Check backend availability
try:
    health_response = httpx.get(
        f"{API_URL}/health",
        timeout=10,
    )
    health_response.raise_for_status()
except httpx.HTTPError:
    st.warning(
        "The backend is unavailable or waking up. "
        "Please wait briefly and refresh."
    )
    st.stop()


# Dashboard tabs
tab1, tab2, tab3 = st.tabs(
    ["Evaluate", "Logs", "Metrics"]
)


# TAB 1: EVALUATE
with tab1:
    st.subheader("Evaluate a response")

    prompt = st.text_area(
        "Prompt",
        height=120,
        placeholder="Enter the prompt you want the model to answer...",
    )

    reference = st.text_area(
        "Reference answer (optional)",
        height=100,
        placeholder="Enter an expected answer for ROUGE and BLEU scoring...",
        help=(
            "Leave this empty if you do not have a reference answer. "
            "Reference-based metrics will then be unavailable."
        ),
    )

    max_tokens = st.slider(
        "Maximum response tokens",
        min_value=64,
        max_value=2048,
        value=512,
        step=64,
    )

    if st.button("Run evaluation", type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt before running evaluation.")
        else:
            with st.spinner("Generating and evaluating response..."):
                try:
                    response = httpx.post(
                        f"{API}/evaluate",
                        json={
                            "prompt": prompt.strip(),
                            "reference": reference.strip(),
                            "max_tokens": max_tokens,
                        },
                        timeout=90,
                    )
                    response.raise_for_status()
                    data = response.json()
                    scores = data["scores"]

                    st.subheader("Model response")
                    st.write(data["response"])

                    st.caption(
                        f"Model: {data['model']} | "
                        f"Latency: {data['latency_ms']:.0f} ms | "
                        f"Prompt tokens: {data['prompt_tokens']} | "
                        f"Completion tokens: {data['completion_tokens']}"
                    )

                    st.subheader("Evaluation scores")

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Overall score",
                        f"{scores['overall_score']:.2f}/100",
                    )
                    col2.metric(
                        "Length score",
                        f"{scores['length_score']:.4f}",
                    )
                    col3.metric(
                        "Toxicity status",
                        "Flagged" if scores["is_toxic"] else "Not flagged",
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        show_optional_score(
                            "ROUGE-1 F1",
                            scores.get("rouge1_score"),
                        )

                    with col2:
                        show_optional_score(
                            "ROUGE-L F1",
                            scores.get("rouge_l_score"),
                        )

                    with col3:
                        show_optional_score(
                            "BLEU",
                            scores.get("bleu_score"),
                        )

                    st.caption(
                        "ROUGE and BLEU measure text overlap with the "
                        "reference answer. They do not establish factual "
                        "or semantic correctness. Toxicity detection is heuristic."
                    )

                except httpx.HTTPStatusError as exc:
                    st.error(
                        f"API error ({exc.response.status_code}): "
                        f"{exc.response.text[:1000]}"
                    )

                except httpx.HTTPError as exc:
                    st.error(f"Could not connect to the API: {exc}")

                except (KeyError, ValueError) as exc:
                    st.error(f"Unexpected API response: {exc}")


# TAB 2: LOGS
with tab2:
    st.subheader("Evaluation logs")

    col1, col2 = st.columns(2)

    with col1:
        page = st.number_input(
            "Page",
            min_value=1,
            max_value=10000,
            value=1,
            step=1,
        )

    with col2:
        page_size = st.selectbox(
            "Results per page",
            [10, 20, 50],
            index=0,
        )

    if st.button("Refresh logs"):
        st.rerun()

    try:
        logs = api_get(
            "/logs",
            {
                "page": int(page),
                "page_size": page_size,
            },
        )

        st.write(f"Total evaluations: {logs['total']}")

        if not logs["items"]:
            st.info("No evaluations found on this page.")

        for item in logs["items"]:
            title = (
                item["prompt"].replace("\n", " ")[:80]
                or "Empty prompt"
            )

            with st.expander(title):
                st.markdown("**Prompt**")
                st.write(item["prompt"])

                st.markdown("**Response**")
                st.write(item["response"])

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Overall score",
                    f"{item['overall_score']:.2f}/100",
                )
                col2.metric(
                    "Latency",
                    f"{item['latency_ms']:.0f} ms",
                )
                col3.metric(
                    "Toxicity status",
                    "Flagged" if item["is_toxic"] else "Not flagged",
                )

                st.caption(
                    f"Model: {item['model']} | "
                    f"Created: {item['created_at']}"
                )

    except httpx.HTTPStatusError as exc:
        st.error(
            f"Logs API error ({exc.response.status_code}): "
            f"{exc.response.text[:500]}"
        )

    except httpx.HTTPError as exc:
        st.error(f"Could not load logs: {exc}")


# TAB 3: METRICS
with tab3:
    st.subheader("Evaluation metrics")

    try:
        metrics = api_get("/metrics")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total evaluations",
            metrics["total_evaluations"],
        )
        col2.metric(
            "Average overall score",
            f"{metrics['avg_overall_score']:.2f}/100",
        )
        col3.metric(
            "Average latency",
            f"{metrics['avg_latency_ms']:.0f} ms",
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Toxic responses flagged",
            metrics["toxic_count"],
        )
        col2.metric(
            "Toxicity flag rate",
            f"{metrics['toxic_rate'] * 100:.1f}%",
        )

        st.subheader("Overall score distribution")

        distribution = metrics.get("score_distribution", {})

        if distribution:
            frame = pd.DataFrame(
                {
                    "Evaluations": list(distribution.values()),
                },
                index=list(distribution.keys()),
            )
            st.bar_chart(frame)
        else:
            st.info("No score distribution data available.")

        st.metric(
            "Average ROUGE-1 F1",
            f"{metrics['avg_rouge1']:.4f}",
        )

        st.caption(
            "Scores are evaluation signals, not definitive measures "
            "of answer quality. Text-overlap scores alone do not measure "
            "semantic correctness, and toxicity detection is heuristic."
        )

    except httpx.HTTPStatusError as exc:
        st.error(
            f"Metrics API error ({exc.response.status_code}): "
            f"{exc.response.text[:500]}"
        )

    except httpx.HTTPError as exc:
        st.error(f"Could not load metrics: {exc}")

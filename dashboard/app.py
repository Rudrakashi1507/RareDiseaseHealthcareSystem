import streamlit as st
import requests
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Rare Disease Healthcare Intelligence",
    page_icon="🏥",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"


# -----------------------------
# Header
# -----------------------------

st.title("🏥 Rare Disease Analysis and Healthcare Intelligence System")

st.write(
    "Healthcare analytics and rare disease information platform."
)
st.sidebar.header("🔎 Filters")

try:
    filter_response = requests.get(
        f"{API_URL}/analytics",
        timeout=10
    )

    filter_data = filter_response.json()

    type_options = [
        item["type"]
        for item in filter_data["disorder_types"]
        if item["type"]
    ]

    group_options = [
        item["group"]
        for item in filter_data["disorder_groups"]
        if item["group"]
    ]

except Exception:
    type_options = []
    group_options = []


selected_type = st.sidebar.selectbox(
    "Disorder Type",
    ["All"] + type_options
)

selected_group = st.sidebar.selectbox(
    "Disease Group",
    ["All"] + group_options
)

# -----------------------------
# Dashboard Statistics
# -----------------------------

try:
    response = requests.get(
        f"{API_URL}/diseases/count",
        timeout=5
    )

    total_diseases = response.json()["total_diseases"]

except Exception:
    total_diseases = 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Rare Diseases", f"{total_diseases:,}")

with col2:
    st.metric("Data Source", "PostgreSQL")

with col3:
    st.metric("Backend", "FastAPI")

with col4:
    st.metric("Dashboard", "Streamlit")


st.divider()


# -----------------------------
# Disease Search
# -----------------------------

st.subheader("🔎 Rare Disease Search")

search = st.text_input(
    "Search by Disease Name, OrphaCode or GARD ID",
    placeholder="Example: Cystic"
)

if search:

    try:
        response = requests.get(
            f"{API_URL}/diseases/search",
            params={
                "q": search,
                "disorder_type": selected_type,
                "disorder_group": selected_group
            },
            timeout=10
        )

        if response.status_code == 200:

            results = response.json()

            st.write(
                f"### {len(results)} result(s) found"
            )

            if results:

                # -------------------------
                # Search Results Table
                # -------------------------

                display_data = []

                for item in results:

                    display_data.append({
                        "OrphaCode": item.get("orpha_code"),
                        "Disease Name": (
                            item.get("name")
                            or item.get("disease_name")
                        ),
                        "Disorder Type": item.get(
                            "disorder_type"
                        ),
                        "Disease Group": item.get(
                            "disorder_group"
                        ),
                        "Age of Onset": item.get(
                            "age_of_onset"
                        ),
                        "Type of Inheritance": item.get(
                            "type_of_inheritance"
                        )
                    })

                display_df = pd.DataFrame(
                    display_data
                )

                st.dataframe(
                    display_df,
                    width="stretch",
                    hide_index=True
                )

                # -------------------------
                # Disease Details
                # -------------------------

                st.markdown(
                    "### 🧬 Disease Details"
                )

                disease_names = [
                    item.get("name")
                    or item.get("disease_name")
                    for item in results
                ]

                selected_disease = st.selectbox(
                    "Select a disease to view details",
                    disease_names
                )

                for item in results:

                    disease_name = (
                        item.get("name")
                        or item.get("disease_name")
                    )

                    if disease_name == selected_disease:

                        col1, col2 = st.columns(2)

                        # -------------------------
                        # Basic Information
                        # -------------------------

                        with col1:

                            st.write(
                                "**OrphaCode:**",
                                item.get("orpha_code")
                            )

                            st.write(
                                "**Disorder Type:**",
                                item.get(
                                    "disorder_type"
                                )
                            )

                            st.write(
                                "**Disease Group:**",
                                item.get(
                                    "disorder_group"
                                )
                            )

                        # -------------------------
                        # Disease Identifiers
                        # -------------------------

                        with col2:

                            st.write(
                                "**Age of Onset:**",
                                item.get(
                                    "age_of_onset"
                                )
                            )

                            st.write(
                                "**Type of Inheritance:**",
                                item.get(
                                    "type_of_inheritance"
                                )
                            )

                            st.write(
                                "**ICD-10:**",
                                item.get("icd_10")
                            )

                            st.write(
                                "**ICD-11:**",
                                item.get("icd_11")
                            )

                            st.write(
                                "**MONDO:**",
                                item.get("mondo")
                            )

                            st.write(
                                "**OMIM:**",
                                item.get("omim")
                            )

                            st.write(
                                "**UMLS:**",
                                item.get("umls")
                            )

                            st.write(
                                "**GARD:**",
                                item.get("gard")
                            )

                        # -------------------------
                        # Similar Diseases
                        # -------------------------

                        st.markdown(
                            "### 🔗 Similar Diseases"
                        )

                        similar_response = requests.get(
                            f"{API_URL}/ml/similar-diseases",
                            params={
                                "orpha_code": item.get(
                                    "orpha_code"
                                )
                            },
                            timeout=10
                        )

                        if (
                            similar_response.status_code
                            == 200
                        ):

                            similar_data = (
                                similar_response.json()
                            )

                            similar_diseases = (
                                similar_data.get(
                                    "similar_diseases",
                                    []
                                )
                            )

                            if similar_diseases:

                                similar_display = []

                                for disease in (
                                    similar_diseases
                                ):

                                    similar_display.append({
                                        "OrphaCode":
                                            disease.get(
                                                "orpha_code"
                                            ),
                                        "Disease Name":
                                            disease.get(
                                                "name"
                                            ),
                                        "Disorder Type":
                                            disease.get(
                                                "disorder_type"
                                            ),
                                        "Disease Group":
                                            disease.get(
                                                "disorder_group"
                                            ),
                                        "Age of Onset":
                                            disease.get(
                                                "age_of_onset"
                                            ),
                                        "Inheritance":
                                            disease.get(
                                                "type_of_inheritance"
                                            )
                                    })

                                similar_df = pd.DataFrame(
                                    similar_display
                                )

                                st.dataframe(
                                    similar_df,
                                    width="stretch",
                                    hide_index=True
                                )

                            else:

                                st.info(
                                    "No similar diseases found."
                                )

                        else:

                            st.warning(
                                "Unable to load similar diseases."
                            )

                        break

            else:

                st.info(
                    "No diseases found."
                )

        else:

            st.error(
                "Search API request failed."
            )

    except Exception as e:

        st.error(
            f"Could not connect to FastAPI: {e}"
        )

else:

    st.info(
        "Enter a disease name, OrphaCode or GARD ID to search."
    )

st.divider()


# -----------------------------
# Disease Analytics
# -----------------------------

st.subheader("📊 Disease Analytics")
st.markdown("### 📈 Disease Distribution")

try:

    analytics_response = requests.get(
        f"{API_URL}/analytics",
        timeout=10
    )

    if analytics_response.status_code == 200:

        analytics = analytics_response.json()

        # -------------------------
        # Disease Type Distribution
        # -------------------------

        type_data = analytics["disorder_types"]

        if type_data:

            type_df = pd.DataFrame(type_data)

            fig_type = px.bar(
                type_df,
                x="type",
                y="count",
                title="Disease Type Distribution",
                labels={
                    "type": "Disorder Type",
                    "count": "Number of Diseases"
                }
            )

            st.plotly_chart(
                fig_type,
                width="stretch"
            )

        # -------------------------
        # Age of Onset Distribution
        # -------------------------

        age_response = requests.get(
            f"{API_URL}/analytics/age-onset",
            timeout=10
        )

        if age_response.status_code == 200:

            age_data = age_response.json()

            if age_data:

                age_df = pd.DataFrame(
                    age_data
                ).head(10)

                fig_age = px.bar(
                    age_df,
                    x="age_of_onset",
                    y="count",
                    title="Top 10 Age of Onset Categories",
                    labels={
                        "age_of_onset": "Age of Onset",
                        "count": "Number of Diseases"
                    }
                )

                st.plotly_chart(
                    fig_age,
                    width="stretch"
                )

        # -------------------------
        # Top Disease Groups
        # -------------------------

        group_data = analytics["disorder_groups"]

        if group_data:

            group_df = pd.DataFrame(
                group_data
            )

            fig_group = px.bar(
                group_df,
                x="group",
                y="count",
                title="Top Disease Groups",
                labels={
                    "group": "Disease Group",
                    "count": "Number of Diseases"
                }
            )

            st.plotly_chart(
                fig_group,
                width="stretch"
            )

        # -------------------------
        # ML Disease Clusters
        # -------------------------

        st.markdown(
            "### 🤖 Disease Clustering Analysis"
        )

        cluster_response = requests.get(
            f"{API_URL}/ml/clusters",
            timeout=10
        )

        if cluster_response.status_code == 200:

            cluster_data = cluster_response.json()

            cluster_df = pd.DataFrame(
                cluster_data["clusters"]
            )

            fig_cluster = px.bar(
                cluster_df,
                x="cluster",
                y="count",
                title="Rare Disease Clusters",
                labels={
                    "cluster": "Cluster",
                    "count": "Number of Diseases"
                }
            )

            st.plotly_chart(
                fig_cluster,
                width="stretch"
            )

        else:

            st.error(
                "Unable to load ML cluster data."
            )

        # -------------------------
        # Cluster Characteristics
        # -------------------------

        st.markdown(
            "### 📋 Cluster Characteristics"
        )

        summary_response = requests.get(
            f"{API_URL}/ml/cluster-summary",
            timeout=10
        )

        if summary_response.status_code == 200:

            summary_data = summary_response.json()

            summary_df = pd.DataFrame(
                summary_data["clusters"]
            )

            summary_df.columns = [
                "Cluster",
                "Disease Count",
                "Common Disorder Type",
                "Common Disorder Group",
                "Common Age of Onset",
                "Common Inheritance"
            ]

            st.dataframe(
                summary_df,
                width="stretch",
                hide_index=True
            )

        else:

            st.error(
                "Unable to load cluster summary."
            )

    else:

        st.error(
            "Unable to load analytics."
        )

except Exception as e:

    st.error(
        f"Analytics error: {e}"
    )

st.divider()
# -----------------------------
# Disclaimer
# -----------------------------

st.caption(
    "Healthcare analytics and decision-support system — "
    "not intended for medical diagnosis."
)
import streamlit as st
import pandas as pd
import numpy as np
from matplotlib.pyplot import subplots
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px

YEARS = (2022, 2023)
REGIONS = ("Global", "Arab States", "East Asia / Pacific",
                        "Europe / Central Asia", "Latin America / Caribbean", "South Asia",
                        "Sub Saharan Africa")

st.set_page_config(page_title= "MPI", layout= "wide")
st.title("Multi-dimensional Poverty Index")

st.sidebar.header("Choose the year and regions")

year_box = st.sidebar.selectbox(
    "Selected Year", YEARS
)
   
region_box = st.sidebar.selectbox(
    "Selected Region", REGIONS
)



region_mapper = {
    "Global": "global",
    "Arab States": "arab_states",
    "East Asia / Pacific": "east_asia_and_the_pacific",
    "Europe / Central Asia": "europe_and_central_asia",
    "Latin America / Caribbean": "latin_america_and_the_caribbean",
    "South Asia": "south_asia",
    "Sub Saharan Africa": "sub_saharan_africa"
}

df = pd.read_csv(f"./data/interm/{region_mapper[region_box]}_{year_box}.csv", index_col= 0)
mpi_total = df["Health_w"].sum() + df["Education_w"].sum() + df["Living Standards_w"].sum()

st.header(f"{region_box} MPI Data ({year_box})")
st.subheader(f"Overview: {round(mpi_total, 3)}")
col1, col2 = st.columns(2)

with col1:
    pie_labs = ["Health", "Education", "Living Standards"]
    pie_vals = [df["Health_w"].sum(), df["Education_w"].sum(), df["Living Standards_w"].sum()]
    gen_colors = ["#763028", "#c1b0b4", "#2f4a5b"]
        
    st.subheader(f"")
    fig, ax = subplots(figsize = (4,4))
    ax.pie(pie_vals, labels= pie_labs, colors= gen_colors, wedgeprops=dict(width=0.5))
    st.pyplot(fig, )

with col2:
    mpi_boxplot = px.box(df, x= "MPI", hover_data = "Country")
    fig, ax = subplots(figsize = (10,5))
    sns.boxplot(x= df["MPI"], ax= ax)
    st.pyplot(fig)

st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    health_button = st.checkbox("Health", True, "health")
with col2:
    education_button = st.checkbox("Education", True, "education")
with col3:
    ls_button = st.checkbox("Living Standards", True, "ls")

if health_button or education_button or ls_button:
    selected_cols = ["Country"]
    col_colors = []
    if health_button:
        selected_cols.extend(["Nutrition", "Child Mortality"])
        col_colors.extend(["#962c20", "#642524"])
        
    if education_button:
        selected_cols.extend(["Years of Schooling", "School Attendance"])
        col_colors.extend(["#c5a9ab", "#997a77"])

    if ls_button:
        selected_cols.extend(["Cooking Fuel", "Sanitation", "Drinking Water", "Electricity", "Housing", "Assets"])
        col_colors.extend(["#acc6d6", "#7d9eb3", "#5d8099", "#416682", "#154b66", "#003650"])

    if health_button and education_button and ls_button:
        selected_cols = ["Country", "Health", "Education", "Living Standards"]
        col_colors = ["#763028", "#c1b0b4", "#2f4a5b"]

    sub_df = df[selected_cols].set_index("Country")

else:
    st.markdown("Please select a category above.")
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Countries with the largest ___")
    idx = sub_df.sum(axis= 1).nlargest(5).index
    idx_list = list(idx)[::-1]
    fig, ax = subplots(figsize= (10,6))
    sub_df.loc[idx_list].plot(kind="barh", stacked= True, ax= ax, color= col_colors, legend= False)
    st.pyplot(fig)

with col2:
    st.subheader("Countries with the smallest MPIs")
    idx = sub_df.sum(axis= 1).nsmallest(5).index
    idx_list = list(idx)[::-1]
    fig, ax = subplots(figsize= (10,6))
    sub_df.loc[idx_list].plot(kind="barh", stacked= True, ax= ax, color= col_colors)
    st.pyplot(fig)

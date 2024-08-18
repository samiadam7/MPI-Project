import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# plotting styles    
legend_dict = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1)

# sidebar choices
SECTIONS = ("Dashboard", "Overview")
YEARS = (2020, 2021, 2022, 2023)[::-1]
REGIONS = ("Global", "Arab States", "East Asia / Pacific",
                        "Europe / Central Asia", "Latin America / Caribbean", "South Asia",
                        "Sub Saharan Africa")

# maps
region_mapper = {
    "Global": "global",
    "Arab States": "arab_states",
    "East Asia / Pacific": "east_asia_and_the_pacific",
    "Europe / Central Asia": "europe_and_central_asia",
    "Latin America / Caribbean": "latin_america_and_the_caribbean",
    "South Asia": "south_asia",
    "Sub Saharan Africa": "sub_saharan_africa"
}

st.set_page_config(page_title= "MPI", layout= "wide")

section_box = st.sidebar.selectbox("", SECTIONS)

mpi_description = """

The Multidimensional Poverty Index (MPI) is a comprehensive measure of poverty that goes beyond traditional income-based metrics. 
Developed by the Oxford Poverty and Human Development Initiative and the United Nations Development Programme, 
the MPI captures the complex nature of poverty by considering multiple deprivations experienced by individuals or households.
It assesses poverty across three key dimensions: health, education, and standard of living.
Within these dimensions, ten indicators are evaluated, including nutrition, child mortality, years of schooling,
school attendance, cooking fuel, sanitation, drinking water, electricity, housing, and assets.
By aggregating these factors, the MPI provides a more nuanced understanding of poverty,
allowing policymakers and researchers to identify not only who is poor but also how they are poor.
This approach enables more targeted and effective poverty reduction strategies across different regions and populations.

The MPI's importance extends beyond its complementary role to monetary poverty measures and its ability to enable cross-group comparisons.
By providing a more holistic view of poverty, the MPI allows policymakers and development organizations to design more effective and targeted interventions.
It highlights specific areas of deprivation within communities, which can guide resource allocation and policy formulation. 
For instance, if an area shows high deprivation in education but less in health, resources can be directed towards improving educational access and quality.
Furthermore, the MPI's multidimensional approach aligns more closely with the complex reality of poverty as experienced by individuals,
recognizing that poverty is not just about lack of income, but also about limited access to essential services and opportunities.
This comprehensive perspective is crucial for achieving sustainable development goals and ensuring that no one is left behind in poverty reduction efforts.

"""

mpi_scoring = """

## MPI Scoring and Sub-component Descriptions

Health dimension indicators:

- Nutrition: Examines whether any adult under 70 years of age or any child is undernourished.
- Child mortality: Considers whether any child has died in the family in the five-year period preceding the survey.

Education dimension indicators:

- Years of schooling: Looks at whether no household member aged 10 years or older has completed six years of schooling.
- School attendance: Considers whether any school-aged child is not attending school up to the age at which they would complete class 8.

Living standards dimension indicators:

- Cooking fuel: Whether the household cooks with dung, wood, charcoal, or coal.
- Sanitation: If the household's sanitation facility is not improved or it is improved but shared with other households.
- Drinking water: If the household does not have access to safe drinking water or safe water is more than a 30-minute walk from home.
- Electricity: Whether the household has no electricity.
- Housing: If at least one of the three housing materials for roof, walls, and floor are inadequate.
- Assets: If the household does not own more than one of these assets: radio, TV, telephone, computer, animal cart, bicycle, motorbike, or refrigerator, and does not own a car or truck.

The scoring of these metrics involves:

- Indicator Thresholds: Each indicator has a specific threshold determining household deprivation.
- Weighting: The three dimensions are equally weighted (1/3 each). Within dimensions, indicators are also equally weighted.
- Deprivation Score: Calculated for each household by summing weighted deprivations.
- Poverty Cut-off: A household is considered multidimensionally poor if its deprivation score is 1/3 (33.33%) or higher.
- Intensity of Poverty: For poor households, calculated as the average deprivation score.
- MPI Calculation: Multiply the proportion of poor people by the average intensity of poverty.

This scoring method provides a comprehensive view of poverty, capturing both incidence and intensity. The MPI score ranges from 0 to 1, with **higher values** indicating greater poverty. 
This approach allows for targeted interventions and more effective policy formulation in addressing specific areas of deprivation within communities.



"""

if section_box == "Overview":
    st.title("Multi-Dimensional Poverty Index Overview")
    st.markdown(mpi_description)
    
    with st.columns(6)[1]:
        st.image("assets/mpi_desciption_graph.png", "MPI Metric Breakdown", width= 600)
        
    st.markdown(mpi_scoring)
    

if section_box == "Dashboard":
    st.title("Multi-Dimensional Poverty Index Dashboard")

    st.sidebar.header("Choose the year and regions")

    year_box = st.sidebar.selectbox(
        "Selected Year", YEARS)
    region_box = st.sidebar.selectbox(
        "Selected Region", REGIONS)

    df = pd.read_csv(f"./data/interm/{region_mapper[region_box]}_{year_box}.csv", index_col= 0)

    successful_dfs = {}

    try:
        for i, year in enumerate([year_box-1, year_box-2, year_box-3], start=1):
            df_name = f"df_{i}"
            file_path = f"./data/interm/{region_mapper[region_box]}_{year}.csv"
            successful_dfs[year] = pd.read_csv(file_path, index_col=0)
            

    except Exception as e:
        failed_years = [year_box-1, year_box-2, year_box-3]
        for year in successful_dfs.keys():
            failed_years.remove(year)
        
        if failed_years:
            st.text(f"Missing data for year(s): {', '.join(map(str, failed_years))}")

    curr_mpi_total = df["Health_w"].sum() + df["Education_w"].sum() + df["Living Standards_w"].sum()

    st.header(f"{region_box} MPI Data ({year_box})")
    col1, col2, col3, col4 = st.columns(4)
    try:
        with col1:
            prev_year_mpi_total = (successful_dfs[year_box-1]["Health_w"].sum() + 
                                successful_dfs[year_box-1]["Education_w"].sum() + successful_dfs[year_box-1]["Living Standards_w"].sum())
            st.metric(label= "MPI", value= round(curr_mpi_total, 3),
                    delta = f"{round((curr_mpi_total - prev_year_mpi_total)/curr_mpi_total * 100, 1)}%", delta_color= "inverse")
            
        column_vals = ["Health_w", "Education_w", "Living Standards_w"]
        for i, val in enumerate(column_vals, start=2):
            with globals()[f"col{i}"]:
                curr_val = df[val].sum()
                prev_year_val = successful_dfs[year_box-1][val].sum()
                st.metric(label= val.split("_")[0], value= round(curr_val, 3),
                        delta = f"{round((curr_val - prev_year_val)/prev_year_val * 100, 1)}%", delta_color= "inverse")

    except:
        with col1:
            st.metric(label= "Health", value= round(curr_mpi_total, 3))
        
        column_vals = ["Health_w", "Education_w", "Living Standards_w"]
        for i, val in enumerate(column_vals):
            with globals()[f"col{i+2}"]:
                curr_val = df[val].sum()
                st.metric(label= val.split("_")[0], value= round(curr_val, 3))


    st.divider()
    
    gen_colors = ["#c1b0b4", "#763028", "#2f4a5b"]    
    all_dfs = [df]
    all_dfs.extend(list(successful_dfs.values()))

    merged_df = pd.DataFrame({"Health": [df["Health_w"].sum() for df in all_dfs],
                        "Education": [df["Education_w"].sum() for df in all_dfs],
                        "Living Standards":[df["Living Standards_w"].sum() for df in all_dfs],
                        "Year":[year_box - i for i in range(len((successful_dfs.keys())) + 1)]})

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("MPI Distribution")
        mpi_hist = px.histogram(df, x= "MPI", nbins= 20, color_discrete_sequence= ["#2f4a5b"])
        st.plotly_chart(mpi_hist, use_container_width= True)
        
    with col2:
        st.subheader("MPI Over Time")
        over_time_chart = px.line(merged_df, x= "Year", y= ["Health", "Education", "Living Standards"], color_discrete_sequence= gen_colors,
                                markers= True)
        
        over_time_chart.update_layout(
            xaxis = dict(
                tickmode = 'array',
                tickvals = [year_box - i for i in range(len((successful_dfs.keys())) + 1)]
            ),
            legend= legend_dict
        )
        st.plotly_chart(over_time_chart, use_container_width= True)

    st.divider()
    st.markdown("""
                ### Score Comparison
                """
                )
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

        sub_df = df[selected_cols]

    col1, col2 = st.columns(2)

    try:
        with col1:
            idx = sub_df.drop(columns="Country").sum(axis= 1).nlargest(5).index
            idx_list = list(idx)[::-1]
            sub_df_l = sub_df.loc[idx_list]
            largest_chart = px.bar(sub_df_l, y= "Country", x= selected_cols, color_discrete_sequence= col_colors)
            largest_chart.update_layout(legend= legend_dict)
            largest_chart.update_traces(width= 0.6)
            
            st.markdown("#### Countries with the largest scores")
            st.plotly_chart(largest_chart, use_container_width= True)

        with col2:
            idx = sub_df.drop(columns="Country").sum(axis= 1).nsmallest(5).index
            idx_list = list(idx)[::-1]
            sub_df_s = sub_df.loc[idx_list]
            smallest_chart = px.bar(sub_df_s, y= "Country", x= selected_cols, color_discrete_sequence= col_colors)
            smallest_chart.update_layout(legend= legend_dict)
            smallest_chart.update_traces(width= 0.6)
            
            st.markdown("#### Countries with the smallest scores")
            st.plotly_chart(smallest_chart, use_container_width= True, height= 100)
        

    except:
        st.markdown("Please select a category above.")
        
    st.divider()


    st.markdown("### Country Lookup")
    country_lookup = st.multiselect("Choose the countries and dimensions of interest", options= df["Country"], default= df["Country"].values[0])

    col1, col2, col3 = st.columns(3)
    with col1:
        health_button = st.checkbox("Health", True, "health_2")
    with col2:
        education_button = st.checkbox("Education", True, "education_2")
    with col3:
        ls_button = st.checkbox("Living Standards", True, "ls_2")

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

        sub_df = df[selected_cols].copy()
        
    if country_lookup:
        country_dfs = []
        for i, df in enumerate(all_dfs):
            country = df.loc[df["Country"].isin(country_lookup)].copy()
            country["Year"] = year_box - i
            country_dfs.append(country)
        
        merged_countries_years_df = pd.concat(country_dfs, axis=0, ignore_index=True)
        prev_year = merged_countries_years_df.loc[merged_countries_years_df["Year"] == year_box - 1]
        
        if len(country_lookup) == 1:
            st.markdown("#### MPI Tracker")
            tracker_cols = ["Country", "Health", "Education", "Living Standards"]
            country = df[tracker_cols].loc[df[tracker_cols]["Country"].isin(country_lookup)]
            metrics = ["MPI", "Health", "Education", "Living Standards"]
            col1, col2, col3, col4 = st.columns(4)
            
            for i, metric in enumerate(metrics, 1):
                with globals()[f"col{i}"]:
                    if metric == "MPI":
                        current_val = country[metrics[1:]].sum(axis= 1).values[0]
                        try:
                            prev_val = prev_year[metrics[1:]].sum(axis= 1).values[0]
                            delta = round((current_val - prev_val) / prev_val * 100, 2)
                            st.metric(metric, round(current_val, 3), f"{delta} %", "inverse")
                        except:
                            st.metric(metric, round(current_val, 3))
                    else:
                        current_val = country[metric].values[0]
                        try:
                            prev_val = prev_year[metric].values[0]
                            delta = round((current_val - prev_val) / prev_val * 100, 2)
                            st.metric(metric, round(current_val, 3), f"{delta} %", "inverse")
                        except:
                            st.metric(metric, round(current_val, 3))
                            
            st.markdown(f"#### MPI Over Time")
            
            over_time_chart = px.line(merged_countries_years_df, x= "Year", y= selected_cols[1:], color_discrete_sequence= col_colors,
                        markers= True)
            
            over_time_chart.update_layout(
                xaxis = dict(
                    tickmode = 'array',
                    tickvals = [year_box - i for i in range(len((successful_dfs.keys())) + 1)]
                ),
                legend= legend_dict
            )
            st.plotly_chart(over_time_chart, use_container_width= True)
        
        else:
            
            col1, col2= st.columns(2)
            
            with col1:
                st.markdown("#### MPI Over Time")
                
                over_time_comp_chart = px.line(merged_countries_years_df, x= "Year", y= "MPI", color= "Country", color_discrete_sequence = px.colors.qualitative.T10)
                over_time_comp_chart.update_layout(
                    xaxis = dict(
                        tickmode = 'array',
                        tickvals = [year_box - i for i in range(len((successful_dfs.keys())) + 1)]
                    ),
                    legend= legend_dict)
                
                st.plotly_chart(over_time_comp_chart, use_container_width= True)
            
            with col2:
                st.markdown("#### MPI Comparison")

                comp_df = sub_df.loc[sub_df["Country"].isin(country_lookup)]
                comp_graph =px.bar(comp_df, y= "Country", x= selected_cols, color_discrete_sequence = col_colors)
                comp_graph.update_layout(legend= legend_dict)
                comp_graph.update_traces(width= 0.4)
                
                st.plotly_chart(comp_graph, True)
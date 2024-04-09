import pandas as pd

def standardize(df: pd.DataFrame, x: str):
    """
    
    This function will convert the indicator values from percents to values by\
        multiplying the percents to the country's MPI

    Args:
        df (pd.DataFrame): Original DataFrame
        x (str): Column Name
    """
    df.loc[:, x] = df["Multidimensional Poverty Index\n(MPI = H*A)"] * df[x] / 100

def get_weights(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns DataFrame with weight

    Args:
        df (pd.DataFrame): Original DataFrame

    Returns:
        pd.DataFrame: DataFrame column with weighted column
    """
    total_pop = df["Population 2021"].sum()
    df.loc[:, "Weight"] = df["Population 2021"] / total_pop
    return df

def get_hels(df: pd.DataFrame):
    """"
    Creates normal and weighted Health, Education, and Living Standards columns
    """
    df.loc[:, "Health"] = df["Nutrition"] + df["Child mortality"]
    df.loc[:, "Education"] = df["Years of schooling"] + df["School attendance"]
    df.loc[:, "Living Standards"] = (df["Cooking fuel"] + df["Sanitation"] + df["Drinking water"]
                                    + df["Electricity"] + df["Housing"] + df["Assets"])

    df.loc[:, "Health_w"] = df["Nutrition_w"] + df["Child mortality_w"]
    df.loc[:, "Education_w"] = df["Years of schooling_w"] + df["School attendance_w"]
    df.loc[:, "Living Standards_w"] = (df["Cooking fuel_w"] + df["Sanitation_w"] + df["Drinking water_w"]
                                    + df["Electricity_w"] + df["Housing_w"] + df["Assets_w"])

df_1 = pd.read_excel("./data/raw/Global MPI 2023 National Results.xlsx",
                     sheet_name= "1.1 National MPI Results")
df_2 = pd.read_excel("./data/raw/Global MPI 2023 National Results.xlsx",
                     sheet_name= "1.3 Contribut'n of Deprivations")
df = pd.merge(left=df_1, right=df_2, how= "left", on="ISO\ncountry numeric code")

df = df[["Country_x", 'Multidimensional Poverty Index\n(MPI = H*A)',
       'Intensity of deprivation among the poor\n(A) ', 'Population 2021', "World region_y", 'Nutrition', 'Child mortality',
       'Years of schooling', 'School attendance', 'Cooking \nfuel',
       'Sanitation', 'Drinking water', 'Electricity', 'Housing', 'Assets']]

indicator_list = ['Nutrition', 'Child mortality',
       'Years of schooling', 'School attendance', 'Cooking \nfuel',
       'Sanitation', 'Drinking water', 'Electricity', 'Housing', 'Assets']

for x in indicator_list:
    standardize(df, x)
    
df.rename(columns={"Country_x": "Country",
                   "Headcount ratio: Population in multidimensional poverty\n(H)": "Headcount",
                                  "Intensity of deprivation among the poor\n(A) ": "Intensity",
                                  'Multidimensional Poverty Index\n(MPI = H*A)': "MPI",
                                  "World region_y": "Region",
                                  "Cooking \nfuel": "Cooking fuel"}, inplace= True)

regions = list(df["Region"].unique())
region_dfs = {}
region_dfs["Global"] = df
for region in regions:
    region_df = df[df["Region"] == region].drop(columns= "Region")
    region_dfs[region] = region_df
    
needs_weights = ['Nutrition', 'Child mortality', 'Years of schooling',
       'School attendance', 'Cooking fuel', 'Sanitation', 'Drinking water',
       'Electricity', 'Housing', 'Assets']

for region in region_dfs.keys():
    var_name = region.lower().replace(" ", "_").replace("-", "_") + "_df"
    df = get_weights(region_dfs[region])
    
    for col in needs_weights:
        col_name = col + "_w"
        df.loc[:, col_name] = df[col] * df["Weight"]


    output_filepath = f"./data/interm/{var_name}.csv"
    globals()[var_name] = df
    globals()[var_name].fillna(0).to_csv(output_filepath)
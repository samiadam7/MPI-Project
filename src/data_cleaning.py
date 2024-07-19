import os
import pandas as pd

def merge(df1: pd.DataFrame, df2: pd.DataFrame, merge_on: str, check_col: str) -> pd.DataFrame:
    """
    
    Merges df1 and df2

    Args:
        df1 (pd.DataFrame): First Excel Sheet
        df2 (pd.DataFrame): Second Excel Sheet
        merge_on (str): Column to merge on
        check_col (str): Colum to check merge

    Returns:
        pd.DataFrame: Merged Excel Sheet
    """
    
    df = pd.merge(left=df1, right= df2, how= "left", on= merge_on)
    
    if df[f"{check_col}_x"].equals(df[f"{check_col}_y"]):
        return df
    else:
        return ValueError(f"Values in the '{check_col}' column do not match after the merge.")

def standardize(df: pd.DataFrame, x: str):
    """
    
    This function will convert the indicator values from percents to values by\
        multiplying the percents to the country's MPI

    Args:
        df (pd.DataFrame): Original DataFrame
        x (str): Column Name
    """
    df.loc[:, x] = df["MPI"] * df[x] / 100

def get_region_dict(regions: list, df: pd.DataFrame) -> dict:
    """_summary_

    Args:
        regions (list): _description_
        df (pd.DataFrame): _description_

    Returns:
        dict: _description_
    """
    region_dict = {}
    for region in regions:
        region_df = df.loc[df["Region"] == region].drop(columns= "Region")
        region_dict[region] = region_df
    
    return region_dict

def get_weights(df: pd.DataFrame, pop_col: str) -> pd.DataFrame:
    """
    Returns DataFrame with population weight column

    Args:
        df (pd.DataFrame): Original DataFrame
        pop_col (str): Population Column Name

    Returns:
        pd.DataFrame: DataFrame column with weighted column
    """
    total_pop = df[pop_col].sum()
    df.loc[:, "Weight"] = df[pop_col] / total_pop
    return df

def get_weighted_cols(df: pd.DataFrame):
    """
    Creates weighted indicator columns

    Args:
        df (pd.DataFrame): DataFrame to transform
    """
    
    needs_weights = ['Nutrition', 'Child Mortality', 'Years of Schooling',
            'School Attendance', 'Cooking Fuel', 'Sanitation', 'Drinking Water',
            'Electricity', 'Housing', 'Assets']
    
    for col in needs_weights:
        col_name = col + "_w"
        df.loc[:, col_name] = df[col] * df["Weight"]
    

def get_hels(df: pd.DataFrame):
    """
    Creates normal and weighted Health, Education, and Living Standards columns

    Args:
        df (pd.DataFrame): DataFrame to transform
    """
    df.loc[:, "Health"] = df["Nutrition"] + df["Child Mortality"]
    df.loc[:, "Education"] = df["Years of Schooling"] + df["School Attendance"]
    df.loc[:, "Living Standards"] = (df["Cooking Fuel"] + df["Sanitation"] + df["Drinking Water"]
                                    + df["Electricity"] + df["Housing"] + df["Assets"])

    df.loc[:, "Health_w"] = df["Nutrition_w"] + df["Child Mortality_w"]
    df.loc[:, "Education_w"] = df["Years of Schooling_w"] + df["School Attendance_w"]
    df.loc[:, "Living Standards_w"] = (df["Cooking Fuel_w"] + df["Sanitation_w"] + df["Drinking Water_w"]
                                    + df["Electricity_w"] + df["Housing_w"] + df["Assets_w"])

def gather_dfs(year: int | list) -> dict[int, pd.DataFrame]:
    """
    Generates merged DataFrames for every year

    Args:
        year (int | list): Int or List of the year/s to gather
    
    Returns:
        dict[int, pd.DataFrame]: Dictionary containing all merged DataFrames, with years as keys
    """
    
    if isinstance(year, int):
        years = [year]
    elif isinstance(year, list):
        years = year
    
    dfs = {}
    checked = set()
    
    for year in years:
        if year not in checked:
            file_path = f"./data/raw/Global MPI {year} National Results.xlsx"
            
            if os.path.exists(file_path):
                
                col1 = ["ISO Country Numeric Code", "ISO Country Code", "Country", "Region",
                        "Survey", "Survey Year", "MPI", "Headcount", "Intensity", "Vulnerable to Poverty",
                        "Severe Poverty", "Headcount Destitution", "MPI Poor Destitute", "Poor Variance",
                        "Population YOS", f"Population {year - 3}", f"Population {year - 2}", "Poor YOS",
                        f"Poor Population {year - 3}", f"Poor Population {year - 2}", "Total Indicators",
                        "Indicator Missing"]
                
                col2 = ["ISO Country Numeric Code", "ISO Country Code", "Country", "Region", "Survey", "Year",
                        "MPI", "Health", "Education", "Living Standards", "Nutrition", "Child Mortality", "Years of Schooling",
                        "School Attendance", "Cooking Fuel", "Sanitation", "Drinking Water", "Electricity", "Housing",
                        "Assets", "Total Indicators", "Missing Indicators"]
                
                df_1 = pd.read_excel(file_path,
                        sheet_name= "1.1 National MPI Results",
                        skiprows=8, skipfooter=10, names = col1)
                df_2 = pd.read_excel(file_path,
                                sheet_name= "1.3 Contribut'n of Deprivations",
                                skiprows=8, skipfooter=3, names= col2)
                
                df = merge(df_1.fillna(0), df_2.fillna(0), "ISO Country Code", "MPI") 
                df = df[["Country_x", 'MPI_x',
                    'Intensity', f'Population {year- 2}', "Region_y", 'Nutrition', 'Child Mortality',
                    'Years of Schooling', 'School Attendance', 'Cooking Fuel',
                    'Sanitation', 'Drinking Water', 'Electricity', 'Housing', 'Assets']]
                
                df = df.rename(columns={"Country_x": "Country", "MPI_x": "MPI", "Region_y": "Region"})
                
                indicator_list = ['Nutrition', 'Child Mortality',
                'Years of Schooling', 'School Attendance', 'Cooking Fuel',
                'Sanitation', 'Drinking Water', 'Electricity', 'Housing', 'Assets']
                
                for x in indicator_list:
                    standardize(df, x)
                    
                dfs[year] = df
                checked.add(year)
            
            else:
                raise ValueError(f"{file_path} file does not exist.")
            
    return dfs

def get_regionals(year: int | list, year_dict: dict):
    """
    Creates csv files of regional information

    Args:
        year (int | list): Int or List of the year/s to gather
        year_dict (dict): Dictionary containing all the DataFrames
    """
    if isinstance(year, int):
        years = [year]
    elif isinstance(year, list):
        years = year
    checked = set()
    
    for year in years:
        if year not in checked:
            
            full_df = year_dict[year]
            regions = list(full_df["Region"].unique())
            region_dict = get_region_dict(regions, full_df)
            region_dict["Global"] = full_df
                
            for region in region_dict.keys():
                var_name = region.lower().replace(" ", "_").replace("-", "_") + f"_{year}"
                region_df = get_weights(region_dict[region], f"Population {year - 2}")
                
                get_weighted_cols(region_df)
                get_hels(region_df)
                
                output_filepath = f"./data/interm/{var_name}.csv"
                region_df.to_csv(output_filepath)


def main():
    YEARS = [2020, 2021, 2022, 2023]
    year_dfs = gather_dfs(YEARS)
    get_regionals(YEARS, year_dfs)
    

if __name__ == "__main__":
    main()
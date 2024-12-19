import pandas as pd
import plotly.express as px
import os
import configparser


# Read the configuration file
config_file = os.path.expanduser('~/code/analytics/covid/conf.ini')
config = configparser.ConfigParser()
config.read(config_file)

# Data Params
staged_datapath = config.get('Paths', 'staged_datapath')
save_trend_dir_gh = config.get('Paths', 'save_trend_dir_gh')
save_trend_filepath_gh = os.path.join(save_trend_dir_gh, 'country_trends.html')
save_trend_dir_bb = config.get('Paths', 'save_trend_dir_bb')
save_trend_filepath_bb = os.path.join(save_trend_dir_bb, 'country_trends.html')

# Load wastewater data for different countries
d1 = pd.read_parquet(os.path.join(staged_datapath, 'france_wastewater.parquet'))
d2 = pd.read_parquet(os.path.join(staged_datapath, 'sweden_wastewater.parquet'))
d3 = pd.read_parquet(os.path.join(staged_datapath, 'netherlands_wastewater.parquet'))
d4 = pd.read_parquet(os.path.join(staged_datapath, 'denmark_wastewater.parquet'))
d5 = pd.read_parquet(os.path.join(staged_datapath, 'austria_wastewater.parquet'))
d6 = pd.read_parquet(os.path.join(staged_datapath, 'poland_wastewater.parquet'))
d7 = pd.read_parquet(os.path.join(staged_datapath, 'finland_wastewater.parquet'))
d8 = pd.read_parquet(os.path.join(staged_datapath, 'switzerland_wastewater.parquet'))
d9 = pd.read_parquet(os.path.join(staged_datapath, 'canada_wastewater.parquet'))
d10 = pd.read_parquet(os.path.join(staged_datapath, 'usa_wastewater.parquet'))
d11 = pd.read_parquet(os.path.join(staged_datapath, 'newzealand_wastewater.parquet'))
d12 = pd.read_parquet(os.path.join(staged_datapath, 'germany_wastewater.parquet'))
d13 = pd.read_parquet(os.path.join(staged_datapath, 'slovenia_wastewater.parquet'))

# Concatenate DataFrames
df = pd.DataFrame(pd.concat([d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13], ignore_index=True))
df = df[['first_day', 'virus', 'region', 'cntr_code', 'cntr_nm', 'value']]
df['virus'].fillna('sars-cov-2', inplace=True)

df_sars = df.loc[df['virus'] == 'sars-cov-2']
df_sars.sort_values(by=['first_day', 'cntr_nm', 'region'], inplace=True)
df_sars = df_sars.groupby(['first_day', 'cntr_nm', 'region'])['value'].mean().reset_index()

print(df_sars.duplicated().sum())
df_sars.drop_duplicates(inplace=True)
print(df_sars.duplicated().sum())


df_all = df = df.groupby(['first_day', 'virus','cntr_nm'])['value'].agg('mean').reset_index()
df_all.drop_duplicates(inplace=True)
df_all.sort_values(by=['first_day', 'virus', 'cntr_nm'], inplace=True)


files_to_remove = [save_trend_filepath_bb, save_trend_filepath_gh]
for file in files_to_remove:
    trend_html_filepath = file

    try:
        os.remove(trend_html_filepath)
        print(trend_html_filepath, 'removed')
    except FileNotFoundError:
        print(trend_html_filepath, 'does not exist')
    except Exception as e:
        print(f"An error occurred: {e}")


def create_figures(df_sars, df_all):
    country_list = sorted(df_all['cntr_nm'].unique())
    print('country order:', country_list)
    
    # Collect HTML snippets for figures
    html_snippets = []

    for country in country_list:
        country_nm = country.title()
        
        # Filter for SARS-CoV-2 data
        df_region_sars = df_sars[df_sars['cntr_nm'] == country]
        df_country_all = df[(df['cntr_nm'] == country)]

        current_fig = px.line(df_region_sars, x="first_day", y="value", color='region',
                               title=f'{country_nm} Wastewater Sars-Cov-2 by Region')
        
        current_fig.show()
        
        html_snippets.append(current_fig.to_html(full_html=False, include_plotlyjs='cdn'))

        if df_country_all.virus.nunique() > 1:
            multivirus_fig = px.bar(df_country_all, x="first_day", y="value",
                                    color='virus',
                                    title=f'{country_nm} Virus Types in Wastewater',
                                    barmode='stack')
            multivirus_fig.show()
            
            html_snippets.append(multivirus_fig.to_html(full_html=False, include_plotlyjs='cdn'))

    # Write all collected HTML snippets to files
    with open(trend_html_filepath, 'a') as f:
        f.write("\n".join(html_snippets))

    with open(save_trend_filepath_bb, 'a') as f:
        f.write("\n".join(html_snippets))

create_figures(df_sars, df_all)

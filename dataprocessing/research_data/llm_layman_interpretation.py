import ollama
import pandas as pd
import configparser
from datetime import datetime as dt
from datetime import timedelta

config_file = '/home/stratega/code/analytics/covid/conf.ini'
n_days_back_to_include = 30 # research from latest 30 days
n_articles_to_write_to_publish = 4

# Read the Conf file
config = configparser.ConfigParser()
config.read(config_file)

# Paths
existing_research_articles = config.get('Paths', 'existing_research_articles')
selected_research_articles = config.get('Paths', 'selected_research_articles')

selected_research_articles
html_dir_gh = config.get('Paths', 'html_savedir_gh')
html_dir_bb = config.get('Paths', 'html_savedir_gh')

df = pd.read_json(existing_research_articles)
date_threshold = pd.to_datetime(dt.now()) - pd.DateOffset(days=n_days_back_to_include)
df['publication_date_dt'] = pd.to_datetime(df['publication_date'])
df = df[df['publication_date_dt'] > date_threshold]
df.drop(columns=['publication_date_dt'], inplace=True)
df
#df[df['article_title']=='COVID-19 vaccines and beyond'].needs_ai_processing
df.sort_values(by='publication_date',ascending=False, inplace=True)
df.reset_index(inplace=True)

#df.loc[df.index < n_articles_to_write_to_publish, 'needs_ai_processing'] = 1

df


#df.needs_ai_processing=1 # Needing to reparse stuff


# Make sure all columns needed are present
columns_to_check = ['layman_title', 'layman_abstract', 'needs_ai_processing']
if any(col not in df.columns for col in columns_to_check):
    print('WARNING: At least one column does not exist. Recreating  & Processing All!')
    df.loc[:, 'layman_title'] = ''
    df.loc[:, 'layman_abstract'] = ''
    df.loc[:, 'needs_ai_processing'] = 1

else:
    print('OK - all cols present.')


#df = df.head(2) # Testing. Runs slow because LLM requires much time

for index, row in df.iterrows():
    article_title = df['article_title'][index]
    abstract = df['abstract'][index]
    print(f"Article Title: {article_title[:50]}")
    print(f"Abstract: {abstract[:50]}\n")
    
    if df['needs_ai_processing'][index] == 1:
        print('LLM processing article:', article_title[:50],'..')
        response_title = ollama.chat(model='openchat', messages=[
        {
            'role': 'user',
            'content': f"Please provide a concise summary of this research title in a single sentence, using a maximum of 20 words. Use simple language and phrasing without difficult words to ensure it's easily understandable for a layperson: {article_title}",
        },
        ])
        print('AI Title:', response_title['message']['content'])
        df.loc[index, 'layman_title'] = response_title['message']['content'].strip()

        response_abstract = ollama.chat(model='openchat', messages=[
        {
            'role': 'user',
            'content': f"Please provide a concise summary of this research abstract in a single sentence, using a maximum of 50 words. Use simple language and phrasing without difficult words to ensure it's easily understandable for a layperson: {abstract}",
        },
        ])
        print('AI Abstract:',response_abstract['message']['content'])
        df.loc[index, 'layman_abstract'] = response_abstract['message']['content'].strip()
        df.loc[index, 'needs_ai_processing'] = 0 # indicate that it has been processed to not need to compute it again

    elif df['needs_ai_processing'][index] == 0:
        print('Skipping - Already processed', article_title[:50],'..')
    else:
        print('Error! Something went wrong..')


    # Process paragraphs as needed


    


if 'index' in df.columns:
    df.drop(columns=['index'], inplace=True)
else:
    print("The 'index' column does not exist.")

df.reset_index(inplace=True)
df = df[0:n_articles_to_write_to_publish]

df.to_json(selected_research_articles, orient='records', date_format='iso', index=False)
df
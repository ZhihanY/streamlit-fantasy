# --------- Streamlit Example ----------

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st
from tools import *
import requests
import pygwalker as pyg

# ---------- Util Funcs -----------
@output_dataframe
@stat_parse_decorator
def get_player_boxscore(season, season_type='Regular Season', advance_filters={}):
    '''
    -- Retrieve player-level boxscores from stats.nba.com 
    -- Visit nba.com to understand some of the paramterers below

    season: string
        The nba season to retrieve
    season_type: string
        The type of season to retrieve, default 'Regular Season'
    '''

    headers = {
        'Connection': 'keep-alive',
        'Referer': 'https://www.nba.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.200',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    link = 'https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=&DateTo=&Direction=DESC&ISTRound=&LeagueID=00&PlayerOrTeam=P&Season='+ season +'&SeasonType='+ season_type +'&Sorter=DATE'
    res = requests.get(link, headers=headers).json()
    return res

def opponent(row):
    if '@' in row:
        return row.split('@')[1].rstrip()
    else:
        return row.split('vs.')[1].rstrip()

@st.cache_data
def download(df):
    return df.to_csv(index=False, encoding ='utf-8')


# ------------ main ---------------
season = '2022-23'
pbs = get_player_boxscore(season)
pbs['Opponent'] = pbs['MATCHUP'].apply(opponent)
data = pbs.copy()
data.GAME_DATE = pd.to_datetime(data['GAME_DATE'])

st.set_page_config(
    page_title="NBA Player Dashboard",
    page_icon="🏀",
    layout="wide",
)

st.markdown("<h1 style='text-align: center; color: Black;'>⭐ Live Fantasy Player Dashboard ⭐</h1>", unsafe_allow_html=True)
st.text('/n')

with st.sidebar:
    mode = st.radio("Select Visual Mode", ['***Display Mode***', '***Comparison Mode***'])
    if mode == '***Display Mode***':
        main_filter = st.selectbox("Select the Player", pd.unique(pbs["PLAYER_NAME"]))
        match_filter = st.multiselect('Select Opponent', pd.unique(pbs["Opponent"]), [])
        df = pbs[(pbs['PLAYER_NAME'] == main_filter) & (pbs['Opponent'].isin(match_filter))]

    else:
        main_filter = st.multiselect('Select Players', pd.unique(pbs["PLAYER_NAME"]), [], max_selections=2)
        df = pbs[pbs['PLAYER_NAME'].isin(main_filter)]
    st.download_button('Download Data', download(pbs), 'fantasy_dash.csv')

if mode == '***Display Mode***':

    # creating a single-element container.
    placeholder = st.empty()

    # crating kPIs
    pts = df['PTS'].mean()
    rbd = df['REB'].mean()
    ast = df['AST'].mean()
    f_pts = df['FANTASY_PTS'].mean()

    with placeholder.container():
        # create three columns
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        # fill in those three columns with respective metrics or KPIs
        kpi1.metric(
            label="PTS ⏳",
            value=round(pts, 1)
            #delta=round(avg_age) - 10,
        )
        
        kpi2.metric(
            label="Rebounds 💍",
            value=round(rbd, 1)
            #delta=-10 + count_married,
        )
        
        kpi3.metric(
            label="Assists",
            value=round(ast,1)
            #delta=-round(balance / count_married) * 100,
        )
        
        kpi4.metric(
            label="Fantasy Points ＄",
            value=round(f_pts,1)
            #delta=-round(balance / count_married) * 100,
        )
        
        # create two columns for charts
        fig_col1, fig_col2 = st.columns(2)

        with fig_col1:
            st.markdown("<h3 style='text-align: center; color: Black;'>PTS Trend</h3>", unsafe_allow_html=True)
            fig = px.line(
                data_frame=df, y="PTS", x="GAME_DATE"
            )
            st.write(fig)
                
        with fig_col2:
            st.markdown("<h3 style='text-align: center; color: Black;'>Fantasy PTS Trend</h3>", unsafe_allow_html=True)
            fig2 = px.line(
                data_frame=df, y="FANTASY_PTS", x="GAME_DATE"
            )
            st.write(fig2)
        
        st.markdown("### Detailed Table View")
        st.dataframe(df, hide_index=True)

    diy_block = st.container()
    with diy_block:
        prompt = diy_block.chat_input('Type Customized Commands')
        if prompt:
            pyg.walk(data)


else:
    from streamlit_elements import elements, nivo, mui, html
    
    with elements("nivo_charts"):

    # Streamlit Elements includes 45 dataviz components powered by Nivo.

        #data = 
        DATA = []
        
        selection = df['PLAYER_NAME'].unique()

        for attr in ['PTS', 'REB', 'AST', 'MIN', 'FANTASY_PTS']:
            player_dict = dict()
            player_dict['attribute'] = attr
            if len(selection) > 0:
                player_dict[selection[0]] = df[df['PLAYER_NAME'] == selection[0]][attr].mean()
                player_dict[selection[-1]] = df[df['PLAYER_NAME'] == selection[-1]][attr].mean()
            DATA.append(player_dict)
    
        with mui.Box(sx={"height": 500}):
            nivo.Radar(
                data=DATA,
                keys=df['PLAYER_NAME'].unique(),
                indexBy='attribute',
                valueFormat=">-.1f",
                margin={ "top": 70, "right": 80, "bottom": 40, "left": 80 },
                borderColor={ "from": "color" },
                gridLabelOffset=36,
                dotSize=10,
                dotColor={ "theme": "background" },
                dotBorderWidth=2,
                motionConfig="wobbly",
                legends=[
                    {
                        "anchor": "top-left",
                        "direction": "column",
                        "translateX": -50,
                        "translateY": -40,
                        "itemWidth": 80,
                        "itemHeight": 20,
                        "itemTextColor": "#999",
                        "symbolSize": 12,
                        "symbolShape": "circle",
                        "effects": [
                            {
                                "on": "hover",
                                "style": {
                                    "itemTextColor": "#000"
                                }
                            }
                        ]
                    }
                ],
                theme={
                    "background": "#FFFFFF",
                    "textColor": "#31333F",
                    "tooltip": {
                        "container": {
                            "background": "#FFFFFF",
                            "color": "#31333F",
                        }
                    }
                }
            )
        
        st.markdown("### Data View")
        DATA = pd.DataFrame(DATA).round(1)
        st.dataframe(DATA)
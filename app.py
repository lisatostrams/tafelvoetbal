# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 16:41:18 2024

@author: tostraml
"""

import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import io
import base64
import dash_table
import dash_bootstrap_components as dbc
import numpy as np
from datetime import date
import itertools
import plotly.express as px

# Sample CSV data
INITIAL_CSV = pd.read_csv('db.csv').fillna('')
columns = ['Naam1','Naam2','wins','losses']

indivi = INITIAL_CSV.groupby('Naam1').agg({'wins':'sum','losses':'sum','games':'sum'}).add(INITIAL_CSV.groupby('Naam2').agg({'wins':'sum','losses':'sum','games':'sum'}),fill_value=0)
indivi['proportie_gewonnen'] = (indivi.wins/(indivi.wins+indivi.losses)).fillna(0)
indivi=indivi.reset_index().rename({'index':'Naam'},axis=1)
indivi[indivi.Naam==''] = ['',0,0,0,0]
indivi.games = indivi.wins+indivi.losses
indivi.sort_values(by='games', ascending=False,inplace=True)
namen = indivi.Naam.values

app = dash.Dash(__name__)


nav_item1 = dbc.NavItem(dbc.NavLink("Wij willen spelen..",id='home', href="/",className='nav-link',active='exact'))
nav_item2 = dbc.NavItem(dbc.NavLink("Players Championship",id='page1', href="/page-1",className='nav-link'))
nav_item3 = dbc.NavItem(dbc.NavLink("Team Championship",id='page2', href="/page-2",className='nav-link'))
nav_item4 = dbc.NavItem(dbc.NavLink('Gespeelde potjes',id='page3', href='/page-3',className='nav-link'))
nav_item5 = dbc.NavItem(dbc.NavLink('Stats for nerds',id='page4', href='/page-4',className='nav-link'))
nav_item6 = dbc.NavItem(dbc.NavLink('',href='/admin',className='nav-link-secret'))
app.layout = html.Div([
    dcc.Location(id='url'),
    html.Header("Rijksinstituut voor Voetballen \nen Malligheid", id='header',className='header-color',style={'margin-left':-0,'whiteSpace': 'pre-wrap'}),
    html.Header('SPA-felvoetbal',id='smol-header',className='header-small'),
    dbc.Nav(
        [nav_item1,nav_item2,nav_item3,nav_item4,nav_item5],
        pills=True,
        # fill=True,

        className="nav-bar",
        style={'display':'flex'}
        
    
    ),
    html.Div([
        dbc.Container(id='content')]),
    
    dcc.Store(id='store')
])



@app.callback(Output("content", "children"),
              [Input("url", "pathname")])
def render_content(pathname):
    # app.current_user = request.authorization['username']
    
    if pathname == "/":
        
        return html.Div([
            html.H1('Kies 2 of meer spelers:'),
            html.Br(),
            html.Div([
                
                dcc.Dropdown(
                    id='dropdown-1',
                    options=[{'label': naam, 'value': naam} for naam in namen],
                    value=namen[0],
                    clearable=False,
                    style={'width':'80%'}
                ),
                dcc.Dropdown(
                    id='dropdown-2',
                    options=[{'label': naam, 'value': naam} for naam in namen],
                    value=namen[1],
                    clearable=False,
                    style={'width':'80%'}
                ),
                html.Br(),
                dcc.Dropdown(
                    id='dropdown-3',
                    options=[{'label': naam, 'value': naam} for naam in namen],
                    value=namen[2],
                    clearable=False,
                    style={'width':'80%'}
                ),
                dcc.Dropdown(
                    id='dropdown-4',
                    options=[{'label': naam, 'value': naam} for naam in namen],
                    value=namen[3],
                    clearable=False,
                    style={'width':'80%'}
                ),
            ], style={'display': 'flex'}),
            html.Br(),
            html.Div(children=[
            html.Button('Kies teams voor me!', id='team-order', n_clicks=0),
            html.Button('Ik wil een score invoeren!', id='team-score', n_clicks=0),
            ]),
            html.Div(id='output-div'),
            html.Div(id='output-div2')

            ])
    elif pathname == "/page-1":
        df = pd.read_csv('db.csv')
        indivi = df.groupby('Naam1').agg({'wins':'sum','losses':'sum'}).add(df.groupby('Naam2').agg({'wins':'sum','losses':'sum'}),fill_value=0)
        indivi['proportie_gewonnen'] = (indivi.wins/(indivi.wins+indivi.losses)).fillna(0)
        indivi=indivi.reset_index().rename({'index':'Naam'},axis=1)
        indivi['score'] = indivi.wins*3 + indivi.losses
        indivi.sort_values(by='score',inplace=True,ascending=False)
        indivi['proportie_gewonnen'] = indivi['proportie_gewonnen'].round(4).apply(str)
        indivi['rank'] = list(range(1,len(indivi)+1))
        cols = ['rank', 'Naam', 'wins', 'losses', 'proportie_gewonnen', 'score']
        return html.Div(className='row', children=[
            html.H1('Individuele scores:'),
            dash_table.DataTable(
                id='your-table',
                data = indivi.to_dict('records'),
                columns = [{'id':c,'name':c} for c in cols],
                editable=False
            ),
            
            
            ])
    
    elif pathname == "/page-2":
        df = pd.read_csv('db.csv')
        df['proportie'] = (df.wins/(df.losses+df.wins)).fillna(0)
        df['score'] = df.wins*3 + df.losses
        df.sort_values(by='score',inplace=True,ascending=False)
        df['rank'] =  list(range(1,len(df)+1))
        cols = ['rank','Naam1', 'Naam2', 'wins', 'losses', 'proportie', 'score']
        

        return html.Div(className='row', children=[
            html.H1('Team scores:'),
            dash_table.DataTable(
                id='our-table',
                data = df.to_dict('records'),
                columns = [{'id':c,'name':c} for c in cols],
                editable=False
            ),
            
            
            ])

    elif pathname == "/page-3":
        df = pd.read_csv('gespeelde_potjes.csv')

        return html.Div(className='row', children=[
            html.H1('Overzicht alle gespeelde potjes!'),
            dash_table.DataTable(
                id='our-table',
                data = df.to_dict('records'),
                columns = [{'id':c,'name':c} for c in df.columns],
                editable=False
            ),
            
            
            ])
    
    elif pathname == "/page-4":  

        
        return html.Div(className='row', children=[
            html.H1('Statistieken per speler:'),
            dcc.Dropdown(
                    id='dropdown-stat',
                    options=[{'label': naam, 'value': naam} for naam in namen if naam != ''],
                    value=namen[0],
                    clearable=False,
                    style={'width':'80%'}
                ),
            html.P(id='bvrienden'),
            html.P(id='svrienden'),
            html.P(id='nemesis'),
            html.P(id='pwn'),
            dcc.Graph(id='winrate'),
            html.P(id='potjesgespeeld'),
            html.Div(id='tablediv',children=[]),
     
            #dcc.Graph(id='timeline'), 
            ])
    
    elif pathname == "/admin":  

        
        return html.Div(className='row', children=[
            html.H1('admin'),
            dcc.Input(id='password'),
            html.Div(id='admin-stuff')
            
            
         
            ])
    
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        
    ) , html.Div(
        [
            html.H1("404: Not found"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        
    )


@app.callback(
    Output('tablediv','children'),
    Output('potjesgespeeld','children'),
    Input("dropdown-stat", "value"))
def generate_table(naam):

    potjes = pd.read_csv('gespeelde_potjes.csv')
    df = potjes[potjes.Team1.str.contains(naam)|potjes.Team2.str.contains(naam)]
    return [dash_table.DataTable(
        id='your-table',
        data = df.to_dict('records'),
        columns = [{'id':c,'name':c} for c in df.columns],
        editable=False
    )], f"Je hebt {len(df)} potjes gespeeld."
            
   



@app.callback(
    Output("bvrienden", "children"), 
    Output("svrienden", "children"), 
    Output("nemesis", "children"), 
    Output("pwn", "children"), 
    Input("dropdown-stat", "value"), )
def generate_text(naam):
    df = pd.read_csv('db.csv')
    
    beste_vrienden_df = df[(df.Naam1==naam)|(df.Naam2==naam)].sort_values(by='wins',ascending=False).fillna('Jezelf')
    if len(beste_vrienden_df) ==0:
        return 'Je hebt nog geen potjes gespeeld!', '', '', '' 
    beste_vrienden = []
    for i in range(3):
        row = beste_vrienden_df.iloc[i]
        if row.Naam1 != naam:
            beste_vrienden.append((row.Naam1,row.wins))
        else:
            beste_vrienden.append((row.Naam2,row.wins))

    friend_str = f'Je 3 beste vrienden zijn: {beste_vrienden[0][0]} met {beste_vrienden[0][1]:.0f} overwinningen, {beste_vrienden[1][0]} met {beste_vrienden[1][1]:.0f} overwinningen en {beste_vrienden[2][0]} met {beste_vrienden[2][1]:.0f} overwinningen!'

    slechtste_vrienden_df = df[(df.Naam1==naam)|(df.Naam2==naam)].sort_values(by='losses',ascending=False).fillna('Jezelf')
    slechtste_vrienden = []
    for i in range(3):
        row = slechtste_vrienden_df.iloc[i]
        if row.Naam1 != naam:
            slechtste_vrienden.append((row.Naam1,row.losses))
        else:
            slechtste_vrienden.append((row.Naam2,row.losses))

    bad_friend_str = f'Je 3 slechtste vrienden zijn: {slechtste_vrienden[0][0]} met {slechtste_vrienden[0][1]:.0f} nederlagen, \n {slechtste_vrienden[1][0]} met {slechtste_vrienden[1][1]:.0f} nederlagen en \n {slechtste_vrienden[2][0]} met {slechtste_vrienden[2][1]:.0f} nederlagen!'
    potjes = pd.read_csv('gespeelde_potjes.csv')
    nemesis_df = potjes[potjes.Team2.str.contains(naam)]
    nemesis_list = nemesis_df.Team1.str.split(',',expand=True)
    df_melted = nemesis_list.melt(value_name='frenemy', var_name='Original_Column')
    df_melted = df_melted.drop('Original_Column', axis=1)
    nemesis = df_melted.value_counts().reset_index() 
    nemesis = nemesis[nemesis.frenemy!= '']
    try:
        nemesis_str = f'Je nemesis is {nemesis.iloc[0].frenemy}. Je hebt {nemesis.iloc[0][0]} keer verloren van deze nemesis.'
    except:
        nemesis_str = 'Je hebt geen nemesis want je verliest nooit. Dit kwalificeert je om afdelingshoofd van SPA te zijn.' 
        
    if naam=='Benjamin':
        nemesis_str = 'Je hebt de beste stats van alle spelers. Dit kwalificeert je om afdelingshoofd van SPA te zijn.'
    potjes = pd.read_csv('gespeelde_potjes.csv')
    nemesis_df = potjes[potjes.Team1.str.contains(naam)]
    nemesis_list = nemesis_df.Team2.str.split(',',expand=True)
    df_melted = nemesis_list.melt(value_name='frenemy', var_name='Original_Column')
    df_melted = df_melted.drop('Original_Column', axis=1)
    nemesis = df_melted.value_counts().reset_index() 
    nemesis = nemesis[nemesis.frenemy!= '']

    pwn_str = f'Je pwned {nemesis.iloc[0].frenemy}. Je hebt {nemesis.iloc[0].frenemy} {nemesis.iloc[0][0]} keer verslagen. Je domineert!'

    return friend_str, bad_friend_str,nemesis_str, pwn_str



@app.callback(
    Output("winrate", "figure"), 
    Input("dropdown-stat", "value"), )
def generate_chart(naam):
    potjes = pd.read_csv('gespeelde_potjes.csv')
    potjes = potjes[potjes.Team1.str.contains(naam) | potjes.Team2.str.contains(naam)]
    potjes['Uitkomst'] = potjes.Team1.str.contains(naam)
    potjes['Uitkomst'] = potjes['Uitkomst'].map({True:'Gewonnen',False:'Verloren'})
    potjes['Uitkomst_count'] = 1

    fig = px.pie(potjes, values='Uitkomst_count', names='Uitkomst', hole=.3)
    return fig



@app.callback(
    Output('output-div', 'children'),
    Input('team-order','n_clicks'),
    State('dropdown-1', 'value'),
    State('dropdown-2', 'value'),
    State('dropdown-3', 'value'),
    State('dropdown-4', 'value'),
    prevent_initial_call=True
)
def update_output(team_order,value1, value2, value3, value4):
    combi = list(itertools.permutations([value1,value2,value3,value4]))
    
    teams = []

    for com in combi:
        
        team1 = sorted(com[:2])
        team2 = sorted(com[2:])
        if team1 != ['',''] and team2 != ['','']:
            if (team1,team2) not in teams and (team2,team1) not in teams:
                teams.append((team1,team2))
            
    
            
    combi_df = pd.DataFrame(data=teams)
    combi_df['games']=0
    combi_df['sum_prop1'] = 0.0
    combi_df['sum_prop2'] = 0.0
    
        
    df = pd.read_csv('db.csv').fillna('')
    
    indivi = df.groupby('Naam1').agg({'wins':'sum','losses':'sum'}).add(df.groupby('Naam2').agg({'wins':'sum','losses':'sum'}),fill_value=0)
    indivi['proportie_gewonnen'] = (indivi.wins/(indivi.wins+indivi.losses)).fillna(0)
    indivi=indivi.reset_index().rename({'index':'Naam'},axis=1)
    indivi[indivi.Naam==''] = ['',0,0,0]
    for i, combi in enumerate(teams):
        idx = np.where(((df.Naam1==combi[0][0])&(df.Naam2==combi[0][1]))|((df.Naam1==combi[0][1])&(df.Naam2==combi[0][0])))
        games = df.iloc[idx[0][0]]
        n_games = games.games
        prop1 = indivi[indivi.Naam==combi[0][0]].iloc[0].proportie_gewonnen
        prop2 = indivi[indivi.Naam==combi[0][1]].iloc[0].proportie_gewonnen
        combi_df.at[i,'sum_prop1'] = prop1+prop2
     
        idx = np.where(((df.Naam1==combi[1][0])&(df.Naam2==combi[1][1]))|((df.Naam1==combi[1][1])&(df.Naam2==combi[1][0])))
        games = df.iloc[idx[0][0]]
    
        prop1 = indivi[indivi.Naam==combi[1][0]].iloc[0].proportie_gewonnen
        prop2 = indivi[indivi.Naam==combi[1][1]].iloc[0].proportie_gewonnen
        combi_df.at[i,'sum_prop2'] = prop1+prop2
        
        combi_df.at[i,'games'] = n_games + games.games
    
    print(combi_df)
    min_games = combi_df[combi_df.games == combi_df.games.min()]
    if len(min_games)>1:
        min_games['diff_teams'] = abs(min_games.sum_prop1-min_games.sum_prop2)
        min_games.sort_values(by='diff_teams',inplace=True)
    team1 = min_games[0].iloc[0]
    team2 = min_games[1].iloc[0]   
        
    
    
    return html.Div([
        html.Br(),
        html.P(f'Team (¯`·._){team1[0]},{team1[1]}(¯`·._) VS Team (¯`·.¸¸.->{team2[0]},{team2[1]}<-.¸¸.·´¯)',id='teams'),
        html.Br(),
        html.Div(id='input-div', children=
            [html.P(f'Score {team1}'),
             dcc.Input(id='input1'),
             html.P(f'Score {team2}'),
             dcc.Input(id='input2')],
            style={'columnCount': 2}
                 ),
        html.Br(),
        html.P('',id='winnaar'),
        html.Div(id='score_input',children=[], style={'columnCount': 2}),
        html.Div(id='button-div',children=[html.Button('Sla score op',id='add-score')]), 

        
    ])



@app.callback(
    Output('winnaar','children'),
    Input('add-score','n_clicks'),
    State('input1', 'value'),
    State('input2', 'value'), 

    State('teams','children'),
    prevent_initial_call=True
    )
def sla_score_op(button, score1,score2,teams):
    if button is not None:
        df = pd.read_csv('db.csv').fillna('')
        team1 = teams.split('(¯`·._)')[1].split(',')
        team2 = teams.split('¯`·.¸¸.->')[1].split('<-.¸¸.·´¯)')[0].split(',')
        
        print(team1,score1)
        print(team2,score2)

        winnend_team = team1 if int(score1)>int(score2) else team2
        print(winnend_team)
        idx = np.where(((df.Naam1==winnend_team[0])&(df.Naam2==winnend_team[1]))|((df.Naam1==winnend_team[1])&(df.Naam2==winnend_team[0])))
        print(idx)
        df.at[idx[0][0],'wins'] += 1
        verliezend_team = team2 if int(score1)>int(score2) else team1
        idx = np.where(((df.Naam1==verliezend_team[0])&(df.Naam2==verliezend_team[1]))|((df.Naam1==verliezend_team[1])&(df.Naam2==verliezend_team[0])))
        df.at[idx[0][0],'losses'] += 1
        df['games'] = df.wins+df.losses
        df.to_csv('db.csv',index=False)
        
        potjes = pd.read_csv('gespeelde_potjes.csv')

        today = date.today()
        str_today = today.strftime("%d-%m-%Y")
        winnende_score = 10
        verliezende_score = score1 if int(score1)<int(score2) else score2
        potjes = pd.concat([potjes,pd.DataFrame({'Datum':str_today,'Team1':[','.join(winnend_team)],'Team2':[','.join(verliezend_team)],'Score team1':[winnende_score],'Score team2':[verliezende_score]})])
        potjes.to_csv('gespeelde_potjes.csv',index=False)
        return f'Gefeliciteerd Team .o0×X×0o.{winnend_team[0]} en {winnend_team[1]}.o0×X×0o.'

@app.callback(
    Output('output-div2', 'children'),
    Input('team-score','n_clicks'),
    State('dropdown-1', 'value'),
    State('dropdown-2', 'value'),
    State('dropdown-3', 'value'),
    State('dropdown-4', 'value'),
    prevent_initial_call=True
)
def update_output2(team_order,value1, value2, value3, value4):
    team1 = (value1,value2)
    team2 = (value3,value4)
    return html.Div([
        html.Br(),
        html.P(f'Team (¯`·._){value1},{value2}(¯`·._) VS Team (¯`·.¸¸.->{value3},{value4}<-.¸¸.·´¯)',id='teams'),
        html.Br(),
        html.Div(id='input-div', children=
            [html.P(f'Score {team1}'),
             dcc.Input(id='input1'),
             html.P(f'Score {team2}'),
             dcc.Input(id='input2')],
            style={'columnCount': 2}
                 ),
        html.Br(),
        html.P('',id='winnaar'),
        html.Div(id='score_input',children=[], style={'columnCount': 2}),
        html.Div(id='button-div',children=[html.Button('Sla score op',id='add-score')]), 

        
    ])

if __name__ == '__main__':
    app.run_server(debug=False)
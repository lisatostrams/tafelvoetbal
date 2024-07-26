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

# Sample CSV data
INITIAL_CSV = pd.read_csv('db.csv')
columns = ['Naam1','Naam2','wins','losses']
namen = INITIAL_CSV.Naam1.unique()
app = dash.Dash(__name__)


nav_item1 = dbc.NavItem(dbc.NavLink("Wij willen spelen..", href="/",className='nav-link'))
nav_item2 = dbc.NavItem(dbc.NavLink("Players Championship", href="/page-1",className='nav-link'))
nav_item3 = dbc.NavItem(dbc.NavLink("Team Championship", href="/page-2",className='nav-link'))
nav_item4 = dbc.NavItem(dbc.NavLink('Gespeelde potjes',href='/page-3',className='nav-link'))


app.layout = html.Div([
    dcc.Location(id='url'),
    html.Header("Rijksinstituut voor Voetballen \nen Malligheid", id='header',className='header-color',style={'margin-left':10,'whiteSpace': 'pre-wrap'}),
    html.Header('SPA-felvoetbal',id='smol-header',className='header-small'),
    dbc.Nav(
        [nav_item1,nav_item2,nav_item3,nav_item4],
        pills=True,
        fill=True,
        horizontal='start',
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
            html.H1('Kies 4 spelers:'),
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
            html.Button('Kies teams voor me!', id='team-order', n_clicks=0),
            html.Div(id='output-div')

            ])
    elif pathname == "/page-1":
        df = pd.read_csv('db.csv')
        indivi = df.groupby('Naam1').agg({'wins':'sum','losses':'sum'}).add(df.groupby('Naam2').agg({'wins':'sum','losses':'sum'}),fill_value=0)
        indivi['proportie_gewonnen'] = (indivi.wins/(indivi.wins+indivi.losses)).fillna(0)
        indivi=indivi.reset_index().rename({'index':'Naam'},axis=1)
        indivi['score'] = indivi.wins*3 + indivi.losses
        indivi.sort_values(by='score',inplace=True,ascending=False)
        indivi['proportie_gewonnen'] = indivi['score'].round(2).apply(str)
        return html.Div(className='row', children=[
            html.H1('Individuele scores:'),
            dash_table.DataTable(
                id='your-table',
                data = indivi.to_dict('records'),
                columns = [{'id':c,'name':c} for c in indivi.columns],
                editable=False
            ),
            
            
            ])
    
    elif pathname == "/page-2":
        df = pd.read_csv('db.csv')
        df['proportie'] = (df.wins/(df.losses+df.wins)).fillna(0)
        df['score'] = df.wins*3 + df.losses
        df.sort_values(by='score',inplace=True,ascending=False)

        return html.Div(className='row', children=[
            html.H1('Team scores:'),
            dash_table.DataTable(
                id='our-table',
                data = df.to_dict('records'),
                columns = [{'id':c,'name':c} for c in df.columns],
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
    Output('output-div', 'children'),
    Input('team-order','n_clicks'),
    State('dropdown-1', 'value'),
    State('dropdown-2', 'value'),
    State('dropdown-3', 'value'),
    State('dropdown-4', 'value'),
    prevent_initial_call=True
)
def update_output(team_order,value1, value2, value3, value4):
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
        df = pd.read_csv('db.csv')
        team1 = teams.split('(¯`·._)')[1].split(',')
        team2 = teams.split('¯`·.¸¸.->')[1].split('<-.¸¸.·´¯)')[0].split(',')

        winnend_team = team1 if score1>score2 else team2
        idx = np.where(((df.Naam1==winnend_team[0])&(df.Naam2==winnend_team[1]))|((df.Naam1==winnend_team[1])&(df.Naam2==winnend_team[0])))
        df.at[idx[0][0],'wins'] = 1
        verliezend_team = team2 if score1>score2 else team1
        idx = np.where(((df.Naam1==verliezend_team[0])&(df.Naam2==verliezend_team[1]))|((df.Naam1==verliezend_team[1])&(df.Naam2==verliezend_team[0])))
        df.at[idx[0][0],'losses'] = 1
        df.to_csv('db.csv',index=False)
        
        potjes = pd.read_csv('gespeelde_potjes.csv')

        today = date.today()
        str_today = today.strftime("%d-%m-%Y")
        potjes = pd.concat([potjes,pd.DataFrame({'Datum':str_today,'Team1':[','.join(winnend_team)],'Team2':[','.join(verliezend_team)],'Score team1':[score1],'Score team2':[score2]})])
        potjes.to_csv('gespeelde_potjes.csv',index=False)
        return f'Gefeliciteerd Team .o0×X×0o.{winnend_team[0]} en {winnend_team[1]}.o0×X×0o.'
    
if __name__ == '__main__':
    app.run_server(debug=False)
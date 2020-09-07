from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import sd_material_ui as mui
from dash.dependencies import Input, Output,State
import dash_ui as dui
import plotly.graph_objs as plotlygraphs
import dash_bootstrap_components as dbc

app = Dash(__name__,external_stylesheets=['https://codepen.io/rmarren1/pen/mLqGRg.css',"https://use.fontawesome.com/releases/v5.1.0/css/all.css",dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions'] = True
app.title = 'Forecast accuracy dashboard'
#dbc.themes.BOOTSTRAP

#***********************************************************
#*************************Lists*****************************
#***********************************************************

Disos = {'aut':{'Name':'Austria','Region':'eur'},'bel':{'Name':'Belgium','Region':'eur'},'bgr':{'Name':'Bulgaria','Region':'eur'},'chn':{'Name':'Mainland China','Region':'ap'},
         'hrv':{'Name':'Croatia','Region':'eur'},'cyp':{'Name':'Cyprus','Region':'eur'},'cze':{'Name':'Czech Republic','Region':'eur'},'dnk':{'Name':'Denmark','Region':'eur'},
         'est':{'Name':'Estonia','Region':'eur'},'fin':{'Name':'Finland','Region':'eur'},'fra':{'Name':'France','Region':'eur'},'deu':{'Name':'Germany','Region':'eur'},
         'grc':{'Name':'Greece','Region':'eur'},'hun':{'Name':'Hungary','Region':'eur'},'irl':{'Name':'Ireland','Region':'eur'},'ita':{'Name':'Italy','Region':'eur'},
         'jpn':{'Name':'Japan','Region':'ap'},'lva':{'Name':'Latvia','Region':'eur'},'ltu':{'Name':'Lithuania','Region':'eur'},'lux':{'Name':'Luxembourg','Region':'eur'},
         'mlt':{'Name':'Malta','Region':'eur'},'nld':{'Name':'Netherlands','Region':'eur'},'pol':{'Name':'Poland','Region':'eur'},'prt':{'Name':'Portugal','Region':'eur'},
         'rou':{'Name':'Romania','Region':'eur'},'svk':{'Name':'Slovakia','Region':'eur'},'svn':{'Name':'Slovenia','Region':'eur'},'esp':{'Name':'Spain','Region':'eur'},
         'swe':{'Name':'Sweden','Region':'eur'},'gbr':{'Name':'United Kingdom','Region':'eur'},'usa':{'Name':'United States','Region':'nafta'},
         'are':{'Name':'United Arab Emirates','Region':'mena'},'arg':{'Name':'Argentina','Region':'latam'},'aus':{'Name':'Australia','Region':'ap'},'bra':{'Name':'Brazil','Region':'latam'},
         'can':{'Name':'Canada','Region':'nafta'},'che':{'Name':'Switzerland','Region':'eur'},'idn':{'Name':'Indonesia','Region':'ap'},'ind':{'Name':'India','Region':'ap'},
         'isr':{'Name':'Israel','Region':'mena'},'kor':{'Name':'South Korea','Region':'ap'},'kwt':{'Name':'Kuwait','Region':'mena'},'mex':{'Name':'Mexico','Region':'nafta'},
         'nor':{'Name':'Norway','Region':'eur'},'phl':{'Name':'Philippines','Region':'ap'},'rus':{'Name':'Russia','Region':'eur'},'sau':{'Name':'Saudi Arabia','Region':'mena'},
         'tha':{'Name':'Thailand','Region':'ap'},'tur':{'Name':'Turkey','Region':'mena'},'zaf':{'Name':'South Africa','Region':'afr'},'ago':{'Name':'Angola','Region':'afr'},
         'chl':{'Name':'Chile','Region':'latam'},'col':{'Name':'Colombia','Region':'latam'},'dza':{'Name':'Algeria','Region':'mena'},'egy':{'Name':'Egypt','Region':'mena'},
         'hkg':{'Name':'Hong-Kong','Region':'ap'},'irn':{'Name':'Iran','Region':'mena'},'mar':{'Name':'Morocco','Region':'mena'},'mys':{'Name':'Malaysia','Region':'ap'},
         'nga':{'Name':'Nigeria','Region':'afr'},'nzl':{'Name':'New Zealand','Region':'ap'},'per':{'Name':'Peru','Region':'latam'},'qat':{'Name':'Qatar','Region':'mena'},
         'sgp':{'Name':'Singapore','Region':'ap'},'tun':{'Name':'Tunisia','Region':'mena'},'twn':{'Name':'Taiwan','Region':'ap'},'vnm':{'Name':'Vietnam','Region':'ap'}}

Dregions = {'eur':'Europe','nafta':'North America','ap':'Asia','mena':'MENA','afr':'Sub-Saharan Africa','latam':'Latin America'}

Dcons = {'gdpr$':'Real GDP','gdpr': 'Real GDP','cpi':'Consumer Price Index'}

Visos=['can' ,'mex' ,'usa' ,'aut' ,'bel' ,'che' ,'cyp' ,'deu' ,'dnk' ,'esp' ,'fin' ,'fra' ,'gbr' ,'grc' ,'irl' ,'ita' ,
       'lux' ,'mlt' ,'nld' ,'nor' ,'prt' ,'swe' ,'bgr' ,'cze' ,'est' ,'hrv' ,'hun' ,'ltu' ,'lva' ,'pol' ,'rou' ,'rus' ,'svk'
       ,'svn' ,'ago' ,'nga' ,'zaf' ,'are' ,'dza' ,'egy' ,'irn' ,'isr' ,'kwt' ,'mar' ,'qat' ,'sau' ,'tun' ,'tur' ,'arg' ,'bra' ,'chl'
       ,'col' ,'per' ,'aus' ,'chn' ,'hkg' ,'idn' ,'ind' ,'jpn' ,'kor' ,'mys' ,'nzl' ,'phl' ,'sgp' ,'tha' ,'twn' ,'vnm']

Dicregions = {'can':'nafta' ,'mex':'nafta' ,'usa':'nafta' ,'aut':'eur' ,'bel':'eur' ,'che':'eur' ,'cyp':'eur' ,'deu':'eur' ,'dnk':'eur' ,'esp':'eur' ,'fin':'eur' ,'fra':'eur' ,'gbr':'eur' ,'grc':'eur' ,'irl':'eur' ,'ita':'eur' ,
       'lux':'eur' ,'mlt':'eur' ,'nld':'eur' ,'nor':'eur' ,'prt':'eur' ,'swe':'eur' ,'bgr':'eur' ,'cze':'eur' ,'est':'eur' ,'hrv':'eur' ,'hun':'eur' ,'ltu':'eur' ,'lva':'eur' ,'pol':'eur' ,'rou':'eur' ,'rus':'eur' ,'svk':'eur'
       ,'svn':'eur' ,'ago':'afr' ,'nga':'afr' ,'zaf':'afr' ,'are':'mena' ,'dza':'mena' ,'egy':'mena' ,'irn':'mena' ,'isr':'mena' ,'kwt':'mena' ,'mar':'mena' ,'qat':'mena' ,'sau':'mena' ,'tun':'mena' ,'tur':'mena' ,'arg':'latam' ,'bra':'latam' ,'chl':'latam'
       ,'col':'latam' ,'per':'latam' ,'aus':'ap' ,'chn':'ap' ,'hkg':'ap' ,'idn':'ap' ,'ind':'ap' ,'jpn':'ap' ,'kor':'ap' ,'mys':'ap' ,'nzl':'ap' ,'phl':'ap' ,'sgp':'ap' ,'tha':'ap' ,'twn':'ap' ,'vnm':'ap'}

Dictproviders = {}

Vvintages = ['Q115','Q215','Q315','Q415','Q116','Q216','Q316','Q416','Q117','Q217','Q317','Q417','Q118','Q218','Q318','Q418','Q119','Q219','Q319','Q419','Q120','Q220']

#chart_layout = {'layout': {'xaxis':{'tickformat':'.0'},'yaxis':{'tickformat':'.1%','scaleanchor':'x', 'scaleratio':1},'margin':{'b': 20,'t': 50},'plot_bgcolor':'white','transition':{'duration': 500},'title':{'text': "Title",'xanchor': 'center','yanchor': 'top','x':0.5}}}
chart_layout = {'layout': {'xaxis':{'tickformat':'.0'},'yaxis':{'tickformat':'.1%'},'margin':{'b': 20,'t': 50},'plot_bgcolor':'white','transition':{'duration': 500},'title':{'text': "Title",'xanchor': 'center','yanchor': 'top','x':0.5}}}

######################################################################################################################################################
############################################################# Object creation ########################################################################
######################################################################################################################################################

grid = dui.Grid(_id="grid", num_rows=6, num_cols=12, grid_padding=5) #Forecast accuracy
grid2 = dui.Grid(_id="grid2", num_rows=9, num_cols=12, grid_padding=5) #Sources of forecast error
grid3 = dui.Grid(_id="grid3", num_rows=5, num_cols=12, grid_padding=5) #Forecast positioning
grid4 = dui.Grid(_id="grid4", num_rows=5, num_cols=12, grid_padding=5) #Forecast positioning

controlpanel = dui.ControlPanel(_id="controlpanel1")
controlpanel2 = dui.ControlPanel(_id="controlpanel2")
controlpanel3 = dui.ControlPanel(_id="controlpanel3")
controlpanel4 = dui.ControlPanel(_id="controlpanel4")

######################################################################################################################################################
############################################################### Control panel ########################################################################
######################################################################################################################################################

controlpanel.create_group(group="cptitle",group_title="")
controlpanel.add_element(html.Div([html.H2(children=html.P(['Control panel'],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}),"cptitle")

controlpanel.create_group(group="cpblank1",group_title="")
controlpanel.add_element(html.Div([html.H2(children=html.P([html.Br()],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}),"cpblank1")

controlpanel.create_group(group="Conceptsgroup",group_title="Choose a concept")
ConceptSelection = dcc.Dropdown(id="ConceptSelection",options=[{'label': 'Real GDP','value': 'gdpr$'},{'label': 'Consumer price index','value': 'cpi'}],value = 'gdpr$')
controlpanel.add_element(ConceptSelection, "Conceptsgroup")

controlpanel.create_group(group="cpblank6",group_title="")
controlpanel.add_element(html.Div([html.H2(children=html.P([' ', html.Br()],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}),"cpblank6")

controlpanel.create_group(group="Isosgroup",group_title="Choose the country of reference")
IsoSelection = dcc.Dropdown(id="IsoSelection",options=[{'label': Disos[Siso]['Name'],'value': Siso} for Siso in Disos.keys()],value = 'deu')
controlpanel.add_element(IsoSelection, "Isosgroup")

controlpanel.create_group(group="cpblank2",group_title="")
controlpanel.add_element(html.Div([html.H2(children=html.P([' ', html.Br()],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}),"cpblank2")

controlpanel.create_group(group="MonthsAheadgroup",group_title="Choose the horizons at which the quality of the forecast will be evaluated")
MonthSelection = dcc.Dropdown(id = "MonthSelection",options=[{'label': str(i) + 'M', 'value': i} for i in [3,6,9,12,15,18,21,24,27,30,33,36]],value=[24,18,12,6],multi=True)  
controlpanel.add_element(MonthSelection, "MonthsAheadgroup")

controlpanel.create_group(group="cpblank3",group_title="")
controlpanel.add_element(html.Div([html.H2(children=html.P([' ', html.Br()],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}),"cpblank3")

controlpanel.create_group(group="Periodsgroup",group_title="Choose the period of reference")
PeriodSelection = dcc.RangeSlider(id="PeriodSelection",marks={i: i for i in range(2017,2020)},min=2017,max=2019,value=[2017,2019])  
controlpanel.add_element(PeriodSelection, "Periodsgroup")

controlpanel.create_group(group="cpblank4",group_title="")
controlpanel.add_element(html.Div([html.H2(children=html.P([' ', html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),html.Br(),html.Br(),html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br()],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}),"cpblank4")

controlpanel3.create_group(group="Providersgroup",group_title="Choose the competitors to display")
ProviderSelection = dbc.Checklist(id="ProviderSelection",options=[{'label': Skey, 'value': Dictproviders[Skey]} for Skey in Dictproviders.keys()],inline=True,style={'backgroundColor':'transparent'})  
controlpanel3.add_element(ProviderSelection, "Providersgroup")

#controlpanel.create_group(group="cpblank5",group_title="")
#controlpanel.add_element(html.Div([html.H2(children=html.P([' ', html.Br(), html.Br()],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}),"cpblank5")

######################################################################################################################################################
######################################################### 1) Accuracy of forecast ####################################################################
######################################################################################################################################################

#Title
grid.add_element(col=1, row=1, width=3, height=1, element=html.Div([html.Img(src='https://news.ihsmarkit.com/template_files/1247/sites/ihs.newshq.businesswire.com/files/logo/image/IHSMarkit_logo.png',style={'height':'100%', 'width':'100%'})]))
grid.add_element(col=10, row=1, width=3, height=1, element=html.Div([html.Img(src='https://news.ihsmarkit.com/template_files/1247/sites/ihs.newshq.businesswire.com/files/logo/image/IHSMarkit_logo.png',style={'height':'100%', 'width':'100%'})]))
grid.add_element(col=4, row=1, width=6, height=1, element=html.Div([html.H1(children="1 - Forecast accuracy performance",id='titlepart1')],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))
grid.add_element(col=1, row=1, width=1, height=1, element=html.Div(dbc.Tooltip(fn_help('Part 1'),target='titlepart1',placement='bottom')))

#Chart 2: Behavior of forecast for each year
grid.add_graph(col=1, row=3, width=6, height=2, graph_id="chart2")

#Chart 3: Forecast error, aligned starts and ends
grid.add_graph(col=7, row=3, width=6, height=2, graph_id="chart3")

#Chart 5: Spaghetti chart
grid.add_graph(col=1, row=5, width=11, height=2, graph_id="chart5")
form = fn_create_paramsboxform('chart5',
                               [{'Slabel':'#Q projected','Swhat':'nbq','Stype':'input','Lvalues':['6']},
                               {'Slabel':'Operation','Swhat':'Soperation','Stype':'input','Lvalues':['yoy']},
                                {'Slabel':'Chart type','Swhat':'Stype','Stype':'Radio','Soptions':{'Dotted lines':'Dotted lines','Fan chart':'Fan chart'},'Lvalues':['Dotted lines']},
                                {'Slabel':'Display','Swhat':'Vfirstfinal','Stype':'checklist','Soptions':{'First estimate':'First','Final estimate':'Final'},'Lvalues':['First']}])
grid.add_element(col=12, row=5, width=1, height=2, element=html.Div(form))

#Cards deck
Vcarddeck = [];carddeck = dbc.CardDeck(Vcarddeck,id = 'carddeck1');grid.add_element(col=1, row=2, width=12, height=2, element=html.Div(carddeck))

######################################################################################################################################################
############################################################# 2) Sources of error ####################################################################
######################################################################################################################################################

#Title
grid2.add_element(col=1, row=1, width=12, height=1, element=html.Div([html.H1(children="2 - Sources of forecast error",id='titlepart2')],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))
grid2.add_element(col=1, row=1, width=1, height=1, element=html.Div(dbc.Tooltip(fn_help('Part 2'),target='titlepart2',placement='bottom')))

#Chart 10: what year threw us in?
grid2.add_graph(col=2, row=2, width=5, height=2, graph_id="chart10")
form = fn_create_paramsboxform('chart10',[
                                {'Slabel':'X-axis values','Swhat':'xvals','Stype':'dropdown','Soptions':{'Quarters ahead':'nbq','Years':'iYear'},'Lvalues':['nbq']},
                                {'Slabel':'Chart type','Swhat':'Stype','Stype':'Radio','Soptions':{'Bars':'Bars','Lines':'Lines'},'Lvalues':['Bars']},
                                {'Slabel':'Mode','Swhat':'Smode','Stype':'checklist','Soptions':{'Cumulative?':'Cumul'},'Lvalues':['Cumul']}
                                ])
grid2.add_element(col=1, row=2, width=1, height=2, element=html.Div(form))

#Chart 11: Contribs to error
grid2.add_graph(col=2, row=4, width=5, height=2, graph_id="chart11")
form = fn_create_paramsboxform('chart11',[
                                {'Slabel':'Year of ref','Swhat':'iYear','Stype':'dropdown','Soptions':{2017:2017,2018:2018,2019:2019},'Lvalues':[2018]},
                                {'Slabel':'Contributions to','Swhat':'Serrorcontrib','Stype':'dropdown','Soptions':{'Forecast error':'Error','Growth':'Growth'},'Lvalues':['Error']}
                                ])
grid2.add_element(col=1, row=4, width=1, height=2, element=html.Div(form))

#Chart 12: Additional context indicators
grid2.add_graph(col=7, row=2, width=5,  height=4,graph_id="chart12")
form = fn_create_paramsboxform('chart12',[{'Slabel':'Year of ref','Swhat':'iYear','Stype':'dropdown','Soptions':{2017:2017,2018:2018,2019:2019},'Lvalues':[2018]},
                                         {'Slabel':'GDP agg. excluding country','Swhat':'Bexccountry','Stype':'toggle','Soptions':{'Son':True},'Lvalues':['']}])
grid2.add_element(col=12, row=2, width=1, height=4, element=html.Div(form))

#Chart 4:  scatter output gap
grid2.add_graph(col=1, row=6, width=6, height=4, graph_id="chart4")

#Chart 13:  Target chart
grid2.add_graph(col=7, row=6, width=5,  height=4,graph_id="chart13")
form = fn_create_paramsboxform('chart13',[
                                {'Slabel':'X-axis year','Swhat':'iYearX','Stype':'dropdown','Soptions':{2017:2017,2018:2018,2019:2019},'Lvalues':[2017]},
                                {'Slabel':'Y-axis year','Swhat':'iYearY','Stype':'dropdown','Soptions':{2017:2017,2018:2018,2019:2019},'Lvalues':[2018]},
                                {'Slabel':'Z-axis year','Swhat':'iYearZ','Stype':'dropdown','Soptions':{2017:2017,2018:2018,2019:2019},'Lvalues':[2019]},
                                {'Slabel':'# Months ahead','Swhat':'nbq','Stype':'dropdown','Soptions':{str(i) + 'M': i for i in [3,6,9,12,15,18,21,24,27,30,33,36]},'Lvalues':[12]},
                                {'Slabel':'Circle 1','Swhat':'c1','Stype':'input','Lvalues':['0.2%, green']},
                                {'Slabel':'Circle 2','Swhat':'c2','Stype':'input','Lvalues':['0.5%,lightblue']},
                                {'Slabel':'Circle 3','Swhat':'c3','Stype':'input','Lvalues':['1%,orange']},
                                {'Slabel':'Circle 4','Swhat':'c4','Stype':'input','Lvalues':['2%,pink']},
                                {'Slabel':'Circle 5','Swhat':'c5','Stype':'input','Lvalues':['5%,red']},
                                {'Slabel':'Split by','Swhat':'Scatsplit','Stype':'dropdown','Soptions':{i:i for i in ['Error magnitude', 'Regions']},'Lvalues':['Error magnitude']},
                                {'Slabel':'Display mode','Swhat':'Smode','Stype':'dropdown','Soptions':{i:i for i in ['Target', 'Solar system']},'Lvalues':['Target']}
                                ])
grid2.add_element(col=12, row=6, width=1, height=4, element=html.Div(form))

######################################################################################################################################################
########################################################### 3) Forecast positioning ##################################################################
######################################################################################################################################################

grid3.add_element(col=1, row=1, width=12, height=1, element=html.Div([html.H1(children="3 - Forecast positioning",id='titlepart3')],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))
grid3.add_element(col=1, row=1, width=1, height=1, element=html.Div(dbc.Tooltip(fn_help('Part 3'),target='titlepart3',placement='bottom')))

#Chart 14: Projection by contributor
grid3.add_graph(col=2, row=2, width=5,  height=2,graph_id="chart14")
form = fn_create_paramsboxform('chart14',[
                                {'Slabel':'Chart type','Swhat':'Schartmode','Stype':'Radio','Soptions':{'Lines':'Lines','Bars':'Bars'},'Lvalues':['Lines']},
                                {'Slabel':'Vintage','Swhat':'Svintage','Stype':'dropdown','Soptions':{Svintage:Svintage for Svintage in Vvintages},'Lvalues':['Q220']},                               
                                {'Slabel':'Competitors','Swhat':'SproviderMode','Stype':'Radio','Soptions':{'Selected':'Selection','All available':'All'},'Lvalues':['Selection']},
                                {'Slabel':'X-axis','Swhat':'Sxaxis','Stype':'Radio','Soptions':{'Years':'Years','Competitors':'Competitors'},'Lvalues':['Years']},
                                {'Slabel':'Cumulative?','Swhat':'Bcumul','Stype':'toggle','Soptions':{'Son':True},'Lvalues':['']},
                                {'Slabel':'High/low tunnel','Swhat':'Btunnel','Stype':'toggle','Soptions':{'Son':False},'Lvalues':['']},
                                {'Slabel':'+/- 1 STD','Swhat':'Bstd','Stype':'toggle','Soptions':{'Son':False},'Lvalues':['']}
                                ])
grid3.add_element(col=1, row=2, width=1, height=2, element=html.Div(form))

#Chart 15: Dispersion of projections for one country
grid3.add_graph(col=7, row=2, width=5,  height=2,graph_id="chart15")
form = fn_create_paramsboxform('chart15',[
                                {'Slabel':'Vintage','Swhat':'Svintage','Stype':'dropdown','Soptions':{Svintage:Svintage for Svintage in Vvintages},'Lvalues':['Q117']},
                                {'Slabel':'Year of forecast','Swhat':'Syear','Stype':'dropdown','Soptions':{'Current':'Current','Next':'Next','Average':'Average','Cumul':'Cumul'},'Lvalues':['Next']},
                                {'Slabel':'Bucket size','Swhat':'Sstep','Stype':'input','Lvalues':['0.1%']},
                                {'Slabel':'Display','Swhat':'Smode','Stype':'dropdown','Soptions':{'Labels':'Labels','Points':'Scatter'},'Lvalues':['Scatter']},
                                {'Slabel':'Point size','Swhat':'Spointsize','Stype':'input','Lvalues':['7']}
                                ])
grid3.add_element(col=12, row=2, width=1, height=2, element=html.Div(form))

#Chart 16: Dispersion of projections for IHS all countries
grid3.add_graph(col=1, row=4, width=11,  height=2,graph_id="chart16")
form = fn_create_paramsboxform('chart16',[
                                {'Slabel':'Vintage','Swhat':'Svintage','Stype':'dropdown','Soptions':{Svintage:Svintage for Svintage in Vvintages},'Lvalues':['Q117']},
                                {'Slabel':'Year of forecast','Swhat':'Syear','Stype':'dropdown','Soptions':{'Current':'Current','Next':'Next','Average':'Average','Cumul':'Cumul'},'Lvalues':['Next']},
                                {'Slabel':'Gap scale','Swhat':'Sdisplay','Stype':'dropdown','Soptions':{'% gap':'gap','# Stdevs':'std'},'Lvalues':['gap']},        
                                {'Slabel':'Bucket size','Swhat':'Sstep','Stype':'input','Lvalues':['0.1%']},
                                {'Slabel':'Display','Swhat':'Smode','Stype':'dropdown','Soptions':{'Labels':'Labels','Points':'Scatter'},'Lvalues':['Scatter']},
                                {'Slabel':'Point size','Swhat':'Spointsize','Stype':'input','Lvalues':['7']}
                                ])
grid3.add_element(col=12, row=4, width=1, height=2, element=html.Div(form))

######################################################################################################################################################
#################################################### 4) Consensus performance comparison #############################################################
######################################################################################################################################################

#Title
grid4.add_element(col=1, row=1, width=12, height=1, element=html.Div([html.H1(children="4 - Consensus performance comparison",id='titlepart4')],style = {'width': '100%', 'display': 'flex','align-items':'center', 'justify-content':'center','height': '100%'}))
grid4.add_element(col=1, row=1, width=1, height=1, element=html.Div(dbc.Tooltip(fn_help('Part 4'),target='titlepart4',placement='bottom')))

#Chart 8: Forecast and actual for each forecaster
grid4.add_graph(col=2, row=2, width=5, height=2, graph_id="chart8")
form = fn_create_paramsboxform('chart8',[
                                {'Slabel':'#Years ahead','Swhat':'nbYahead','Stype':'dropdown','Soptions':{0:0,1:1,2:2},'Lvalues':[1]},
                                {'Slabel':'Display','Swhat':'Vfirstfinal','Stype':'checklist','Soptions':{'First estimate':'First','Final estimate':'Final'},'Lvalues':['First']},
                                {'Slabel':'High/low tunnel','Swhat':'Btunnel','Stype':'toggle','Soptions':{'Son':False},'Lvalues':['']},
                                {'Slabel':'+/- 1 STD','Swhat':'Bstd','Stype':'toggle','Soptions':{'Son':False},'Lvalues':['']},
                                ])
grid4.add_element(col=1, row=2, width=1, height=2, element=html.Div(form))

#Chart 9: Error, absolute error, rank
grid4.add_graph(col=7, row=2, width=5, height=2, graph_id="chart9")
form = fn_create_paramsboxform('chart9',[
                                {'Slabel':'#Years ahead','Swhat':'nbYahead','Stype':'dropdown','Soptions':{0:0,1:1,2:2},'Lvalues':[1]},
                                {'Slabel':'Display','Swhat':'Serrorrank','Stype':'dropdown','Soptions':{'Actual error':'Error','Absolute error':'Abserr','Rank':'Rank'},'Lvalues':['Error']},
                                {'Slabel':'High/low tunnel','Swhat':'Btunnel','Stype':'toggle','Soptions':{'Son':False},'Lvalues':['']},
                                {'Slabel':'+/- 1 STD','Swhat':'Bstd','Stype':'toggle','Soptions':{'Son':False},'Lvalues':['']}
                                ])
grid4.add_element(col=12, row=2, width=1, height=2, element=html.Div(form))

#Chart 6: Error by forecaster
grid4.add_graph(col=1, row=4, width=6, height=2, graph_id="chart6")

#Chart 7: Cumulative error by forecaster
grid4.add_graph(col=7, row=4, width=6, height=2, graph_id="chart7")


######################################################################################################################################################
############################################################# Genr app layout#########################################################################
######################################################################################################################################################

app.layout = html.Div(
    [html.Div(dui.Layout(grid=grid,controlpanel=controlpanel),style={'height': '100vh','width': '99vw'}),
    html.Div(dui.Layout(grid=grid2,controlpanel=controlpanel2),style={'height': '150vh','width': '99vw'}),
    html.Div(dui.Layout(grid=grid3,controlpanel=controlpanel3),style={'height': '83vh','width': '99vw'}),
    html.Div(dui.Layout(grid=grid4,controlpanel=controlpanel4),style={'height': '83vh','width': '99vw'})])



#app.layout = html.Div(
#    [html.Div(dui.Layout(grid=grid,controlpanel=controlpanel),style={'height': '200vh','width': '99vw'}),
#    html.Div(dui.Layout(grid=grid2,controlpanel=controlpanel2),style={'height': '200vh','width': '99vw'}),
#    html.Div(dui.Layout(grid=grid3,controlpanel=controlpanel3),style={'height': '200vh','width': '99vw'}),
#    html.Div(dui.Layout(grid=grid4,controlpanel=controlpanel4),style={'height': '200vh','width': '99vw'})])


#grid = dui.Grid(_id="grid", num_rows=6, num_cols=12, grid_padding=5) #Forecast accuracy
#grid2 = dui.Grid(_id="grid2", num_rows=9, num_cols=12, grid_padding=5) #Sources of forecast error
#grid3 = dui.Grid(_id="grid3", num_rows=5, num_cols=12, grid_padding=5) #Forecast positioning
#grid4 = dui.Grid(_id="grid4", num_rows=5, num_cols=12, grid_padding=5) #Forecast positioning


#, style={'backgroundColor':'blue'}
#html.Div(
#    dui.Layout(
#        grid=grid,
#        controlpanel=controlpanel
#    ),
#    style={
#        'height': '100vh',
#        'width': '100vw'
#    }
# )	 )
#app.layout = html.Div(
#    [html.Div(dui.Layout(grid=grid),style={'height': '50vh','width': '100vw'}),
#    html.Div(dui.Layout(grid=grid2),style={'height': '50vh','width': '100vw'})]
#)

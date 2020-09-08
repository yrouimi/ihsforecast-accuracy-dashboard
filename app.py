
import datetime as dt;from dateutil.relativedelta import relativedelta
import plotly.graph_objects as plotlygraphs
import plotly
from plotly.offline import iplot
from IPython.display import display
import dash_daq as daq
import pandas as pd

def fn_build_dictdata(Spattern,Stype):#Retrieve eviews values and store them in a dictionary

    df = pd.read_excel (r'C:\Users\yacine.rouimi\Desktop\Archive project\Updated archive\Test.xlsx', sheet_name='Sheet1')
    df = df.astype(object).where(pd.notnull(df),None)
    df = df.to_dict()

    Vdates = fn_create_datelist('2010Q1 2023Q4','Q')
    Vdatesshort = fn_create_datelist('2014Q1 2021Q4','Q')

    #Build a dictionary of dictionaries
    Ddictfull = {}

    for ikey in df['Mnemonics']:

        Smnemonic = df['Mnemonics'][ikey]

        if 'ihs' in Smnemonic.lower():
            Vd = Vdates
        else:
            Vd = Vdatesshort

        Ddict={}

        for Sdate in Vd:

            Dval = df[Sdate][ikey]

            Ddict[Sdate] = Dval
                
        Ddictfull[Smnemonic.lower()] = Ddict
        
    return Ddictfull
    
def fn_filter_competnames(Scon,Siso):#Filter all competitors available in dictionary

    Vcompet = []
    Scomps = ''
    
    for Smnemo in DictDatabase:
        
        Scomp = fn_extract_competname(Smnemo)
    
        if Siso.lower() in Smnemo.lower() and Scon.lower() in Smnemo.lower() and Scomp not in Scomps and Scomp!='ihs':
    
            Scomps = Scomps + ' ' + Scomp
        
            Vcompet.append(Scomp)
            
    return Vcompet    
    
def fn_extract_competname(Smnemo):
    
    Vtxt = Smnemo.split("_")
    
    Stxt = Vtxt[len(Vtxt)-1]
    
    return Stxt
    
#***************************************************************************
#***************************************************************************
#***************************************************************************
#***********************DATA CALCULATION FUNCTIONS**************************
#***************************************************************************
#***************************************************************************
#***************************************************************************

def fn_average(num):
    sum_num = 0
    for t in num:
        sum_num = sum_num + t           

    avg = sum_num / len(num)
    return avg

def fn_ping_dictdatabase(Dictdata,Smnemonic,Soperation,Sdaterange):

    Vmat = [];Smnemonic = Smnemonic.lower()

    if len(Sdaterange)==6:
        Vdates = fn_create_datelist(Sdaterange + ' ' + Sdaterange,'Q')    
    else:
        Vdates = fn_create_datelist(Sdaterange,'Q')

    if Smnemonic not in Dictdata:
        for Sdate in Vdates:
            Vmat.append(None)
        return Vmat
        
    if '=' in Soperation:
        Vargs = Soperation.split('=')
        Sd = Vargs[0];Sdate = Sd.split('-')
        Dval = float(Vargs[1])
        if len(Sd) == 4:
            Sd = Sd + 'Q4'
            Drebasefact = fn_ping_dictdatabase(Dictdata,Smnemonic,'4qma',Sd)
        else:
            Drebasefact = fn_ping_dictdatabase(Dictdata,Smnemonic,'lvl',Sd)            
        
    for Sdate in Vdates:
    
        if Soperation.lower() == 'lvl':
            Vmat.append(Dictdata[Smnemonic][Sdate])    
    
        if Soperation.lower() == '4qma':
            
            Sdate2 = fn_Qdate_offset(Sdate,-3)            
            Vmat2 = fn_ping_dictdatabase(Dictdata,Smnemonic,'lvl',Sdate2 + ' ' + Sdate)
            Vmat.append(fn_average(Vmat2))
        
        if Soperation.lower() == 'yoy':

            Scompa = fn_Qdate_offset(Sdate,-4)
            if Dictdata[Smnemonic][Scompa]!=None:
                
                Vmat.append(Dictdata[Smnemonic][Sdate]/Dictdata[Smnemonic][Scompa]-1)
        
        if Soperation.lower() == '4q4q':

            Scompa =fn_Qdate_offset(Sdate,-7)
            
            if Dictdata[Smnemonic][Scompa]!=None:
                    
                Vdates2 = fn_create_datelist(Scompa + ' ' + Sdate,'Q')
                
                Vy = [Dictdata[Smnemonic][Sdate] for Sdate in Vdates2]
                
                Snone =fn_isvalueinlist(None,Vy)
                
                if Snone == 'no':
                    valeur = Dictdata[Smnemonic][Vdates2[4]]+Dictdata[Smnemonic][Vdates2[5]]+Dictdata[Smnemonic][Vdates2[6]]+Dictdata[Smnemonic][Vdates2[7]]
                    valeur = valeur/(Dictdata[Smnemonic][Vdates2[0]]+Dictdata[Smnemonic][Vdates2[1]]+Dictdata[Smnemonic][Vdates2[2]]+Dictdata[Smnemonic][Vdates2[3]])-1
                    Vmat.append(valeur)
                else:
                    Vmat.append(None)
                
            else:
                Vmat.append(None)

        if fn_extract_leftmidright('left',Soperation.lower(),8) == 'q4q4diff':

            Scompa =fn_Qdate_offset(Sdate,-4)
            
            if Dictdata[Smnemonic][Scompa]!=None:

                Vdates2 = fn_create_datelist(Scompa + ' ' + Sdate,'Q')
                valeur = Dictdata[Smnemonic][Vdates2[4]]
                valeur = (valeur-Dictdata[Smnemonic][Vdates2[0]])
                
                if fn_extract_leftmidright('right',Soperation.lower(),3) == 'bps':
                    valeur= valeur*100
                
                Vmat.append(valeur)
        
        if '=' in Soperation:
            
            if Dictdata[Smnemonic][Sdate]!=None:
                valeur = Dictdata[Smnemonic][Sdate]/Drebasefact[0]*Dval
            else:
                valeur = None
            
            Vmat.append(valeur)
                
    return Vmat    
    
def fn_draw_circle(R, Cx, Cy,Cz,option3d):
    
    import math
    
    if option3d != '3d':
        #Radians
        Vi=[i for i in range(0,361)]
        Vradians= [math.pi/180*i for i in Vi]
        Vx = [math.sin(radian)*R+Cx for radian in Vradians]
        Vy = [math.cos(radian)*R+Cy for radian in Vradians]
        Vxyz = [Vx,Vy]

    if option3d == '3d':
        step = 20
        #Radians
        Vi=[i for i in range(-360,361,step)]
        Vu= [math.pi/180*i for i in Vi];Vv= [math.pi/360*i for i in Vi]
        Vx0 =[math.sin(u)*math.sin(v)*R+Cx for u in Vu for v in Vv]
        Vy0 =[math.cos(v)*R+Cy for u in Vu  for v in Vv]
        Vz0 =[math.cos(u)*math.sin(v)*R+Cz for u in Vu for v in Vv]   
        Vy = Vx0;Vz = Vy0;Vx = Vz0;Vxyz = [Vx,Vy,Vz]
    
    return Vxyz    

def fn_calc_aveerror(Smnemo,Vminmaxyear,ihorizon,Sprovider):

    nbq = ihorizon / 3
    Vyy = [];miniYear = Vminmaxyear[0]
    if len(Vminmaxyear)>1:
        maxiYear = Vminmaxyear[1]
    else:
        maxiYear = miniYear
    
    Snone = 'no'
    
    for iYear in range(miniYear,maxiYear+1):

        Sreleasedate = str(iYear+1) + 'Q2'

        Svintage = fn_Qdate_offset(Sreleasedate,-nbq);Dvintage = fn_convert_Sdaterange([Svintage])
        Svintage = 'Q' + str(Dvintage[0].month//3) + fn_extract_leftmidright('right',str(Dvintage[0].year),2) 
        Smnemonic = Smnemo + '_' + Svintage + '_' + Sprovider
        Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(iYear) + 'Q4')
        Smnemonic = Smnemo + '_' + 'Q2' + fn_extract_leftmidright('right',str(iYear+1),2) + '_ihs'  #+ Sprovider   Take ihs, as the data for previous year is not available in consensus sheet (We had )
        Vdatapoint2 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(iYear) + 'Q4')
        
        if Vdatapoint[0]!=None and Vdatapoint2[0]!=None:
            Vyy.append(abs(Vdatapoint[0]-Vdatapoint2[0]))
        else:
            Vyy.append(None)
            Snone = 'yes'
    
    if Snone == 'no':
        averror = fn_average(Vyy) 
    else:
        averror = None 
        
    return averror
    
#***************************************************************************
#***************************************************************************
#***************************************************************************
#***********************DATE MANAGEMENT FUNCTIONS***************************
#***************************************************************************
#***************************************************************************
#***************************************************************************

def fn_Qdate_offset(Sdate,nbq):
    
    iyear = int(Sdate[:4]);n = len(Sdate);imonth = int(Sdate[(n-1):])*3
    Ddate  = dt.datetime(iyear, imonth, 1);Dnewdate = Ddate+relativedelta(months=3*nbq)
    Snewdate = str(Dnewdate.year) + 'Q' + str(int(Dnewdate.month/3))
    return Snewdate
    
def fn_create_datelist(Sdaterange,Sfreq):
    
    dateslist = []
    
    Sdatestart=Sdaterange[:6];Sdateend=Sdaterange[7:]
    
    iyear = int(Sdatestart[:4]);n = len(Sdatestart);imonth = int(Sdatestart[(n-1):])*3
    Ddatestart  = dt.datetime(iyear, imonth, 1);Ddatestart  = Ddatestart+relativedelta(months=-3)
    
    iyear = int(Sdateend[:4]);n = len(Sdateend);imonth = int(Sdateend[(n-1):])*3
    Ddateend  = dt.datetime(iyear, imonth, 1);Ddateend = Ddateend+relativedelta(months=-3)

    if Sfreq == 'Q':
            
        while True:

            Ddatestart = Ddatestart+relativedelta(months=3);Sdate = str(Ddatestart.year) + 'Q' + str(Ddatestart.month//3)
            dateslist.append(Sdate)
            
            if(Ddatestart>Ddateend):
                break
        
    return dateslist

def fn_convert_Sdaterange(Vdates):
    
    #Idea, find whether you have "M" or "Q" in the date, split, and calculate associated numeric date accordingly
    Vmat = []
    
    for Sdate in Vdates:
        
        iyear = int(Sdate[:4]);n = len(Sdate);imonth = int(Sdate[(n-1):])*3;Ddate = dt.datetime(iyear, imonth, 1)
        Vmat.append(Ddate)
        
    return Vmat

def fn_convert_Q115to2015Q1date(Vdates):
    
    #Idea, find whether you have "M" or "Q" in the date, split, and calculate associated numeric date accordingly
    Vmat = []
    
    for Sdate in Vdates:
        
        iyear = int('20' + fn_extract_leftmidright('right',Sdate,2));n = len(Sdate);imonth = int(fn_extract_leftmidright('mid',Sdate,1,1))
        Stxt = str(iyear) + 'Q' + str(imonth)
        Vmat.append(Stxt)
        
    return Vmat

#***************************************************************************
#***************************************************************************
#***************************************************************************
#***********************STRING MANAGEMENT FUNCTIONS*************************
#***************************************************************************
#***************************************************************************
#***************************************************************************

def fn_isvalueinlist(value, Vlist):
    
    Sfound = 'no'
    
    for y in Vlist:
        
        if y==value:
            
            Sfound = 'yes'
            
    return Sfound

def fn_find_plural(Sword): #Finds the plural form of a word

    n = len(Sword); Slast = Sword[(n-1):]
    if Slast == 'y': 
        Stxt = Sword[:(n-1)] + 'ies' 
    else:
        Stxt = Sword + 's'
    
    return Stxt

def fn_extract_keytypes(Ddic): #Finds all keys looking the same in a dictionary (Scenario, Concept etc)

    Lkeys = []
    
    for Skey in Ddic.keys():
    
        Skeytype = ''.join([i for i in Skey if not i.isdigit()])
        Lkeys.append(Skeytype.lower())

    Lkeys = list(dict.fromkeys(Lkeys))

    return Lkeys

def fn_extract_leftmidright(Stype,Stxt,nbcars,start=0):

    if Stype.lower() == 'left':return Stxt[0:nbcars]
    if Stype.lower() == 'right':return Stxt[len(Stxt)-nbcars:]
    if Stype.lower() == 'mid':return Stxt[start:(start+nbcars)]

#***************************************************************************
#***************************************************************************
#***************************************************************************
#******************************SPECIAL FUNCTIONS****************************
#***************************************************************************
#***************************************************************************
#***************************************************************************
#Here to make life easier and apply in a few cases, not generally
    
#Returns first elements, value in string form (with %), second: number, third: color
def fn_split_circleparams(Vcircles,Bnospace):
    
    Vnew = []
    
    for Vc in Vcircles:
        
        if Bnospace == True:
            Vc = Vc.replace(' ','')
        Vc = Vc.replace(';',',');Vc = Vc.replace(':',',')
        if Vc !='':
            Vmat = []
            Vtxt = Vc.split(",")
            Vmat.append(Vtxt[0])
            Dfactor = 100 if Vmat[0].find('%') != -1 else 1 
            Vmat.append(float(Vmat[0].strip('%'))/Dfactor)
            Vmat.append(Vtxt[1])
            Vnew.append(Vmat)
    
    return Vnew
    
def fn_split_regionparams(Vregions,Bnospace=False):
    
    Vnew = []
    
    for Vc in Vregions:
        
        if Bnospace == True:
            Vc = Vc.replace(' ','')
        Vc = Vc.replace(';',',');Vc = Vc.replace(':',',')
        if Vc !='':
            Vmat = []
            Vtxt = Vc.split(",")
            Vmat.append(Vtxt[0])
            Vmat.append(Vtxt[1])
            Vnew.append(Vmat)
    
    return Vnew
    
def linspace_perso(start, stop, n):

    if n ==1:
        return [start,stop]
    
    Vx = []
    
    h = (stop - start) / (n - 1)

    for i in range(n):
       
        Vx.append(start + h * i)

    return Vx
    
    
#***************************************************************************
#***************************************************************************
#***************************************************************************
#******************************USER ENTRY***********************************
#***************************************************************************
#***************************************************************************
#***************************************************************************

def fn_create_paramsboxform(Schartid,Lcontrols):
        
    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Vcontrols = []
    
    for Dcontrol in Lcontrols: #Loop over each control dictionary
    
        #1) Control label: 
        Slabel = Dcontrol['Slabel']
        Swhat = Dcontrol['Swhat'] #What is the element? 'Year','Color', anything
        Sid = Schartid + Swhat #Will be used in callbacks
        Stype = Dcontrol['Stype'] #Type of control
        Vvalues = Dcontrol['Lvalues']
        print(Vvalues)
        
        labelobject = html.Div([dbc.Label(Slabel, html_for=Sid,style=Dicstyle)],style=Dicstyle)
        
        if Stype.lower()=='input':

            #controlobject = html.Div([dbc.Input(type=Stype, id=Sid,debounce=True,placeholder='Enter ' + Swhat,value = Vvalues[0])],style=dict(width= '50%',display='flex', justifyContent='center'))
            controlobject = dbc.Col(html.Div([dbc.Input(type=Stype, id=Sid,debounce=True,placeholder='Enter ' + Swhat,value = Vvalues[0])]),align='center')
            
        if Stype.lower()=='dropdown':
            
            Doptions = Dcontrol['Soptions']
            
            Vchoices = [{'label': u, 'value': v} for u,v in Doptions.items()]
        
            controlobject = html.Div([dcc.Dropdown(id=Sid,options=Vchoices,value = Vvalues[0])],style=Dicstyle)
        
        if Stype.lower()=='radio':
            
            Doptions = Dcontrol['Soptions']
            
            Vchoices = [{'label': u, 'value': v} for u,v in Doptions.items()]
        
            controlobject = html.Div([dbc.RadioItems(id=Sid,options=Vchoices,value = Vvalues[0])],style=Dicstyle)

        if Stype.lower()=='checklist':
        
            Doptions = Dcontrol['Soptions']
            Vchoices = [{'label': u, 'value': v} for u,v in Doptions.items()]
            controlobject = html.Div([dbc.Checklist(id=Sid,options=Vchoices,value = Vvalues)],style=Dicstyle)
        
        if Stype.lower()=='toggle':
            
            onoff = Dcontrol['Soptions']
            Bonoff = onoff['Son']
            controlobject = html.Div([daq.BooleanSwitch(id=Sid,on=Bonoff,color="#66CC66")],style=Dicstyle)  
        
        Vcontrols.append(dbc.FormGroup([labelobject,controlobject],row=True))
        
    #cardheader=dbc.CardHeader("Chart options")
    form = [dbc.CardHeader("Chart options",style=Dicstyle),dbc.CardBody(dbc.Form(Vcontrols))]
    #style={'height':'100vh'}
    return dbc.Card(form)
                         
def fn_help(Spart):
    
    if Spart == 'Part 1':
        Smsg = '- The set of cards gives a summary of how much IHS over/underestimated average growth over the years selected at each of the horizons selected' 
        Smsg = Smsg + '- The top right chart gives the same average information, and shows the detail for each year'
        Smsg = Smsg + '- The top left chart shows for each year how the projection evolved in each forecast vintage'
        Smsg = Smsg + '- The bottom dotted lines/surface chart shows at each point in time the forecast quarters ahead and compares it to what actually materialized'
        
    if Spart == 'Part 4':
        Smsg = '- The top left chart shows the forecast for the current year (or the next) at each point in time' 
        Smsg = Smsg + '- The top right chart displays the error forecasting the current year (or the next) at each point in time'
        Smsg = Smsg + '- The bottom left chart shows the sum of errors made by forecaster at each forecast horizon (for the years selected)'
        Smsg = Smsg + '- The bottom right chart shows that cumulative error by forecaster (eg the last point in the left-hand chart)'
        
    if Spart == 'Part 2':
        Smsg = '- The top left chart shows the error for each year / forecast horizon and tells when exactly is the error' 
        Smsg = Smsg + '- The bottom left chart displays the contributions to the forecast error (what the headline miss is attributable to)'
        Smsg = Smsg + '- The top right chart shows the error for key variables of the global economy'
        Smsg = Smsg + '- The bottom right chart shows a detail of the forecast error for each country. The closer from the center, the more accurate'

    if Spart == 'Part 3':
        Smsg = '- The top left chart shows the projection at a point in time for every contributor' 
        Smsg = Smsg + '- The top right chart shows the position of the forecast for the selected country against other competitors'
        Smsg = Smsg + '- The bottom chart compares IHS forecast to consensus in all available countries'
        
    return Smsg

from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import sd_material_ui as mui
from dash.dependencies import Input, Output,State
import dash_ui as dui
import plotly.graph_objs as plotlygraphs
import dash_bootstrap_components as dbc

app = Dash(__name__,external_stylesheets=['https://codepen.io/rmarren1/pen/mLqGRg.css',"https://use.fontawesome.com/releases/v5.1.0/css/all.css",dbc.themes.BOOTSTRAP])
server = app.server
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


######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
#******************************************************************************
#**********Retrieve eviews values and store them in a dictionary***************
#******************************************************************************

DictDatabase = fn_build_dictdata("*","series")
print(DictDatabase['gdpr$_deu_q115_imf'])

Dictproviders={'abi':'ABI','abn':'ABN Amro','act':'Action Economics','aff':'Affin Hwang','afi':'AFI','ali':'Allianz','aig':'AIG','amp':'AMP Capital','anz':'ANZ Bank',
               'asb':'ASB Bank','ace':'ACERD','axa':'AXA IM','bah':'Bahana Sec.','bak':'BAK Basel','bjb':'Bank Julius Baer','bofa':'BoFA','vont':'Bank Vontobel',
               'bnl':'BNL','bdo':'BDO Unibank','bnd':'Bank Danamon','boar':'Bank of Ayudhya','boc':'Bank of China (HK)','boea':'Bank of East Asia','bonzl':'Bank of New Zealand',
               'btm':'MUFG','perm':'Bank Permata','barc':'Barclays','baye':'BayernLB','bbva':'BBVA','beacon':'Beacon Econ.','berl':'Berliner Sparkasse',
               'bhf':'BHF-Bank','bipe':'BIPE','oxfo':'Oxford Econ.','bmo':'BMO Capital','bnp':'BNP','brcc':'British Chamber Commerce','btfc':'BT Financial Group',
               'camb':'Cambridge Econometrics','capec':'Capital Econ.','spat':'Center for Spatial Economics','cer':'Centro Europa Ricerche','ceoe':'CEOE','cepre':'CEPREDE',
               'cintl':'China Intl.','chung':'Chung-Hua','cibc':'CIBC','cimb':'CIMB','citi':'Citigroup','cobi':'Confed of British Industry','coe':'COE-Rexecode',
               'comz':'Commerzbank','cowb':'Commonwealth Bank','cobc':'Conf Board of Canada','coii':'Confed of Indian Industry','cswe':'Confed of Swedish Enterprise',
               'cofin':'Confindustria','css':'Consensus (Mean)','cpb':'CPB','cacib':'Credit Agricole','cres':'Credit Suisse','cris':'CRISIL','daew':'Daewoo Securities',
               'daii':'Dai-Ichi Life Research','daiw':'Daiwa','dana':'Danareksa Securities','dbs':'DBS Bank','deka':'DekaBank','delo':'Deloitte','desj':'Desjardins','dban':'Deutsche Bank',
               'diw':'DIW','dnb':'DNB','dubr':'Dun Bradstreet','dws':'DWS','dyes':'Dynamic Econ Strategy','dzb':'DZ Bank','eat':'Eaton Corporation','eiu':'EIU','ecop':'Economic Perspectives',
               'ecmap':'Economap','epb':'Erik Penser Bank','etla':'ETLA','eufn':'European Forecast Network','euler':'Euler Hermes','eumo':'Euromonitor  Intl.','exan':'Exane','expe':'Experian',
               'fitr':'Fitch','fanm':'Fannie Mae','fath':'Fathom Consulting','fedex':'FedEx','feri':'FERI','fnzc':'First NZ Capital','fta':'First Trust Advisors','ford':'Ford','func':'FUNCAS',
               'gold':'Goldman Sachs','sant':'Grupo Santander','gama':'GAMA','gmo':'General Motors','gsu':'Georgia State Univ.','gei':'German Econ. Institute','gld':'GlobalData',
               'hang':'Hang Seng Bank','hela':'Helaba Frankfurt','hete':'Heteronomics','hita':'Hitachi Research Institute','hsbc':'HSBC','hwwi':'HWWI','icic':'ICICI Securities','idea':'IDEA',
               'ucar':'Univ. Carlos III','ifo':'IFO','ifw':'IFW','inte':'Intesa Sanpaolo','inra':'India Ratings','infm':'Infometrics','infr':'Informetrica','uoma':'Univ. of Maryland',
               'ing':'ING','iee':'IEE','ifs':'IFS','uam':'UAM','incr':'Institut Crea','item':'ITEM Club','itoc':'ITOCHU Institute','iww':'IW','iwh':'IWH','jcer':'Japan Center for Econ Research',
               'jpm':'JP Morgan','kasi':'Kasikorn Research','kena':'Kenanga Research','kern':'Kern Consulting','kof':'KOF','kota':'Kotak Securities','kpmg':'KPMG','zmi':'KT ZMICO Securities','liv':'Liverpool Macro',
               'lbp':'La Banque Postale','cai':'La Caixa','lcma':'LC Macro Advisors','lgin':'LG Institute','llo':'Lloyds','lom':'Lombard','luz':'Luzerner Kantonalbank','mac':'Macquarie','maca':'Macroeconomic Advisers',
               'man':'Mandiri Sekuritas','may':'Maybank','mel':'Melbourne Institute','met':'Metrobank','mits':'Mitsubishi Research','miz':'Mizuho','mmw':'MM Warburg','moo':'Moodys Analytics',
               'mst':'Morgan Stanley','mufg':'MUFG','nahb':'NAHB','nati':'Natixis','natw':'NatWest','nab':'National Australia Bank','nbc':'National Bank of Canada','nier':'NIER','nho':'NHO','nibc':'NIBC',
               'niesr':'NIESR','nist':'Nippon Steel','nli':'NLI','nom':'Nomura','nord':'Nordea','nort':'Northern Trust','nzier':'NZIER','ocbc':'OCBC','oddo':'Oddo','ofce':'OFCE','pair':'PAIR Conseil',
               'pant':'Pantheon Econ.','phat':'Phatra Securities','pic':'Pictet','pnc':'PNC','prom':'Prometeia','qic':'QIC','rabo':'Rabobank','rbc':'RBC','rbs':'RBS','rdq':'RDQ','ref':'REF','rep':'Repsol',
               'rhb':'RHB','rfe':'Robert Fry Economics','roug':'Roubini Global','rwi':'RWI Essen','salo':'Sal Oppenheim','sams':'Samsung','sbab':'SBAB','schr':'Schroders','scot':'Scotia Economics','seb':'SE Banken',
               'siam':'Siam Commercial Bank','soge':'Societe Generale','sep':'Standard & Poors','stno':'Statistics Norway','stco':'Stokes Consulting','svh':'Svenska Handelsbanken','swl':'Swiss Life',
               'swdb':'Swedbank','swr':'Swiss Re','tsl':'TS Lombard','twni':'Taiwan Insttitute','than':'Thanachart Securities','tcbd':'The Conference Board','gili':'Theodoor Gilissen','titc':'Timetric',
               'tisc':'TISCO','tord':'Toronto Dominion Bank','toy':'Toyota','trim':'Trimegah Securities','ubs':'UBS','unic':'UniCredit','uov':'United Overseas Bank','uomi':'Univ. of Michigan',
               'uoto':'Univ. of Toronto','uob':'UOB','welp':'Wellershoff & Partners','welf':'Wells Fargo','wpac':'Westpac Banking','wgz':'WGZ Bank','yuan':'Yuanta Consulting','zurk':'Zürcher Kantonalbank',
               'imf':'IMF','oecd':'OECD','ec':'AMECO','cns':'Consensus','high':'Cons. High','low':'Cons. Low','std':'Cons. Stdev','ihs':'IHS Markit'}

@app.callback([Output('ProviderSelection', 'options'),Output('ProviderSelection', 'value')],[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value')],state=[State(component_id='ProviderSelection', component_property='value')])
def fn_update_providers(Scon,Siso,Vproviders):
    
    Vcomps = fn_filter_competnames(Scon,Siso)
    
    Sspecialprovs = ''
    
    for Sprov in reversed(['imf','oecd','ec','cns','high','low','std']):
        if Sprov in Vcomps:
            Sspecialprovs = Sspecialprovs + ' ' + Sprov    
            Vcomps.remove(Sprov)
        
    Voptions = [{'label': Dictproviders[Scomp], 'value': Scomp} for Scomp in Vcomps]

    Voptions = sorted(Voptions, key = lambda i: i['value'])    
    
    Vspecialprovs = Sspecialprovs.split(' ')
    for Sprov in Vspecialprovs:
        if Sprov != '':
            Voptions = [{'label':Dictproviders[Sprov],'value':Sprov}] + Voptions
            Vcomps = [Sprov] + Vcomps
    
    if Vproviders != None:
        Vcomps = list(set(Vcomps) & set(Vproviders)) #Find intersection between the two lists
    else:
        Vcomps= []
    
    return Voptions,Vcomps
    


@app.callback(Output('chart2', 'figure'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_create_chart2(Scon,Siso,Vminmaxyear):

    #import pyeviews
    #pythoncom.CoInitialize()
    #eviewsapp=pyeviews.GetEViewsApp(version='EViews.Manager.11',instance='existing', showwindow=True)
    
    fig = plotlygraphs.Figure(chart_layout)
    fig.update_layout({"title": {"text": 'Behaviour of forecast for each year',"font": {"size": 14}},'xaxis':{'title':'Vintage'},'yaxis':{'title':'Projection (%y/y)'}})

    #Key vectors and variables    
    Vdates = [i for i in range(Vminmaxyear[0],Vminmaxyear[1]+1)]
    Vvintages = ['Q115','Q215','Q315','Q415','Q116','Q216','Q316','Q416','Q117','Q217','Q317','Q417','Q118','Q218','Q318','Q418','Q119','Q219','Q319','Q419','Q120','Q220']
    Sprovider = 'IHS'
    
    compteur = 0

    for iDate in Vdates:

        Sdate = str(iDate)
        compteur = compteur+1
        Vx = [];Vy = [];Vmarkers_size = []
        Bnomoredata = False

        for Svintage in Vvintages:

            if Sprovider != 'Actual':
                Smnemonic = Scon + "_" + Siso + '_' + Svintage + '_ihs'
            else:
                Smnemonic = Scon + "_" + Siso +'_0' + '_ihs'

            if Bnomoredata==False:
                Vy2 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Sdate + 'Q4')
                Vy.append(Vy2[0])
                Vx.append(Svintage)

            if Svintage=='Q2' + str(int(fn_extract_leftmidright('right',Sdate,2))+1):
                Vmarkers_size.append(20)
                Bnomoredata = True
            else:
                if Bnomoredata == False:
                    Vmarkers_size.append(8)
        
        Vx = fn_convert_Q115to2015Q1date(Vx)
        
        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,mode='lines+markers',name=Sdate,marker_size=Vmarkers_size))
       
    return fig









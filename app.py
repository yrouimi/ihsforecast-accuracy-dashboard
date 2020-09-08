
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


#Dictproviders={'abi':'ABI','abn':'ABN Amro','act':'Action Economics','aff':'Affin Hwang Capital','afi':'AFI','ali':'Allianz','aig':'AIG','amp':'AMP Capital','anz':'ANZ Bank',
#               'asb':'ASB Bank','ace':'ACERD','axa':'AXA IM','bah':'Bahana Securities','bak':'BAK Basel','bjb':'Bank Julius Baer','bofa':'BoFA Merrill Lynch','vont':'Bank Vontobel',
#               'bnl':'BNL','bdo':'BDO Unibank','bnd':'Bank Danamon','boar':'Bank of Ayudhya','boc':'Bank of China (HK)','boea':'Bank of East Asia','bonzl':'Bank of New Zealand',
#               'btm':'Bank of Tokyo-Mitsubishi','perm':'Bank Permata','barc':'Barclays','baye':'BayernLB','bbva':'BBVA','beacon':'Beacon Economics','berl':'Berliner Sparkasse',
#               'bhf':'BHF-Bank','bipe':'BIPE','oxfo':'Oxford Economics','bmo':'BMO Capital Markets','bnp':'BNP Paribas','brcc':'British Chamber Commerce','btfc':'BT Financial Group',
#               'camb':'Cambridge Econometrics','capec':'Capital Economics','spat':'Center for Spatial Economics','cer':'Centro Europa Ricerche','ceoe':'CEOE','cepre':'CEPREDE',
#               'cintl':'China International','chung':'Chung-Hua Institute','cibc':'CIBC','cimb':'CIMB','citi':'Citigroup','cobi':'Confed of British Industry','coe':'COE-Rexecode',
#               'comz':'Commerzbank','cowb':'Commonwealth Bank','cobc':'Conf Board of Canada','coii':'Confed of Indian Industry','cswe':'Confed of Swedish Enterprise',
#               'cofin':'Confindustria','css':'Consensus (Mean)','cpb':'CPB','cacib':'Credit Agricole','cres':'Credit Suisse','cris':'CRISIL','daew':'Daewoo Securities',
#               'daii':'Dai-Ichi Life Research','daiw':'Daiwa','dana':'Danareksa Securities','dbs':'DBS Bank','deka':'DekaBank','delo':'Deloitte','desj':'Desjardins','dban':'Deutsche Bank',
#               'diw':'DIW','dnb':'DNB','dubr':'Dun & Bradstreet','dws':'DWS','dyes':'Dynamic Econ Strategy','dzb':'DZ Bank','eat':'Eaton Corporation','eiu':'EIU','ecop':'Economic Perspectives',
#               'ecmap':'Economap','epb':'Erik Penser Bank','etla':'ETLA','eufn':'European Forecast Network','euler':'Euler Hermes','eumo':'Euromonitor  International','exan':'Exane','expe':'Experian',
#               'fitr':'Fitch Ratings','fanm':'Fannie Mae','fath':'Fathom Consulting','fedex':'FedEx','feri':'FERI','fnzc':'First NZ Capital','fta':'First Trust Advisors','ford':'Ford','func':'FUNCAS',
#               'gold':'Goldman Sachs','sant':'Grupo Santander','gama':'GAMA','gmo':'General Motors','gsu':'Georgia State University','gei':'German Economic Institute','gld':'GlobalData',
#               'hang':'Hang Seng Bank','hela':'Helaba Frankfurt','hete':'Heteronomics','hita':'Hitachi Research Institute','hsbc':'HSBC','hwwi':'HWWI','icic':'ICICI Securities','idea':'IDEA',
#               'ucar':'University Carlos III','ifo':'IFO','ifw':'IFW','inte':'Intesa Sanpaolo','inra':'India Ratings & Research','infm':'Infometrics','infr':'Informetrica','uoma':'University of Maryland',
#               'ing':'ING','iee':'IEE','ifs':'IFS','uam':'UAM','incr':'Institut Crea','item':'ITEM Club','itoc':'ITOCHU Institute','iww':'IW','iwh':'IWH','jcer':'Japan Center for Econ Research',
#               'jpm':'JP Morgan','kasi':'Kasikorn Research','kena':'Kenanga Research','kern':'Kern Consulting','kof':'KOF','kota':'Kotak Securities','kpmg':'KPMG','zmi':'KT ZMICO Securities','liv':'Liverpool Macro',
#               'lbp':'La Banque Postale','cai':'La Caixa','lcma':'LC Macro Advisors','lgin':'LG Institute','llo':'Lloyds','lom':'Lombard','luz':'Luzerner Kantonalbank','mac':'Macquarie','maca':'Macroeconomic Advisers',
#               'man':'Mandiri Sekuritas','may':'Maybank','mel':'Melbourne Institute','met':'Metrobank','mits':'Mitsubishi Research','miz':'Mizuho','mmw':'MM Warburg','moo':'Moodys Analytics',
#               'mst':'Morgan Stanley','mufg':'MUFG','nahb':'NAHB','nati':'Natixis','natw':'NatWest','nab':'National Australia Bank','nbc':'National Bank of Canada','nier':'NIER','nho':'NHO','nibc':'NIBC',
#               'niesr':'NIESR','nist':'Nippon Steel','nli':'NLI','nom':'Nomura','nord':'Nordea','nort':'Northern Trust','nzier':'NZIER','ocbc':'OCBC','oddo':'Oddo','ofce':'OFCE','pair':'PAIR Conseil',
#               'pant':'Pantheon Economics','phat':'Phatra Securities','pic':'Pictet','pnc':'PNC','prom':'Prometeia','qic':'QIC','rabo':'Rabobank','rbc':'RBC','rbs':'RBS','rdq':'RDQ','ref':'REF','rep':'Repsol',
#               'rhb':'RHB','rfe':'Robert Fry Economics','roug':'Roubini Global','rwi':'RWI Essen','salo':'Sal Oppenheim','sams':'Samsung','sbab':'SBAB','schr':'Schroders','scot':'Scotia Economics','seb':'SE Banken',
#               'siam':'Siam Commercial Bank','soge':'Societe Generale','sep':'Standard & Poors','stno':'Statistics Norway','stco':'Stokes Consulting','svh':'Svenska Handelsbanken','swl':'Swiss Life',
#               'swdb':'Swedbank','swr':'Swiss Re','tsl':'TS Lombard','twni':'Taiwan Insttitute','than':'Thanachart Securities','tcbd':'The Conference Board','gili':'Theodoor Gilissen','titc':'Timetric',
#               'tisc':'TISCO','tord':'Toronto Dominion Bank','toy':'Toyota','trim':'Trimegah Securities','ubs':'UBS','unic':'UniCredit','uov':'United Overseas Bank','uomi':'University of Michigan',
#               'uoto':'University of Toronto','uob':'UOB','welp':'Wellershoff & Partners','welf':'Wells Fargo','wpac':'Westpac Banking Corp','wgz':'WGZ Bank','yuan':'Yuanta Consulting','zurk':'Zürcher Kantonalbank',
#               'imf':'IMF','oecd':'OECD','ec':'AMECO','cns':'Consensus','high':'Cons. High','low':'Cons. Low','std':'Cons. Stdev','ihs':'IHS Markit'}
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
    
@app.callback(Output('carddeck1', 'children'),[Input('MonthSelection', 'value')])
def fn_create_cards(Vmonthsahead):

    Vmonthsahead = sorted(Vmonthsahead,reverse = True)
    Vcarddeck = []
    for i in Vmonthsahead:
        #card = dbc.Card([dbc.CardHeader("Error " + str(i) + ' months ahead'),dbc.CardBody([html.H4("Error", className="card-title"),html.P("Error", className="card-text"),]),],id = "card" + str(i))
        card = dbc.Card([dbc.CardHeader("..."),dbc.CardBody([html.H4("...", className="card-title"),html.P("...", className="card-text"),]),],id = "card" + str(i))
        Vcarddeck.append(card)
    
    return Vcarddeck

   
@app.callback(Output('card3', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card3(Scon,Siso,Vminmaxyear):

    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 3
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))

    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')
    
    Siso = Disos[Siso]['Name']
    
    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])
    return card

@app.callback(Output('card6', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card6(Scon,Siso,Vminmaxyear):

    Shorizon = 6
    
    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))

    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')

    Siso = Disos[Siso]['Name']
    
    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card

@app.callback(Output('card9', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card9(Scon, Siso,Vminmaxyear):

    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 9
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))
  
    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')

    Siso = Disos[Siso]['Name']
    
    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card

@app.callback(Output('card12', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card12(Scon,Siso,Vminmaxyear):

    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 12
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))
    
    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')

    Siso = Disos[Siso]['Name']
    
    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card

@app.callback(Output('card15', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card15(Scon,Siso,Vminmaxyear):

    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 15
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))
    
    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')

    Siso = Disos[Siso]['Name']    

    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)

    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card

@app.callback(Output('card18', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card18(Scon,Siso,Vminmaxyear):

    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 18
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))
    
    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')

    Siso = Disos[Siso]['Name']
    
    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card

@app.callback(Output('card21', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card21(Scon,Siso,Vminmaxyear):

    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 21
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))
    
    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')

    Siso = Disos[Siso]['Name']
    
    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card

@app.callback(Output('card24', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card24(Scon,Siso,Vminmaxyear):
    
    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 24
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))
    
    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')

    Siso = Disos[Siso]['Name']
    
    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card

@app.callback(Output('card27', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card27(Scon,Siso,Vminmaxyear):

    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 27
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))
    
    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')

    Siso = Disos[Siso]['Name']
    
    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card

@app.callback(Output('card30', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card30(Scon,Siso,Vminmaxyear):

    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 30;Scon = 'gdpr$'
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))
    
    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')
    
    Siso = Disos[Siso]['Name']    

    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card

@app.callback(Output('card33', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card33(Scon,Siso,Vminmaxyear):

    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 33;Scon = 'gdpr$'
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))
    
    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')

    Siso = Disos[Siso]['Name']
    
    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card

@app.callback(Output('card36', 'children'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value')])
def fn_update_card36(Scon,Siso,Vminmaxyear):

    Dicstyle = {'width': '100%', 'display': 'flex','align-items': 'center','justify-content':'center'}
    
    Shorizon = 36;Scon = 'gdpr$'
    
    Vminmaxyear = list(dict.fromkeys(Vminmaxyear))
    
    averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,Shorizon,'ihs')
    
    Siso = Disos[Siso]['Name']
    
    if len(Vminmaxyear)>1:
        Speriodmsg = 'for the years ' + str(min(Vminmaxyear)) + '-' + str(max(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Average absolute error ' + str(Shorizon) + ' months ahead'
    else:
        Speriodmsg = 'for the year ' + str(min(Vminmaxyear)) + ' in ' + Siso
        Stitlemsg = 'Absolute error ' + str(Shorizon) + ' months ahead'
    
    Saverror = "{:.1%}".format(averror)
    
    card = ([dbc.CardHeader(Stitlemsg,style=Dicstyle),dbc.CardBody([html.H4(Saverror, className="card-title",style=Dicstyle),html.P(Speriodmsg, className="card-text",style=Dicstyle)])])

    return card
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
       
    #pythoncom.CoUninitialize()
    #pyeviews.Cleanup()
    return fig
@app.callback(Output('chart3', 'figure'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value'),Input('MonthSelection','value')])
def fn_create_chart3(Scon,Siso,Vminmaxyear,Vmonthsahead):
       
    fig = plotlygraphs.Figure(chart_layout)
    fig.update_layout({"title": {"text": 'Forecast error, aligned starts and ends',"font": {"size": 14}}})
    fig.update_layout({'xaxis':{'title':'# Months ahead of data release'},'yaxis':{'title':'Absolute forecast error'}})
    
    #Key vectors and variables
    Vyears = [i for i in range(Vminmaxyear[0],Vminmaxyear[1]+1)]     #Define vector for years
    Vmonthsahead = sorted(Vmonthsahead,reverse = True)
    Vquartersahead = [i/3 for i in Vmonthsahead];Vx = [str(int(-nbq*3)) + 'M' for nbq in Vquartersahead]
    #Scon = 'gdpr$';

    Vy = []
    
    for iYear in Vyears:
        
        Vyy = [];compteur=-1
        
        for nbq in Vquartersahead:
        
            Sreleasedate = str(iYear+1) + 'Q2'
            
            Svintage = fn_Qdate_offset(Sreleasedate,-nbq);Dvintage = fn_convert_Sdaterange([Svintage])
            Svintage = 'Q' + str(Dvintage[0].month//3) + fn_extract_leftmidright('right',str(Dvintage[0].year),2) 
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_ihs'
            Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(iYear) + 'Q4')
            Smnemonic = Scon + '_' + Siso + '_' + 'Q2' + fn_extract_leftmidright('right',str(iYear+1),2) + '_ihs'
            Vdatapoint2 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(iYear) + 'Q4')
    
            Vyy.append(abs(Vdatapoint[0]-Vdatapoint2[0]))
            
            compteur=compteur+1
            
            if iYear == Vyears[0]:
                Vy.append(abs(Vdatapoint[0]-Vdatapoint2[0]))
            else:
                Vy[compteur]=Vy[compteur] + abs(Vdatapoint[0]-Vdatapoint2[0])
        
        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyy,mode='lines+markers',name=str(iYear)))

    if len(Vyears)>1:
        for i in range(0,len(Vy)):
            Vy[i] = Vy[i]/len(Vyears)
        fig.add_trace(plotlygraphs.Bar(x=Vx,y=Vy,name='Average'))
    
    return fig
@app.callback(Output('chart5', 'figure'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('chart5nbq', 'value'),Input('chart5Soperation', 'value'),Input('chart5Stype', 'value'),Input('chart5Vfirstfinal','value')])
def fn_create_chart5(Scon,Siso,Snbq,Soperation,Scharttype,Vfirstfinal):
    
    #Scon = 'gdpr$'

    #Scharttype = 'Fan chart'#'Dotted lines'#'Fan chart'
    Bfirst = False;Bfinal = False
    if Vfirstfinal !=None:
        SdisFirst = fn_isvalueinlist('First',Vfirstfinal)                
        if SdisFirst == 'yes':
            Bfirst = True
        SdisFinal = fn_isvalueinlist('Final',Vfirstfinal)                
        if SdisFinal == 'yes':
            Bfinal = True
    
    nbqahead = int(Snbq)
    
    num2words = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five',
             6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten',
            11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen',
            15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen',
            19: 'Nineteen', 20: 'Twenty'}
    
    if '=' in Soperation:
        Sticks = '0'
    else:
        Sticks = '.2%'
    
    fig = plotlygraphs.Figure(chart_layout)
    fig.update_layout({"title": {"text": "Actual, first prints and forecast " + num2words[nbqahead].lower() + " quarters ahead","font": {"size": 14}}})
    fig.update_layout({'xaxis':{'title':'Vintage'},'yaxis':{'title':'Forecast (' + Soperation + ')','tickformat':Sticks}})
    
    Vvintages = ['Q115','Q215','Q315','Q415','Q116','Q216','Q316','Q416','Q117','Q217','Q317','Q417','Q118','Q218','Q318','Q418','Q119','Q219']#,'Q319','Q419','Q120','Q220'
    
    Sdaterange = '2012Q1 2019Q4'

    Vx=fn_create_datelist(Sdaterange,'Q') #Full date range to display actuals 

    Vy = fn_ping_dictdatabase(DictDatabase,Scon + '_' + Siso + '_0' + '_ihs',Soperation,Sdaterange) 
    Vxfinal = Vx;Vyfinal = Vy
    if Bfinal == True:
        fig.add_trace(plotlygraphs.Scatter(x=Vxfinal,y=Vyfinal,mode='lines',name='Final'))            

    
    Vy = [];Vx = [];DictFirsts = {}#First prints

    for Svintage in Vvintages:

        Sdate = '20' + fn_extract_leftmidright('right',Svintage,2) + fn_extract_leftmidright('left',Svintage,2)
        Sdate2 = fn_Qdate_offset(Sdate,1)#Moment when first print released'
        Dvintage = fn_convert_Sdaterange([Sdate2])
        Svintage2 = 'Q' + str(Dvintage[0].month//3) + fn_extract_leftmidright('right',str(Dvintage[0].year),2)

        Smnemonic = Scon + '_' + Siso + '_' + Svintage2 + '_ihs'
        Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,Soperation,Sdate)
        Vx.append(Sdate)
        Vy.append(Vdatapoint[0])
        DictFirsts[Svintage] = Vdatapoint[0]

    if Bfirst == True:
        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,mode='lines',name='First estimates'))

    if Scharttype == 'Dotted lines':
    
        for Svintage in Vvintages:

            Sdate = '20' + fn_extract_leftmidright('right',Svintage,2) + fn_extract_leftmidright('left',Svintage,2)
            Dvintage = fn_convert_Sdaterange([Sdate])

            Vy = [];Vx= []
            Vy.append(DictFirsts[Svintage]);Vx.append(Sdate)  #Basis, we will add the change

            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_ihs'
            Vybase = fn_ping_dictdatabase(DictDatabase,Smnemonic,Soperation,Sdate)

            for i in range(1,nbqahead+1):

                Sdate2 = fn_Qdate_offset(Sdate,i)#i quarters ahead: date
                Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_ihs'
                Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,Soperation,Sdate2)
                Vy.append(DictFirsts[Svintage]+Vdatapoint[0]-Vybase[0]);Vx.append(Sdate2)

            fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,mode='lines',name=Svintage,line=dict(color='black', dash='dash')))
    
    if Scharttype == 'Fan chart':
        
        Blet = False
        compteur = -1;Vy = []
        Sdaterange = '2015Q1 ' + fn_Qdate_offset('2019Q4',nbqahead)
        Vx = fn_create_datelist(Sdaterange,'Q')
        
        #1) Download all series as is with the same range. After than, we select and sort
        for Svintage in Vvintages:
            
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_ihs'
            Vyy = fn_ping_dictdatabase(DictDatabase,Smnemonic,Soperation,Sdaterange)
            compteur = compteur+1;
            for i in range(0,compteur):#2) Put none where needed in Vy (before release date)
                Vyy[i]=None
            
            if Svintage == Vvintages[len(Vvintages)-nbqahead]:
                Blet = True
                
            if Blet==False:
                for i in range(compteur+nbqahead,len(Vyy)):#2) Put none where needed in Vy (after nbq until the end)
                    Vyy[i]=None
            
            print(Svintage);print(Vyy);#OK
            Vy.append(Vyy) #Vy: 1 element per vintage, which has the trajectory
        
        compteur=-1;Vyyy = []
        for i in range(0,nbqahead):
            Vyyy.append([])
        
        for Svintage in Vx:
            
            compteur = compteur+1;Vmat = []
            
            for i in range(0,len(Vy)): #Rank observations
                if Vy[i][compteur]!=None:
                    Vmat.append(Vy[i][compteur])
            
            Vmatsorted = sorted(Vmat,key=lambda x: (x is None, x),reverse=False)
            n = len(Vmatsorted);nbnas = nbqahead-n;nbnasbelow = int(nbnas/2);nbnasabove = nbnas-nbnasbelow
            
            j=-1
            for i in range(0,nbnasbelow):
                j=j+1;Vyyy[j].append(None)
            for y in Vmatsorted:
                j=j+1;Vyyy[j].append(y)
            for i in range(0,nbnasabove):
                j=j+1;Vyyy[j].append(None)

        for i in range(0,len(Vyyy)-1):
            
            stepcolor = abs(i+1-nbqahead/2)/(nbqahead/2)
            stepcolor_g = 100+int(155*stepcolor)
            stepcolor_rb = 0+int(255*stepcolor)
            
            print(i);print(stepcolor_g);print(stepcolor_rb)
            
            fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyyy[i],fill=None,mode='lines', line_color='rgba(' + str(stepcolor_rb) + ',' + str(stepcolor_g) + ',' + str(stepcolor_rb) + ',0)',name = 'Test',showlegend=False))  
            fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyyy[i+1],fill='tonexty', line_color = 'rgba(' + str(stepcolor_rb) + ',' + str(stepcolor_g) + ',' + str(stepcolor_rb) + ',0)',mode='lines',name = 'Test',showlegend=False))

        
    return fig

@app.callback(Output('chart4', 'figure'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value'),Input('MonthSelection','value')])
def fn_create_chart4(Scon,Siso,Vminmaxyear,Vmonthsahead):
    
    fig = plotlygraphs.Figure(chart_layout)
        
    fig.update_layout({"title": {"text": "Forecast error and output gap","font": {"size": 14}}})
    fig.update_layout({'xaxis':{'tickformat':'.2%','title':'Output gap at time of projection (%pot GDP)'},'yaxis':{'tickformat':'.2%','title':'Forecast error','scaleanchor':'x', 'scaleratio':1}})
    
    Vmonthsahead = sorted(Vmonthsahead,reverse = True)
    
    #Vy: GDP projection VS Vx: GDP gap at the time. 
    Vyears = [i for i in range(Vminmaxyear[0],Vminmaxyear[1]+1)]     #Define vector for years
    Vquartersahead = [i/3 for i in Vmonthsahead];Vx = [str(int(-nbq*3)) + 'M' for nbq in Vquartersahead]
    #Scon = 'gdpr';

    Vavy = [];Vavx = []
    
    for nbq in Vquartersahead:
        
        Vy = [];Vx = []
        compteur=-1
        
        for iYear in Vyears:
        
            Sreleasedate = str(iYear+1) + 'Q2'
            
            Svintage = fn_Qdate_offset(Sreleasedate,-nbq);Dvintage = fn_convert_Sdaterange([Svintage])
            Svintage = 'Q' + str(Dvintage[0].month//3) + fn_extract_leftmidright('right',str(Dvintage[0].year),2) 
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_ihs'
            Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(iYear) + 'Q4')
            Smnemonic = Scon + '_' + Siso + '_' + 'Q2' + fn_extract_leftmidright('right',str(iYear+1),2) + '_ihs'
            Vdatapoint2 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(iYear) + 'Q4')
    
            Vy.append(Vdatapoint[0]-Vdatapoint2[0]) #Calculate error
            Svintage2 = fn_Qdate_offset(Sreleasedate,-nbq-1) #Svintage2 contains when was the projection made? Minus one quarter is last data point available at the time
            Smnemonic = 'gdpgapr' + '_' + Siso + '_' + Svintage + '_ihs'
            Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'lvl',Svintage2) #Svintage still contains right vintage to look at
            Vx.append(Vdatapoint[0]/100) #Calculate output gap
                        
        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,mode='lines+markers',name=str(int(nbq*3)) + 'M ahead'))                  

    return fig
@app.callback(Output('chart6', 'figure'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value'),Input('MonthSelection','value'),Input('ProviderSelection','value')])
def fn_create_chart6(Scon,Siso,Vminmaxyear,Vmonthsahead,Vproviders):
    
    fig = plotlygraphs.Figure(chart_layout)
        
    fig.update_layout({"title": {"text": "Cumulative absolute forecast error","font": {"size": 14}},'xaxis':{'tickformat':'.2%','title':'# Months ahead'},'yaxis':{'tickformat':'.2%','title':'Forecast error'}})
    
    Vmonthsahead = sorted(Vmonthsahead,reverse = True)

    if Vproviders!=None:
        Vproviders = ['ihs'] + Vproviders
    else:
        Vproviders = ['ihs']
    
    #Vy: GDP projection VS Vx: GDP gap at the time. 
    Vyears = [i for i in range(Vminmaxyear[0],Vminmaxyear[1]+1)]     #Define vector for years
    Vquartersahead = [i/3 for i in Vmonthsahead];Vx = [' '] + [str(int(-nbq*3)) + 'M' for nbq in Vquartersahead]
    #Scon = 'gdpr$';

    Vavy = [];Vavx = []

    for Sprovider in Vproviders:

        Vy = [0];averror = 0
        Snone = 'no'
        
        for nbq in Vquartersahead:
            
            add = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,nbq*3,Sprovider)
            
            if add != None:
                averror = averror + add
                Vy.append(averror)
            else:
                Snone = 'yes'
        
        if Snone == 'no':
            fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,mode='lines+markers',name=Dictproviders[Sprovider]))                  

    return fig
@app.callback(Output('chart7', 'figure'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value'),Input('MonthSelection','value'),Input('ProviderSelection','value')])
def fn_create_chart7(Scon,Siso,Vminmaxyear,Vmonthsahead,Vproviders):
    
    fig = plotlygraphs.Figure(chart_layout)
        
    fig.update_layout({"title": {"text": "Cumulative forecast error by forecaster","font": {"size": 14}},'barmode': 'stack','xaxis':{'title':'Forecaster'},'yaxis':{'tickformat':'.2%','title':'Cumulative forecast error'}})
    
    Vmonthsahead = sorted(Vmonthsahead,reverse = True)
    
    if Vproviders!=None:
        Vproviders = ['ihs'] + Vproviders
    else:
        Vproviders = ['ihs']
    
    #Vy: GDP projection VS Vx: GDP gap at the time. 
    Vyears = [i for i in range(Vminmaxyear[0],Vminmaxyear[1]+1)]     #Define vector for years
    Vquartersahead = [i/3 for i in Vmonthsahead];Vx = [' '] + [str(int(-nbq*3)) + 'M' for nbq in Vquartersahead]
    #Scon = 'gdpr$';
    
    for nbq in Vquartersahead:

        Vy = []
        
        for Sprovider in Vproviders:

            averror = fn_calc_aveerror(Scon + '_' + Siso,Vminmaxyear,nbq*3,Sprovider)            
            
            Vy.append(averror)

        fig.add_trace(plotlygraphs.Bar(x=[Dictproviders[Sprovider] for Sprovider in Vproviders],y=Vy,name=str(int(-nbq*3)) + 'M'))                  

    return fig
@app.callback(Output('chart8', 'figure'),
              [Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('ProviderSelection','value'),Input('chart8Vfirstfinal','value'),Input('chart8nbYahead','value'),Input('chart8Btunnel','on'),Input('chart8Bstd','on')])
def fn_create_chart8(Scon,Siso,Vproviders,Vfirstfinal,nbyahead,Btunnel,Bstd):
    
    fig = plotlygraphs.Figure(chart_layout)
    
    DicStype = {0:'Current year',1:'Year ahead',2:'Two years ahead'}
    
    fig.update_layout({"title": {"text": DicStype[nbyahead]+ " forecast and actual","font": {"size": 14}},'xaxis':{'tickformat':'.2%','title':'Vintage'},'yaxis':{'tickformat':'.2%','title':'Forecast (%y/y)'}})
    
    if Vproviders!=None:
        Vproviders = ['ihs'] + Vproviders
    else:
        Vproviders = ['ihs']

    if nbyahead == 0:
        Vvintages = ['Q115','Q215','Q315','Q415','Q116','Q216','Q316','Q416','Q117','Q217','Q317','Q417','Q118','Q218','Q318','Q418','Q119','Q219','Q319','Q419']#,'Q319','Q419','Q120','Q220'    
    if nbyahead == 1:
        Vvintages = ['Q115','Q215','Q315','Q415','Q116','Q216','Q316','Q416','Q117','Q217','Q317','Q417','Q118','Q218','Q318','Q418']#,'Q319','Q419','Q120','Q220'
    if nbyahead == 2:
        Vvintages = ['Q115','Q215','Q315','Q415','Q116','Q216','Q316','Q416','Q117','Q217','Q317','Q417']#,'Q319','Q419','Q120','Q220'

    Vx = fn_convert_Q115to2015Q1date(Vvintages)
        
    if Btunnel == True:
        if 'high' in Vproviders:
            Vproviders.remove('high')
        if 'low' in Vproviders:
            Vproviders.remove('low')
        Vproviders.append('high')
        Vproviders.append('low')
        
    for Sprovider in Vproviders: #Deal with providers

        Vy = []

        for Svintage in Vvintages:
            
            Sdate = '20' + fn_extract_leftmidright('right',Svintage,2) + fn_extract_leftmidright('left',Svintage,2)
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + Sprovider

            Syear = str(int(fn_extract_leftmidright('left',Sdate,4))+nbyahead)

            Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Syear + 'Q4')          

            Vy.append(Vdatapoint[0])
        
        if Btunnel == False or (Sprovider!='low' and Sprovider!='high'):
        
            fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,mode='lines',name=Dictproviders[Sprovider]))
            
    Vy0 = [];Vyfirsts = []
            
    for Svintage in Vvintages: #Deal with finals, first prints

        Sdate = '20' + fn_extract_leftmidright('right',Svintage,2) + fn_extract_leftmidright('left',Svintage,2)
        Syear = fn_extract_leftmidright('left',Sdate,4)

        Svintage2 = 'Q2' + str(int(fn_extract_leftmidright('right',Syear,2))+nbyahead+1) #Year ahead, available in Q2 of the next year
        Smnemonic = Scon + '_' + Siso + '_' + Svintage2 + '_ihs'
        Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+nbyahead) + 'Q4')

        Vyfirsts.append(Vdatapoint[0])
        
        Smnemonic = Scon + '_' + Siso + '_' + '0' + '_ihs'
        Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+nbyahead) + 'Q4')
        
        Vy0.append(Vdatapoint[0])
    
    if Vfirstfinal !=None:
        
        SdisFirst = fn_isvalueinlist('First',Vfirstfinal)                
        if SdisFirst == 'yes':
            fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyfirsts,mode='markers',name='First estimate'))    
        
        SdisFinal = fn_isvalueinlist('Final',Vfirstfinal)                
        if SdisFinal == 'yes':
            fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy0,mode='markers',name='Final'))
            
    if Btunnel == True:
        
        for Sprovider in ['low','high']: #Deal with providers

            Vy = []

            for Svintage in Vvintages:

                Sdate = '20' + fn_extract_leftmidright('right',Svintage,2) + fn_extract_leftmidright('left',Svintage,2)
                Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + Sprovider

                Syear = str(int(fn_extract_leftmidright('left',Sdate,4))+nbyahead)

                Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Syear + 'Q4')          

                Vy.append(Vdatapoint[0])
            
            if Sprovider == 'low':
                fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,fill=None,mode='lines',line_color='rgba(192,192,192,0.3)',name = 'Tunnel min',showlegend=False))  
            else:
                fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,fill='tonexty',mode='lines',line_color='rgba(192,192,192,0.3)',name = 'Max/min tunnel'))

                
    if Bstd == True:

        Vyplus = [];Vyminus=[]

        for Svintage in Vvintages:

            Sdate = '20' + fn_extract_leftmidright('right',Svintage,2) + fn_extract_leftmidright('left',Svintage,2)
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + 'cns'
            Syear = str(int(fn_extract_leftmidright('left',Sdate,4))+nbyahead)
            
            Vdatapointcns = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Syear + 'Q4')          
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + 'std'
            Vdatapointstd = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Syear + 'Q4')                      
            
            if Vdatapointstd[0]!=None and Vdatapointcns[0]!=None:   
                Vyplus.append(Vdatapointcns[0]+Vdatapointstd[0])
                Vyminus.append(Vdatapointcns[0]-Vdatapointstd[0])
            else:
                Vyplus.append(None)
                Vyminus.append(None)
                
        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyminus,fill=None,mode='lines',line_color='rgba(255,192,203,0.01)',name = 'CNS - 1 stdev',showlegend=False))  
        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyplus,fill='tonexty',mode='lines',line_color='rgba(255,192,203,0.01)',name = '(+)/(-) 1 STD'))

                
    return fig
@app.callback(Output('chart9Btunnel', 'disabled'),[Input('chart9Serrorrank','value')])
def set_button_enabled_state(Serrorrank):
    
    if Serrorrank =='Abserr' or  Serrorrank =='Error':
        return False
    else:
        return True

@app.callback(Output('chart9Bstd', 'disabled'),[Input('chart9Serrorrank','value')])
def set_button_enabled_state(Serrorrank):
    
    if Serrorrank =='Abserr' or  Serrorrank =='Error':
        return False
    else:
        return True
    
@app.callback(Output('chart9', 'figure'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('ProviderSelection','value'),Input('chart9Serrorrank','value'),Input('chart9nbYahead','value'),Input('chart9Btunnel','on'),Input('chart9Bstd','on')])
def fn_create_chart9(Scon,Siso,Vproviders,Smode,nbYahead,Btunnel,Bstd):
    
    fig = plotlygraphs.Figure(chart_layout)

    DicStype = {0:'Current year',1:'Year ahead',2:'Two years ahead'}
    
    if Smode == 'Rank':
        fig.update_layout({"title": {"text": DicStype[nbYahead]+ " forecast - Rank of each forecaster","font": {"size": 14}},'xaxis':{'tickformat':'.2%','title':'Vintage'},'yaxis':{'autorange':'reversed','tickformat':'0','dtick':1,'title':'Rank (1 = Most accurate)'}})
        Btunnel = False;Bstd = False
    else:
        if Smode == 'Abserr':
            Stitle = 'Absolute error'
        if Smode == 'Error':
            Stitle = 'Error'
        fig.update_layout({"title": {"text": DicStype[nbYahead] + " forecast - " + Stitle + " by forecaster","font": {"size": 14}},'xaxis':{'tickformat':'.2%','title':'Vintage'},'yaxis':{'title':'Forecast - ' + Stitle,'tickformat':'.2%'}})
    
    if Vproviders!=None:
        Vproviders = ['ihs'] + Vproviders
    else:
        Vproviders = ['ihs']
    
    if Btunnel == True:
        if 'high' in Vproviders:
            Vproviders.remove('high')
        if 'low' in Vproviders:
            Vproviders.remove('low')
        Vproviders.append('low')
        Vproviders.append('high')
    
    #Scon = 'gdpr$';
    
    if nbYahead == 0:
        Vvintages = ['Q115','Q215','Q315','Q415','Q116','Q216','Q316','Q416','Q117','Q217','Q317','Q417','Q118','Q218','Q318','Q418','Q119','Q219','Q319','Q419']#,'Q319','Q419','Q120','Q220'    
    if nbYahead == 1:
        Vvintages = ['Q115','Q215','Q315','Q415','Q116','Q216','Q316','Q416','Q117','Q217','Q317','Q417','Q118','Q218','Q318','Q418']#,'Q319','Q419','Q120','Q220'
    if nbYahead == 2:
        Vvintages = ['Q115','Q215','Q315','Q415','Q116','Q216','Q316','Q416','Q117','Q217','Q317','Q417']#,'Q319','Q419','Q120','Q220'

        
    Vx = fn_convert_Q115to2015Q1date(Vvintages)
        
    Ddict = {}
    
    for Sprovider in Vproviders:
        
        Vy = []
        
        for Svintage in Vvintages: 

            # 1) Calculate first print
            Sdate = '20' + fn_extract_leftmidright('right',Svintage,2) + fn_extract_leftmidright('left',Svintage,2) #Date associated to vintage
            Syear = fn_extract_leftmidright('left',Sdate,4) #Year associated to vintage'
            Svintage2 = 'Q2' + str(int(fn_extract_leftmidright('right',str(int(Syear)),2))+nbYahead+1) #Year ahead, available in Q2 of the next year
            Smnemonic = Scon + '_' + Siso + '_' + Svintage2 + '_ihs' #Vintage where full year number first available
            Vyfirst = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+nbYahead) + 'Q4')
    
            # 2) Calculate error
            Sdate = '20' + fn_extract_leftmidright('right',Svintage,2) + fn_extract_leftmidright('left',Svintage,2)
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + Sprovider
            Syear = str(int(fn_extract_leftmidright('left',Sdate,4)))
            Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+nbYahead) + 'Q4')        
            
            if Smode == 'Abserr' or Smode == 'Rank':
                if Vdatapoint[0]!=None and Vyfirst[0]!=None:
                    Vy.append(abs(Vdatapoint[0]-Vyfirst[0]))
                else:
                    Vy.append(None)
            else:
                if Vdatapoint[0]!=None and Vyfirst[0]!=None:
                    Vy.append(Vdatapoint[0]-Vyfirst[0])
                else:
                    Vy.append(None)
            
        Ddict[Sprovider] = Vy #All the errors
    
    #Calculate the ranks, if the user wants
    if Smode == 'Rank':
        
        compteur = -1

        for Svintage in Vvintages: 

            compteur= compteur+1;Vy = []

            for Sprovider in Vproviders: 

                val = Ddict[Sprovider][compteur]
                Vy.append(val)

            #Vysorted = sorted(Vy,key=lambda x: (x is None, x),reverse=False)
            Vysorted = sorted(Vy,key=lambda x: (x is None, x),reverse=False)
            Vranks = [Vysorted.index(y)+1 for y in Vy]

            for i in range(0,len(Vproviders)):

                Sprovider = Vproviders[i]

                Ddict[Sprovider][compteur] = Vranks[i]
        
    for Sprovider in Vproviders:

        Vy = Ddict[Sprovider]
        
        if Btunnel == False or (Sprovider!='low' and Sprovider!='high'):
            fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,mode='lines+markers',name=Dictproviders[Sprovider]))
        else:
            if Sprovider=='low':
                fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,fill=None,mode='lines',line_color='rgba(192,192,192,0.3)',name = 'Tunnel min',showlegend=False))
            if Sprovider=='high':
                fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,fill='tonexty',mode='lines',line_color='rgba(192,192,192,0.3)',name = 'Max/min tunnel'))

    if Bstd == True:

        Vyplus = [];Vyminus=[]
        
        for Svintage in Vvintages: 

            # 1) Calculate first print
            Sdate = '20' + fn_extract_leftmidright('right',Svintage,2) + fn_extract_leftmidright('left',Svintage,2) #Date associated to vintage
            Syear = fn_extract_leftmidright('left',Sdate,4) #Year associated to vintage'
            Svintage2 = 'Q2' + str(int(fn_extract_leftmidright('right',str(int(Syear)),2))+nbYahead+1) #Year ahead, available in Q2 of the next year
            Smnemonic = Scon + '_' + Siso + '_' + Svintage2 + '_ihs' #Vintage where full year number first available
            Vyfirst = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+nbYahead) + 'Q4')
    
            # 2) Calculate error
            Sdate = '20' + fn_extract_leftmidright('right',Svintage,2) + fn_extract_leftmidright('left',Svintage,2)
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + 'cns'
            Syear = str(int(fn_extract_leftmidright('left',Sdate,4)))
            Vdatapointcns = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+nbYahead) + 'Q4')        
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + 'std'
            Vdatapointstd = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+nbYahead) + 'Q4')
            
            if Smode == 'Abserr' or Smode == 'Rank':
                if Vdatapointcns[0]!=None and Vdatapointstd[0]!=None and Vyfirst[0]!=None:
                    Vyplus.append(abs(Vdatapointcns[0]+Vdatapointstd[0]-Vyfirst[0]))
                    Vyminus.append(abs(Vdatapointcns[0]-Vdatapointstd[0]-Vyfirst[0]))
                else:
                    Vyplus.append(None);Vyminus.append(None)
            else:
                if Vdatapointstd[0]!=None and Vdatapointcns[0]!=None and Vyfirst[0]!=None:
                    Vyplus.append(Vdatapointcns[0]+Vdatapointstd[0]-Vyfirst[0])
                    Vyminus.append(Vdatapointcns[0]-Vdatapointstd[0]-Vyfirst[0])
                else:
                    Vyplus.append(None);Vyminus.append(None)

        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyminus,fill=None,mode='lines',line_color='rgba(255,192,203,0.3)',name = 'CNS - 1 stdev',showlegend=False))  
        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyplus,fill='tonexty',mode='lines',line_color='rgba(255,192,203,0.3)',name = '(+)/(-) 1 STD'))
    
    return fig
@app.callback(Output('chart10', 'figure'),[Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('PeriodSelection','value'),Input('MonthSelection','value'),Input('chart10xvals','value'),Input('chart10Stype','value'),Input('chart10Smode','value')])
def fn_create_chart10(Scon,Siso,Vminmaxyear,Vmonthsahead,Sxaxis,Scharttype,Schartmode):
       
    fig = plotlygraphs.Figure({'layout': {'xaxis':{'tickformat':'0','dtick':1,'type': 'category'},'yaxis':{'tickformat':'.0'},'margin':{'b': 20,'t': 50},'plot_bgcolor':'white','transition':{'duration': 500},'title':{'text': "Title",'xanchor': 'center','yanchor': 'top','x':0.5}}})        
    
    Smode = Schartmode[0] if len(Schartmode)>0 else 'simple'
    
    #x=#Q ahead or 'years'
    #Stype = 'Lines, Bars
    #Smode = 'Cumulative, Simple'
        
    Vmonthsahead = sorted(Vmonthsahead,reverse = True)
    
    Vyears = [i for i in range(Vminmaxyear[0],Vminmaxyear[1]+1)]     #Define vector for years
    Vquartersahead = [i/3 for i in Vmonthsahead]#Vx = [str(int(-nbq*3)) + 'M' for nbq in Vquartersahead]
    #Scon = 'gdpr$';

    if Sxaxis == 'iYear':
        Vx = Vyears
        Vx2 = Vquartersahead
        Vlabels = [str(y) for y in Vyears]
        Stitle = 'Year projected'
    else:
        Vx = Vquartersahead
        Vx2 = Vyears   
        Vlabels = [str(int(-nbq*3)) + 'M' for nbq in Vquartersahead]
        Stitle = '# Months ahead'
    
    if Scharttype == 'Bars' and Smode == 'Cumul':
        fig.update_layout({"title": {"text": "Forecast error by year of forecast and time of projection","font": {"size": 14}},'barmode': 'stack','xaxis':{'title':Stitle},'yaxis':{'tickformat':'.2%','title':'Absolute forecast error'}})
    else:
        fig.update_layout({"title": {"text": "Forecast error by year of forecast and time of projection","font": {"size": 14}},'xaxis':{'title':Stitle},'yaxis':{'tickformat':'.2%','title':'Absolute forecast error'}})

    Vlabels = [''] + Vlabels if Scharttype == 'Lines' and Smode == 'Cumul' else Vlabels
        
    for x2 in Vx2:
    
        Vy = [0] if Scharttype == 'Lines' and Smode == 'Cumul' else []
        #print(Vy);print(Vlabels)
        
        averror = 0
            
        for x in Vx:
            
            iYear = x if Sxaxis == 'iYear' else x2
            nbq = x2 if Sxaxis == 'iYear' else x 
            
            if Smode == 'Cumul' and Scharttype == 'Lines':
                averror = averror + fn_calc_aveerror(Scon + '_' + Siso,[iYear],nbq*3,'ihs')            
            else:
                averror = fn_calc_aveerror(Scon + '_' + Siso,[iYear],nbq*3,'ihs')
            
            Vy.append(averror)
        
        Sname = str(int(-nbq*3)) + 'M' if Sxaxis =='iYear' else str(x2)
        
        if Scharttype == 'Bars':
            fig.add_trace(plotlygraphs.Bar(x=Vlabels,y=Vy,name=Sname))                  
        else:
            fig.add_trace(plotlygraphs.Scatter(x=Vlabels,y=Vy,mode='lines+markers',name=Sname))
            
    return fig
@app.callback(Output('chart11', 'figure'),[Input('IsoSelection', 'value'),Input('MonthSelection','value'),Input('chart11iYear','value'),Input('chart11Serrorcontrib','value')])
def fn_create_chart11(Siso,Vmonthsahead,iYear,Smode):
    
    #iYear = 2018
        
    fig = plotlygraphs.Figure(chart_layout)
    Syear = str(iYear)
    fig.update_layout({"title": {"text": "Contributions to growth / error for year " + Syear,"font": {"size": 14}},'barmode': 'relative','xaxis':{'tickformat':'.2%','title':'# Months ahead'},'yaxis':{'tickformat':'.2%','title':'Contributions to growth / error'}})
    
    Vmonthsahead = sorted(Vmonthsahead,reverse = True)
    
    #Vy: GDP projection VS Vx: GDP gap at the time. 
    Vquartersahead = [i/3 for i in Vmonthsahead];Vx = [str(int(-nbq*3)) + 'M' for nbq in Vquartersahead]

    Vconcepts = ['cpvr','ifr','cgvr','iir','xr','mr','gdpr']
    Dicconcepts = {'cpvr':'Private consumption','ifr':'Investment','cgvr':'Public consumption','iir':'Inventory change','xr':'Exports','mr':'Imports (-)','gdpdisr':'Stat. discrepancy','gdpr':'Real GDP'}
    
    for Scon in Vconcepts:       
            
        Vy = []
        mrfact=1 if Scon != 'mr' else -1
        
        print(mrfact)
            
        for nbq in Vquartersahead:

            Sreleasedate = str(iYear+1) + 'Q2'            
            Svintage = fn_Qdate_offset(Sreleasedate,-nbq);Dvintage = fn_convert_Sdaterange([Svintage])
            Svintage = 'Q' + str(Dvintage[0].month//3) + fn_extract_leftmidright('right',str(Dvintage[0].year),2) 
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_ihs'
            
            Vdatapoint1 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear) + 'Q4')          
            Vdatapoint0 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear-1) + 'Q4')          

            Smnemonic = 'gdpr' + '_' + Siso + '_' + Svintage + '_ihs'
            Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear-1) + 'Q4')          
            
            contrib = (Vdatapoint1[0]-Vdatapoint0[0])/Vdatapoint[0]*mrfact
            Vy.append(contrib)

        Vy.append(None)
        #First estimate
        Svintage = 'Q2' + fn_extract_leftmidright('right',str(iYear+1),2)
        Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_ihs'
        Vdatapoint1 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear) + 'Q4');Vdatapoint0 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear-1) + 'Q4')          
        Smnemonic = 'gdpr' + '_' + Siso + '_' + Svintage + '_ihs'
        Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear-1) + 'Q4')          
        contrib = (Vdatapoint1[0]-Vdatapoint0[0])/Vdatapoint[0]*mrfact
        Vy.append(contrib);rebasefactor = contrib
        
        #Final
        Smnemonic = Scon + '_' + Siso + '_' + '0' + '_ihs'
        Vdatapoint1 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear) + 'Q4');Vdatapoint0 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear-1) + 'Q4')          
        Smnemonic = 'gdpr' + '_' + Siso + '_' + '0' + '_ihs'
        Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear-1) + 'Q4')          
        contrib = (Vdatapoint1[0]-Vdatapoint0[0])/Vdatapoint[0]*mrfact
        Vy.append(contrib)
        
        if Smode == 'Error':
            for i in range(0,len(Vy)):
                if Vy[i]!=None:
                    val = Vy[i]-rebasefactor
                else:
                    val = None
                Vy[i] = val
        
        if Scon != 'gdpr':
            fig.add_trace(plotlygraphs.Bar(x=Vx + [' ','First estimate','Final'],y=Vy,name=Dicconcepts[Scon]))                  
        else:
            fig.add_trace(plotlygraphs.Scatter(x=Vx + [' ','First estimate','Final'],y=Vy,mode='lines+markers',name=Dicconcepts[Scon],line=dict(color='black', dash='dash')))

    return fig
@app.callback(Output('chart12', 'figure'),[Input('IsoSelection', 'value'),Input('MonthSelection','value'),Input('chart12iYear','value'),Input('chart12Bexccountry','on')])
def fn_create_chart12(Siso,Vmonthsahead,iYear,Bexccountry):
    
    #iYear = 2018
    
    Sregion = Disos[Siso]['Region']
    Sregionname = Dregions[Sregion]
    
    #html.Span("floccinaucinihilipilification",id="chart13title")
    
    fig = plotly.tools.make_subplots(rows=2, cols=2, subplot_titles=( Sregionname + " - GDP (%y/y)", "Oil prices (year average)","World - GDP (%y/y)", "Fed funds rate (Q4 / Q4 increase, bps)"))     
    #fig.update_layout(chart_layout)    
    Stitle = 'Additional context indicators'
    
    if Bexccountry == True:
        Stitle = Stitle + ' (GDP aggregates are excluding) ' + Disos[Siso]['Name'] + ')'
    
    fig.update_layout({"title": {"text": 'Additional context indicators',"font": {"size": 14},'xanchor': 'center','yanchor': 'top','x':0.5},'barmode':'overlay',"showlegend": False})
    
    
    Vmonthsahead = sorted(Vmonthsahead,reverse = True)
    Vquartersahead = [i/3 for i in Vmonthsahead];Vx = [str(int(-nbq*3)) + 'M' for nbq in Vquartersahead]
    
    ####################################################################################################
    ####################################Chart creation######################################################
    ####################################################################################################
    #,'xaxis':{'tickformat':'.2%','title':'Time ahead'},'yaxis':{'tickformat':'.2%','title':'Forecast error'}
    
    Smnemos = ['gdpr$_' + Sregion,'gdpr$_world', 'poilbrent$','rmpolicy_usa']
    
    Dicchart = {
                'gdpr$_world':{'coords':[2,1],'Sfunc':'4q4q','Sreleasedate':str(iYear+1) + 'Q2','Sformat':'.1%'},
                'gdpr$_' + Sregion:{'coords':[1,1],'Sfunc':'4q4q','Sreleasedate':str(iYear+1) + 'Q2','Sformat':'.1%'},
                'poilbrent$':{'coords':[1,2],'Sfunc':'4qma','Sreleasedate':str(iYear) + 'Q4','Sformat':'0'},
                'rmpolicy_usa':{'coords':[2,2],'Sfunc':'q4q4diffbps','Sreleasedate':str(iYear) + 'Q4','Sformat':'.2f'}
                }
    
    #Dichartcoords = {'gdpr$_world':[1,1],'gdpr$_' + Sregion : [2,1], 'poilbrent$':[1,2],'rmpolicy_usa':[2,2]}
    #Dichartfuncs = {'gdpr$_world':'4q4q','gdpr$_' + Sregion : '4q4q', 'poilbrent$':'4qma','rmpolicy_usa':'4qma'}
    #Dicreleasedates = {'gdpr$_world':str(iYear+1) + 'Q2','gdpr$_' + Sregion : str(iYear+1) + 'Q2', 'poilbrent$':str(iYear) + 'Q4','rmpolicy_usa':str(iYear) + 'Q4'}
    #Dicformats = {'gdpr$_world':str(iYear+1) + 'Q2','gdpr$_' + Sregion : str(iYear+1) + 'Q2', 'poilbrent$':str(iYear) + 'Q4','rmpolicy_usa':str(iYear) + 'Q4'}
    
    for Smnemo in Smnemos:
    
        Sfunc = Dicchart[Smnemo]['Sfunc'];
        
        #Cannot take 4qma, as there could be some revisions and changes of base years: cannot compare a level!
        Sreleasedate = Dicchart[Smnemo]['Sreleasedate'];Svintage = fn_extract_leftmidright('right',Sreleasedate,2) + fn_extract_leftmidright('mid',Sreleasedate,2,2)
        Smnemonic = Smnemo + '_' + Svintage + '_ihs'
        Vdatapointref = fn_ping_dictdatabase(DictDatabase,Smnemonic,Sfunc,str(iYear) + 'Q4') #Rescale as well

        #Exclude country if the user wants
        if Bexccountry == True:
            Vdatapointlvl = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear) + 'Q4') #Regional GDP
            if fn_extract_leftmidright('left',Smnemo,4) == 'gdpr':
                Smnemonic = 'gdpr$' + '_' + Siso + '_' + Svintage + '_ihs'
                Ddollgdp2010 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear) + 'Q4')
                Disogdpgrowth = fn_ping_dictdatabase(DictDatabase,Smnemonic,Sfunc,str(iYear) + 'Q4')
                Vdatapointref[0] = (Vdatapointref[0]-Disogdpgrowth[0]*Ddollgdp2010[0]/Vdatapointlvl[0])/(1-Ddollgdp2010[0]/Vdatapointlvl[0])

        Vybars = [];Vy = []

        for nbq in Vquartersahead:

            Svintage = fn_Qdate_offset(Sreleasedate,-nbq);Dvintage = fn_convert_Sdaterange([Svintage])
            Svintage = 'Q' + str(Dvintage[0].month//3) + fn_extract_leftmidright('right',str(Dvintage[0].year),2) 
            Smnemonic = Smnemo + '_' + Svintage + '_ihs'
            Vdatapoint = fn_ping_dictdatabase(DictDatabase,Smnemonic,Sfunc,str(iYear) + 'Q4')           
                        
            #Exclude country if the user wants
            if Bexccountry == True:
                Vdatapointlvl = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear) + 'Q4') #Regional GDP
                if fn_extract_leftmidright('left',Smnemo,4) == 'gdpr':
                    Smnemonic = 'gdpr$' + '_' + Siso + '_' + Svintage + '_ihs'
                    Ddollgdp2010 = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear) + 'Q4')
                    Disogdpgrowth = fn_ping_dictdatabase(DictDatabase,Smnemonic,Sfunc,str(iYear) + 'Q4')
                    Vdatapoint[0] = (Vdatapoint[0]-Disogdpgrowth[0]*Ddollgdp2010[0]/Vdatapointlvl[0])/(1-Ddollgdp2010[0]/Vdatapointlvl[0])
                    
            
            #if nbq == Vquartersahead[0]:

            Vybars.append(Vdatapoint[0])
                
            #else:
                
                #Vybars.append(None)
 
            Vy.append(Vdatapoint[0])

        Vybars.append(Vdatapointref[0]);Vy.append(Vdatapointref[0])
        #fig.update_xaxes(title_text="xaxis 2 title", range=[10, 50], row=1, col=2)
        iRow=Dicchart[Smnemo]['coords'][0];iCol= Dicchart[Smnemo]['coords'][1]
        Sformat = Dicchart[Smnemo]['Sformat']
        
        Dmin = min(Vy); Dmax = max(Vy)
        
        if Dmin>0:
            Dmin = Dmin*0.99
        else:
            Dmin = Dmin*1.01
            
        if Dmax>0:
            Dmax = Dmax*1.01
        else:
            Dmax = Dmax*0.99
            
        #Remove last point, as it is the first estimate, or make it none
        Vybars[len(Vybars)-1] = None

        fig.add_trace(plotlygraphs.Bar(x=Vx + ['First estimate'],y=Vybars),row=iRow, col=iCol)
        fig.add_trace(plotlygraphs.Bar(x=['First estimate'],y=Vdatapointref,marker_color=['black']),row=iRow, col=iCol)
        #fig.add_trace(plotlygraphs.Scatter(x=Vx + ['First estimate'],y=Vy,mode='lines+markers',line=dict(color='black')), row=iRow, col=iCol)
        fig.update_yaxes({'tickformat':Sformat,'range':[Dmin,Dmax]},row=iRow, col=iCol)
        #fig.update_layout({'barmode': 'overlay'},row=iRow, col=iCol)
        
    return fig
# if x, y and z here, solar system mandatory
#if target selected, z disabled
@app.callback([Output('chart13iYearZ', 'disabled')],[Input('chart13Smode','value')])
def set_button_enabled_stateiZ(Smode):
    
    if Smode =='Target':
        return [True]
    else:
        return [False]

@app.callback(Output(component_id='chart13', component_property='figure'),
              [Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('chart13iYearX','value'),Input('chart13iYearY','value'),Input('chart13iYearZ','value'),Input('chart13nbq','value'),
               Input('chart13c1','value'),Input('chart13c2','value'),Input('chart13c3','value'),
              Input('chart13c4','value'),Input('chart13c5','value'),Input('chart13Scatsplit','value'),Input('chart13Smode','value')])
def fn_create_chart13(Scon,Sisolcountries,iYearX,iYearY,iYearZ,nbq,c1,c2,c3,c4,c5,Scatsplit,Smode):

    import math 
    import random
    
    Smsg = "Cest le cercle"
    
    config={'config':{'modeBarButtonsToAdd':{'name': 'How to read this chart','icon': 'lockIcon'}}}#,'click': "function() => { alert('clicked custom button!')"}
    
    #'autorange':'reversed'
    fig = plotlygraphs.Figure(chart_layout)
        
    if Smode == 'Target':
        iYearZ = None
    
    #iYearX = iYear;iYearY = None;iYearZ=None
    
    Saxes = '';Vyears = []
    if iYearX!=None:
        Saxes = Saxes + 'x';Vyears.append(iYearX);Sx = 'Forecast error - ' + str(iYearX)
    else:
        Sx=''
        
    if iYearY!=None:
        Saxes = Saxes + 'y';Vyears.append(iYearY);Sy = 'Forecast error - ' + str(iYearY)
    else:
        Sy=''
        
    if iYearZ!=None:
        Saxes = Saxes + 'z';Vyears.append(iYearZ);Sz = 'Forecast error - ' + str(iYearZ)
    else:
        Sz=''

    if Smode == 'Target':
        fig.update_layout({"title": {"text": "Forecast error - All countries","font": {"size": 14}},'xaxis':{'tickformat':'.2%','title':Sx},
                           'yaxis':{'scaleanchor':'x', 'scaleratio':1,'tickformat':'.2%','title':Sy}})#'legend': {'bgcolor':'rgba(0,0,0,0)','yanchor': 'middle','xanchor': 'right','x': 0.99,'y':0.5}})
    else:
        fig.update_layout({"title": {"text": "Forecast error - All countries","font": {"size": 14}},
                        'scene':{'xaxis':{'title':Sx,'tickformat':'.2%'},'yaxis':{'title':Sy,'tickformat':'.2%'},'zaxis':{'title':Sz,'tickformat':'.2%'}}})
        fig.update_scenes(xaxis_autorange="reversed")
        fig.update_scenes(yaxis_autorange="reversed")

        #'legend': {'bgcolor':'rgba(0,0,0,0)','yanchor': 'middle','xanchor': 'right','x': 0.99,'y':0.5}})

        
    compteuraxes = len(Saxes)
        
    if Saxes == '':
        return fig
    
    #Params to integrate
    #iYear = 2018
    #c1 = '0.2%, green';c2 = '0.5%,lightblue';c3 = '1%,orange';c4 = '2%,pink';c5 = '5%,red'
    #Scatsplit='Regions'#'Error magnitude'#'Regions'
    #Smode = 'Solar system'#'Target'
    
    nbq = nbq/3
    Scon = 'gdpr$'
    
    Vcircles = [c1,c2,c3,c4,c5];Vcircles = fn_split_circleparams(Vcircles,True)
    Vregions = ['Western Europe,blue','CEE,cyan','North America,red','Asia Pacific,green','LATAM,orange','MENA,grey','Africa,brown'];Vregions = fn_split_regionparams(Vregions,False)    
        
    #Sdate = str(iYear)
    Visos = ['can' ,'mex' ,'usa' ,'aut' ,'bel' ,'che' ,'cyp' ,'deu' ,'dnk' ,'esp' ,'fin' ,'fra' ,'gbr' ,'grc' ,'irl' ,'ita' ,'lux' ,'mlt' ,'nld' ,'nor' ,'prt' ,'swe' ,'bgr' ,'cze' ,'est' ,'hrv' ,'hun' ,'ltu' ,'lva' ,'pol' ,'rou' ,'rus' ,'svk' ,'svn' ,'ago' ,'nga' ,'zaf' ,'are' ,'dza' ,'egy' ,'irn' ,'isr' ,'kwt' ,'mar' ,'qat' ,'sau' ,'tun' ,'tur' ,'arg' ,'bra' ,'chl' ,'col' ,'per' ,'aus' ,'chn' ,'hkg' ,'idn' ,'ind' ,'jpn' ,'kor' ,'mys' ,'nzl' ,'phl' ,'sgp' ,'tha' ,'twn' ,'vnm']

    #Svintage = str(iYear + 1) + 'Q2';Svintage_actual = Svintage
    #Svintage = fn_Qdate_offset(Svintage,-nbq)
    #Dvintage = fn_convert_Sdaterange([Svintage])
    #Svintage_compa = 'Q' + str(Dvintage[0].month//3) + fn_extract_leftmidright('right',str(Dvintage[0].year),2) 
        
    #1 put all the gaps in an array and the associated countries too
    Vy = [];Visols=[]
    
    for Siso in Visos:

        Vgaps = [];usdmiss=0
        
        for iYear in Vyears:
        
            Sreleasedate = str(iYear+1) + 'Q2';Sreleasevintage = 'Q2' + fn_extract_leftmidright('mid',Sreleasedate,2,2)       
            Smnemonic = Scon + '_' + Siso + '_' + Sreleasevintage + '_ihs'                
            Vy_actual = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(iYear) + 'Q4') #Actual

            Svintage = fn_Qdate_offset(Sreleasedate,-nbq);Dvintage = fn_convert_Sdaterange([Svintage])
            Svintage = 'Q' + str(Dvintage[0].month//3) + fn_extract_leftmidright('right',str(Dvintage[0].year),2) 
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_ihs'        
            Vy_predicted = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(iYear) + 'Q4') #Predicted

            Smnemonic = 'gdpr$' + '_' + Siso + '_' + '0' + '_ihs'
            Vy_size = fn_ping_dictdatabase(DictDatabase,Smnemonic,'4qma',str(iYear) + 'Q4') #Size
            
            gap=Vy_predicted[0]-Vy_actual[0]
            Vgaps.append(gap);usdmiss = usdmiss + abs(gap*Vy_size[0])
        
        usdmiss = usdmiss/compteuraxes
        
        rnd = random.uniform(0, 1);rnd2 = random.uniform(0, 1);rnd3 = random.uniform(0, 1);rnd4 = random.uniform(0, 1)
                
        if compteuraxes==1:
        
            x = Vgaps[0]*rnd;
        
            y=math.sqrt(abs(gap)**2-x**2);z=0
        
            if Smode!='Target':
                y=y*rnd3
                z = math.sqrt(abs(Vgaps[0])**2-x**2-y**2)
                
            if rnd2>0.5: #SQRT(gap^2-x^2)*IF(@fn_nonvol_randomize()>0.5,-1,1)
                y = -y        
            if rnd4>0.5:
                z = -z        

            x2 = x;y2 = y;z2=z
                
            if Saxes == 'y':
                y = x2;x = y2
            if Saxes == 'z':
                z = x2;x = z2
                
        if compteuraxes==2:
        
            x = Vgaps[0];
        
            y=Vgaps[1];z=0
        
            if Smode!='Target':
                x = x*rnd;y = y*rnd2
                z = math.sqrt(Vgaps[0]**2+Vgaps[1]**2-x**2-y**2)
                
            if rnd4>0.5:
                z = -z        

            x2 = x;y2 = y;z2=z
                
            if 'y' in Saxes and 'z' in Saxes:
                y = x2;z = y2;x = z2

            if 'x' in Saxes and 'z' in Saxes:
                z = y2;y = z2

        if compteuraxes==3:
        
            x = Vgaps[0];
        
            y=Vgaps[1];z=Vgaps[2]                
                
        Vmat = [Siso,max([abs(gap) for gap in Vgaps]),x,y,z,usdmiss];Vy.append(Vmat)
        
        if Siso in Sisolcountries:
            Visols.append(Vmat)
 
    #Put series in appropriate traces
    if Scatsplit=='Error magnitude':
    
        Sid= ''    

        for Vcircle in Vcircles:

            Vyy = [];Vx = [];Visos = [];Vz = [];Vmiss = []

            for Vmat in Vy:

                Siso = Vmat[0];gap = Vmat[1];x = Vmat[2];y = Vmat[3];z = Vmat[4];usdmiss=Vmat[5]

                if abs(gap)<Vcircle[1] and Sid.find(Siso) == -1:# and Sisolcountries.find(Siso) == -1:
                    Vyy.append(y);Vx.append(x);Visos.append(Siso);Vz.append(z);Vmiss.append(usdmiss)
                    Sid = Sid + ' ' + Siso

            if Smode=='Target':
                fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyy,mode='markers+text',name = 'Miss <' + Vcircle[0],textposition="bottom center",textfont=dict(color=Vcircle[2]),text = Visos,marker=dict(size=7,color=Vcircle[2]))) #text = Visos                    
            else:
                fig.add_trace(plotlygraphs.Scatter3d(x=Vx,y=Vyy,z=Vz,mode='markers+text',name = 'Miss <' + Vcircle[0],textposition="bottom center",textfont=dict(color=Vcircle[2]),text = Visos,marker=dict(color=Vcircle[2],size = Vmiss))) #text = Visos

    if Scatsplit == 'Regions':

        Ddict={'aut':'Western Europe','bel':'Western Europe','bgr':'CEE','chn':'Asia Pacific','hrv':'CEE','cyp':'Western Europe','cze':'CEE','dnk':'Western Europe','est':'CEE','fin':'Western Europe','fra':'Western Europe','deu':'Western Europe','grc':'Western Europe','hun':'CEE','irl':'Western Europe','ita':'Western Europe','jpn':'Asia Pacific','lva':'CEE','ltu':'CEE','lux':'Western Europe','mlt':'Western Europe','nld':'Western Europe','pol':'CEE','prt':'Western Europe','rou':'CEE','svk':'CEE','svn':'CEE','esp':'Western Europe','swe':'Western Europe','gbr':'Western Europe','usa':'North America','are':'MENA','arg':'LATAM','aus':'Asia Pacific','bra':'LATAM','can':'North America','che':'Western Europe','idn':'Asia Pacific','ind':'Asia Pacific','isr':'MENA','kor':'Asia Pacific','kwt':'MENA','mex':'North America','nor':'Western Europe','phl':'Asia Pacific','rus':'CEE','sau':'MENA','tha':'Asia Pacific','tur':'MENA','zaf':'Africa','ago':'Africa','chl':'LATAM','col':'LATAM','dza':'MENA','egy':'MENA','hkg':'Asia Pacific','irn':'MENA','mar':'MENA','mys':'Asia Pacific','nga':'Africa','nzl':'Asia Pacific','per':'LATAM','qat':'MENA','sgp':'Asia Pacific','tun':'MENA','twn':'Asia Pacific','ven':'LATAM','vnm':'Asia Pacific'}
        Sid= ''
        
        for Vregion in Vregions:
            
            Vyy = [];Vx = [];Visos = [];Vz = [];Vmiss = []
        
            for Vmat in Vy:

                Siso = Vmat[0];gap = Vmat[1];x = Vmat[2];y = Vmat[3];z = Vmat[4];usdmiss=Vmat[5]
            
                if Ddict[Siso] == Vregion[0] and Sid.find(Siso) == -1:# and Sisolcountries.find(Siso) == -1:
                    Vyy.append(y);Vx.append(x);Visos.append(Siso);Vz.append(z);Vmiss.append(usdmiss)
                    Sid = Sid + ' ' + Siso
            
            if Smode=='Target':
                fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyy,mode='markers+text',name = Vregion[0],textposition="bottom center",textfont=dict(color=Vregion[1]),text = Visos,marker=dict(size=7,color=Vregion[1]))) #text = Visos
            else:
                fig.add_trace(plotlygraphs.Scatter3d(x=Vx,y=Vyy,z=Vz,mode='markers+text',name = Vregion[0],textposition="bottom center",textfont=dict(color=Vregion[1]),text = Visos,marker=dict(color=Vregion[1],size = Vmiss))) #text = Visos
        
    #Dealwith circles
    for Vcircle in Vcircles:
        
        if Smode=='Target':
            Vc = fn_draw_circle(Vcircle[1],0,0,0,'2d')
            fig.add_trace(plotlygraphs.Scatter(x=Vc[0],y=Vc[1],name = Vcircle[0] + ' miss',mode='lines',line=dict(color=Vcircle[2], dash='dash'))) #text = Visos
        else:
            Vc = fn_draw_circle(Vcircle[1],0,0,0,'3d')
            fig.add_trace(plotlygraphs.Scatter3d(x=Vc[0],y=Vc[1],z=Vc[2],name = Vcircle[0] + ' miss',mode='lines',line=dict(color=Vcircle[2],width=1))) #text = Visos ;dash='dash'

    #'Countries' not yet treated as loss too large
    Vyy = [];Vx = [];Visos = [];Vz = [];Vmiss=[]
    for Vmat in Vy:

        Siso = Vmat[0];gap = Vmat[1];x = Vmat[2];y = Vmat[3];z=Vmat[4];usdmiss=Vmat[5]

        if Sid.find(Siso) ==-1 and Sisolcountries.find(Siso)==-1:
            Vyy.append(y);Vx.append(x);Visos.append(Siso);Vz.append(z);Vmiss.append(usdmiss)
            Sid = Sid + ' ' + Siso

    if Smode=='Target':
        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyy,mode='markers+text',name = 'Larger miss',textposition="bottom center",textfont=dict(color='darkviolet'),text = Visos,marker=dict(size=7,color='darkviolet'))) #text = Visos
    else:
        fig.add_trace(plotlygraphs.Scatter3d(x=Vx,y=Vyy,z=Vz,mode='markers+text',name = 'Larger miss',textposition="bottom center",textfont=dict(color='darkviolet'),text = Visos,marker=dict(color='darkviolet',size = Vmiss))) #text = Visos

    #Deal with isolated countries
    if len(Sisolcountries)>0:
      
        Vyy = [];Vx = [];Visos = [];Vz=[];Vmiss=[]
        
        for Vmat in Visols:
        
            Siso = Vmat[0];gap = Vmat[1];x = Vmat[2];y = Vmat[3];z = Vmat[4];usdmiss=Vmat[5]
            Vyy.append(y);Vx.append(x);Visos.append(Siso);Vz.append(z);Vmiss.append(usdmiss)
        
        if Smode=='Target':    
            fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyy,mode='markers+text',name = 'Isol: ' + Sisolcountries,textposition="bottom center",textfont=dict(color='black'),text = Visos,marker=dict(size=7,color='black'))) #text = Visos
        else:
            fig.add_trace(plotlygraphs.Scatter3d(x=Vx,y=Vyy,z=Vz,mode='markers+text',name = 'Isol: ' + Sisolcountries,textposition="bottom center",textfont=dict(color='black'),text = Visos,marker=dict(color='black',size = Vmiss))) #text = Visos
    
    #plotlygraphs.FigureWidget(fig,config)

    return fig
@app.callback(Output('chart14Btunnel', 'disabled'),[Input('chart14Sxaxis','value'),Input('chart14Schartmode','value')])
def set_button_enabled_state(Sxaxis,Smode):
    
    if Sxaxis == 'Years' and Smode == 'Lines':
        return False
    else:
        return True

@app.callback(Output('chart14Bstd', 'disabled'),[Input('chart14Sxaxis','value'),Input('chart14Schartmode','value')])
def set_button_enabled_state(Sxaxis,Smode):
    
    if Sxaxis == 'Years' and Smode == 'Lines':
        return False
    else:
        return True

@app.callback(Output(component_id='chart14', component_property='figure'),
              [Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('ProviderSelection','value'),Input('chart14SproviderMode','value'),
              Input('chart14Svintage','value'),Input('chart14Sxaxis','value'),Input('chart14Bcumul','on'),Input('chart14Schartmode','value'),Input('chart14Btunnel','on'),Input('chart14Bstd','on')])
def fn_create_chart14(Scon,Siso,Vproviders,Sdisplayproviders,Svintage,Sxaxis,Bcumul,Smode,Btunnel,Bstd):

    #To add: ranking (Calculate rank of each, then recreate Vproviders in the right order: easy); Add +- 1 STD, high low tunnel

    if Smode == 'Bars' or Sxaxis == 'Competitors':
        Btunnel = False;Bstd = False
        
    fig = plotlygraphs.Figure(chart_layout)    
    if Bcumul == True:
        Bnet = True
    else:
        Bnet = False
    
    Stitle = 'Forecast two years out vs competition'
    Stitle = Stitle + ' - ' + 'Vintage: ' + Svintage
    Stitle = Stitle + ' - ' + Dcons[Scon]
    Stitle = Stitle + ' - ' + Disos[Siso]['Name']
    
    if Bcumul == True:
        if Smode == 'Bars' and Sxaxis == 'Years':
            fig.update_layout({"title": {"text": Stitle,"font": {"size": 14}},'xaxis':{'tickformat':'0','dtick':1,'title':Sxaxis},'yaxis':{'tickformat':'.2%','title':'Cumulative forecast error'}})
        else:
            fig.update_layout({"title": {"text": Stitle,"font": {"size": 14}},'barmode': 'relative','xaxis':{'tickformat':'0','dtick':1,'title':Sxaxis},'yaxis':{'tickformat':'.2%','title':'Cumulative forecast error'}})
    else:
        fig.update_layout({"title": {"text": Stitle,"font": {"size": 14}},'xaxis':{'tickformat':'0','dtick':1,'title':Sxaxis},'yaxis':{'tickformat':'.2%','title':'Cumulative forecast error'}})    
    
    if Smode == 'Bars':
        Bcumulmemory = Bcumul
        Bcumul = False                    
    
    if Sdisplayproviders == 'Selection':
        if Vproviders!=None:
            Vproviders = ['ihs'] + Vproviders
        else:
            Vproviders = ['ihs']
    
    if Sdisplayproviders == 'All':
        Vcomps = fn_filter_competnames(Scon,Siso)
        Vproviders = ['ihs'] + Vcomps
        if 'std' in Vproviders:
            Vproviders.remove('std')
        
    if Btunnel == True:
        if 'high' in Vproviders:
            Vproviders.remove('high')
        if 'low' in Vproviders:
            Vproviders.remove('low')
        Vproviders.append('high')
        Vproviders.append('low')
        if 'std' in Vproviders:
            Vproviders.remove('std')            

        
    if Bstd==True:
        if 'std' in Vproviders:
            Vproviders.remove('std')            
        Vproviders.append('std')
        if 'cns' in Vproviders:
            Vproviders.remove('cns')            
        Vproviders.append('cns')
        
        
    Srefyear = '20' + fn_extract_leftmidright('right',Svintage,2)
    
    Vyears = [Srefyear,str(int(Srefyear)+1)]

    #Donwload data
    Ddic = {}
        
    for Sprovider in Vproviders + ['low','high','cns','std']:
    
        for Syear in Vyears: 
        
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + Sprovider
            Vval =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Syear + 'Q4')
            
            if Bcumul == True:
            
                if Syear != Vyears[0]:
                    
                    Valprev = Ddic[Sprovider + ' - ' + str(int(Syear)-1)]
                    
                    if Sprovider == 'std':
                        Valprev = 0
                    
                    Ddic[Sprovider + ' - ' + Syear] = Vval[0]+Valprev if (Vval[0] !=None and Valprev !=None) else None
                
                else:
            
                    Ddic[Sprovider + ' - ' + Syear] = Vval[0]
                
            else:
                
                Ddic[Sprovider + ' - ' + Syear] = Vval[0]
                
    Vynet = []
    
    for Sprovider in Vproviders:
    
        if Ddic[Sprovider + ' - ' + Srefyear] !=None and Ddic[Sprovider + ' - ' + str(int(Srefyear)+1)] !=None:
            
            Vynet.append(Ddic[Sprovider + ' - ' + Srefyear]+Ddic[Sprovider + ' - ' + str(int(Srefyear)+1)])
            
        else:

            Vynet.append(None)
            
    
    if Sxaxis == 'Years':
        
        Vx = Vyears
        
        for Sprovider in Vproviders:
        
            Vy = []
        
            for Syear in Vyears:
                           
                Vy.append(Ddic[Sprovider + ' - ' + Syear])
    
            if Smode == 'Lines':
            
                if Bcumul == True:

                    if (Btunnel == False and Bstd == False) or (Sprovider!='low' and Sprovider!='high' and Sprovider !='std'):
                        fig.add_trace(plotlygraphs.Scatter(x=[str(int(Srefyear)-1)] + Vx,y=[0] + Vy,mode='lines+markers',name = Dictproviders[Sprovider],text = '')) #text = Visos                    
            
                else:
            
                    if (Btunnel == False and Bstd == False) or (Sprovider!='low' and Sprovider!='high' and Sprovider !='std'):
                        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,mode='lines+markers',name = Dictproviders[Sprovider],text = '')) #text = Visos
            
            if Smode == 'Bars':

                if Bcumulmemory == True:
                    
                    if Vy[len(Vy)-1] !=None and Vy[len(Vy)-2] !=None :
                        Vy[len(Vy)-1] = Vy[len(Vy)-1] + Vy[len(Vy)-2]
                
                fig.add_trace(plotlygraphs.Bar(x=Vx,y=Vy,name = Dictproviders[Sprovider]))

    if Sxaxis == 'Competitors':
        
        Vx = Vproviders;Vx2 = [Dictproviders[Sprovider] for Sprovider in Vproviders]
        
        for Syear in Vyears:
        
            Vy = []
        
            for Sprovider in Vproviders:
                                
                Vy.append(Ddic[Sprovider + ' - ' + Syear])
    
            if Smode == 'Lines':

                if Btunnel == False:
                    fig.add_trace(plotlygraphs.Scatter(x=Vx2,y=Vy,mode='lines+markers',name = Syear,text = '')) #text = Visos

            if Smode == 'Bars':

                fig.add_trace(plotlygraphs.Bar(x=Vx2,y=Vy,name = Syear))                        
                
                if Syear==Vyears[len(Vyears)-1]:
                    
                    fig.add_trace(plotlygraphs.Scatter(x=Vx2,y=Vynet,mode='markers',name = 'Sum',marker=dict(color='Black',size=12)))
                    
    if Btunnel == True:
        
        for Sprovider in ['low','high']:

            Vy = []

            if Bcumul == True:
                Vx = [str(int(Srefyear)-1)] + Vyears
                Vy = [0]            
            
            for Syear in Vyears:

                Vy.append(Ddic[Sprovider + ' - ' + Syear])

            if Sprovider == 'low':
                fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,fill=None,mode='lines',line_color='rgba(192,192,192,0)',name = 'Tunnel min',showlegend=False))  
            else:
                fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vy,fill='tonexty',mode='lines',line_color='rgba(192,192,192,0)',name = 'Max/min tunnel'))

    if Bstd == True:
        
        Vyminus = [];Vyplus = []

        if Bcumul == True:
            Vx = [str(int(Srefyear)-1)] + Vyears
            Vyminus = [0];Vyplus = [0]            

        for Syear in Vyears:

            if 'cns' + ' - ' + Syear in Ddic and 'std' + ' - ' + Syear in Ddic:
                Vyminus.append(Ddic['cns' + ' - ' + Syear]-Ddic['std' + ' - ' + Syear])
                Vyplus.append(Ddic['cns' + ' - ' + Syear]+Ddic['std' + ' - ' + Syear])
            else:
                Vyminus.append(None)
                Vyplus.append(None)
                
        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyminus,fill=None,mode='lines',line_color='rgba(255,192,203,0)',name = 'CNS - 1 stdev',showlegend=False))  
        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyplus,fill='tonexty',mode='lines',line_color='rgba(255,192,203,0)',name = '(+)/(-) 1 STD'))
            
                
    return fig
@app.callback(Output(component_id='chart15', component_property='figure'),
              [Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('ProviderSelection','value'),Input('chart15Svintage','value'),Input('chart15Sstep','value'),
               Input('chart15Smode','value'),Input('chart15Spointsize','value'),Input('chart15Syear', 'value')])
def fn_create_chart15(Scon,Siso,Vproviders,Svintage,Sstep,Smode,Spointsize,Swhatyear):

    Syear = '20' + fn_extract_leftmidright('right',Svintage,2)
        
    if Swhatyear == 'Next':
        Syear = str(int('20' + fn_extract_leftmidright('right',Svintage,2))+1)    
    
    #Smode: Labels, Scatter, Both
    Stitle = 'Dispersion of forecasts'
    Stitle = Stitle + ' - ' + 'Vintage: ' + Svintage
    Stitle = Stitle + ' - ' + Dcons[Scon]
    Stitle = Stitle + ' - ' + Disos[Siso]['Name']
    Stitle = Stitle + '<br>' + 'Year: ' + Syear
    
    if Swhatyear == 'Cumul':
        Stitle = Stitle + '-' + fn_extract_leftmidright('right',str(int(Syear)+1),2,1) + ' (cumul)'
    if Swhatyear == 'Average':
        Stitle = Stitle + '-' + fn_extract_leftmidright('right',str(int(Syear)+1),2,1) + ' (avg)'
    
    fig = plotlygraphs.Figure(chart_layout)    
    fig.update_layout({"title": {"text": Stitle,"font": {"size": 14}},'xaxis':{'title':'Forecast'},'yaxis':{'title':'Number of providers'}})
    fig.update_layout({'xaxis':{'tickformat':'.1%'},'yaxis':{'tickformat':'0'}})
    #'legend': {'x': 0, 'y': -2, 'orientation': 'h'}
    
    Sproviders = ""
    if Vproviders != None:
        for Sprovider in Vproviders:
            Sproviders = Sproviders + " " + Sprovider
    
    Vcomps = fn_filter_competnames(Scon,Siso)
    
    nbcategories = 10
    
    Vproviders = ['ihs'] + Vcomps
        
    Ddic = {}
    
    maxi = -1000;mini = 1000
    
    for Sprovider in Vproviders:

        Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + Sprovider
        
        Vval =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Syear + 'Q4')
        
        if Swhatyear == 'Cumul' or Swhatyear == 'Average':
            Vval2 =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+1) + 'Q4')        
            if Vval[0]!=None and Vval2[0]!=None:
                Vval[0] = Vval[0]+Vval2[0]
                if Swhatyear == 'Average':
                    Vval[0]=Vval[0]/2
            else:
                Vval[0]=None
        
        if Vval[0]!=None:
                
            if Sprovider != 'std' and Sprovider !='high' and Sprovider != 'low':
                Ddic[Sprovider] = Vval[0]
                if Vval[0]<=mini:
                    mini = Vval[0]
                if Vval[0]>=maxi:
                    maxi = Vval[0]
    
    mini2 = round(mini,3)
    if mini2 > mini:
        mini2 = mini2 - 0.001
    maxi2 = round(maxi,3)
    if maxi2 < maxi:
        maxi2 = maxi2 + 0.001
     
    # initializing start value  
    strt = mini2
    if '%' in Sstep:
        fac = 1/100
        Sstep = Sstep.replace("%", "")
    else:
        fac = 1
        
    step = float(Sstep)*fac
    fig.update_xaxes(showgrid=True, gridwidth=step, gridcolor='LightGray')
    #fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    Vx = [strt + (x * step) for x in range(0,int((maxi2-mini2)*1000)+1)] 
    
    #Vx = [i/1000 for i in range(int(mini2*1000),int(maxi2*1000)+1,istep*1000)]
    #print(Vx)
    #linspace_perso(mini2,maxi2, int((maxi2-mini2)/0.001))
    
    Vcompteurs = [0 for i in range(0,len(Vx)-1)] #len-1
    compteur_last = 0
    
    Vxx = [];Vxihs = [];Vxselected = [];Vxothers = [];Vxcns = []
    Vy = [];Vyihs = [];Vyselected = [];Vyothers = [];Vycns = []
    DVylabels = {};DVylabels['IHS'] = [];DVylabels['Consensus'] = [];DVylabels['Selected providers'] = [];DVylabels['Other providers'] = []
    
    for Sprovider in Ddic:
        
        Dval = Ddic[Sprovider]
        Sfound = "no"
        Sprovtype = ""
        
        if Sprovider == 'ihs':
            Sprovtype = 'IHS'
        if Sprovider == 'cns':
            Sprovtype = 'Consensus'
        if Sprovider in Sproviders:
            Sprovtype = 'Selected providers'
        if Sprovtype == '':
            Sprovtype = 'Other providers'
    
        for i in range(1,len(Vx)):
    
            if Vx[i-1]<=Dval and Vx[i]>Dval and Sprovider != "std":
                
                Sfound = "yes"
                Vcompteurs[i-1]=Vcompteurs[i-1]+1
                
                if Sprovtype == 'IHS':
                    Vxihs.append(Vx[i-1]*0.5+Vx[i]*0.5)
                    Vyihs.append(Vcompteurs[i-1])

                if Sprovtype == 'Selected providers':
                    Vxselected.append(Vx[i-1]*0.5+Vx[i]*0.5)
                    Vyselected.append(Vcompteurs[i-1])

                if Sprovtype == 'Consensus':
                    Vxcns.append(Vx[i-1]*0.5+Vx[i]*0.5)
                    Vycns.append(Vcompteurs[i-1])
                
                if Sprovtype == 'Other providers':
                    Vxothers.append(Vx[i-1]*0.5+Vx[i]*0.5)
                    Vyothers.append(Vcompteurs[i-1])
    
                DVylabels[Sprovtype].append(Dictproviders[Sprovider])
         
        if Sfound == 'no': #Case where max
            compteur_last = compteur_last+1
            if Sprovtype == 'IHS':
                Vxihs.append(Vx[len(Vx)-1]+(Vx[len(Vx)-1]-Vx[len(Vx)-2])/2)
                Vyihs.append(compteur_last)

            if Sprovtype == 'Selected providers':
                Vxselected.append(Vx[len(Vx)-1]+(Vx[len(Vx)-1]-Vx[len(Vx)-2])/2)
                Vyselected.append(compteur_last)

            if Sprovtype == 'Consensus':
                Vxcns.append(Vx[len(Vx)-1]+(Vx[len(Vx)-1]-Vx[len(Vx)-2])/2)
                Vycns.append(compteur_last)

            if Sprovtype == 'Other providers':
                Vxothers.append(Vx[len(Vx)-1]+(Vx[len(Vx)-1]-Vx[len(Vx)-2])/2)
                Vyothers.append(compteur_last)

            DVylabels[Sprovtype].append(Dictproviders[Sprovider])
                
    ipointsize = int(Spointsize);
    if Smode == 'Labels':
        ipointsize = ipointsize + 3
    
    #some_string.split(' ', 1)[0]
    
    if Vxihs != None:
        if Smode == 'Scatter':
            fig.add_trace(plotlygraphs.Scatter(x=Vxihs,y=Vyihs,mode='markers',text=DVylabels['IHS'],name = 'IHS',marker=dict(color='Green',size=ipointsize)))
        if Smode == 'Labels':
            fig.add_trace(plotlygraphs.Scatter(x=Vxihs,y=Vyihs,mode='text',text=DVylabels['IHS'],name = 'IHS',textfont=dict(size=ipointsize,color="Green")))
    
    if Vxcns != None:
        if Smode == 'Scatter':
            fig.add_trace(plotlygraphs.Scatter(x=Vxcns,y=Vycns,mode='markers',text=DVylabels['Consensus'],name = 'Consensus',marker=dict(color='Red',size=ipointsize)))
        if Smode == 'Labels':
            fig.add_trace(plotlygraphs.Scatter(x=Vxcns,y=Vycns,mode='text',text=DVylabels['Consensus'],name = 'Consensus',textfont=dict(size=ipointsize,color="Red")))    
    
    if Vxselected != None:
        if Smode == 'Scatter':
            fig.add_trace(plotlygraphs.Scatter(x=Vxselected,y=Vyselected,mode='markers',text=DVylabels['Selected providers'],name = 'Sel. providers',marker=dict(color='Orange',size=ipointsize)))
        if Smode == 'Labels':
            fig.add_trace(plotlygraphs.Scatter(x=Vxselected,y=Vyselected,mode='text',text=DVylabels['Selected providers'],name = 'Sel. providers',textfont=dict(size=ipointsize,color="Orange")))    
    
    if Vxothers != None:
        if Smode == 'Scatter':
            fig.add_trace(plotlygraphs.Scatter(x=Vxothers,y=Vyothers,mode='markers',text=DVylabels['Other providers'],name = 'Oth. providers',marker=dict(color='blue',size=ipointsize)))
        if Smode == 'Labels':
            fig.add_trace(plotlygraphs.Scatter(x=Vxothers,y=Vyothers,mode='text',text=DVylabels['Other providers'],name = 'Oth. providers',textfont=dict(size=ipointsize,color="blue")))    
    
    Vxx = [];Vyy = [];maxx=-1000
    
    if Vxihs!=None:
        maxx = max(Vxihs + [maxx])
    if Vxcns!=None:
        maxx = max(Vxcns + [maxx])
    if Vxselected!=None:
        maxx = max(Vxselected + [maxx])
    if Vxothers!=None:
        maxx = max(Vxothers + [maxx])    
        
    #maxx = max(max(Vxihs),max(Vxcns),max(Vxselected),max(Vxothers))
    
    for i in range(1,len(Vx)):
        if Vx[i]<=maxx + step:
            Vxx.append(Vx[i]*0.5 + Vx[i-1]*0.5)
            Vyy.append(Vcompteurs[i-1]+2)
    
    fig.add_trace(plotlygraphs.Scatter(x=Vxx,y=Vyy,mode='lines',name = 'Density',marker=dict(color='black')))
    
    ########################
    #######Actual?##########
    ########################
    Svintage = 'Q2' + str(int(fn_extract_leftmidright('right',Syear,2))+1)    
    Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + 'ihs'    
    Vval =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Syear + 'Q4')
    print(Vval[0])
    
    if Swhatyear == 'Cumul' or Swhatyear == 'Average':
        Svintage = 'Q2' + str(int(fn_extract_leftmidright('right',Syear,2))+2)    
        Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + 'ihs'
        Vval2 =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+1) + 'Q4')        
        if Vval[0]!=None and Vval2[0]!=None:
            Vval[0] = Vval[0]+Vval2[0]
            if Swhatyear == 'Average':
                Vval[0]=Vval[0]/2
        else:
            Vval[0]=None

    #Where ?
    if Vval[0]!=None:
        strt = int(Vval[0]/step)*step
        print(strt)
        #OK fig.add_shape(type="rect",x0=strt,y0=0,x1=strt + step,y1=max(Vyy),line=dict(color="RoyalBlue",width=1),fillcolor="LightSkyBlue")
        fig.add_trace(plotlygraphs.Scatter(x=[strt,strt + step],y=[max(Vyy),max(Vyy)],fill='tozeroy',fillcolor='rgba(0,255, 0, 0.3)',mode='none',name = 'First print'))
    
#    if Vval[0]!=None:    
#        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyyy[i],fill=None,mode='lines', line_color='rgba(' + str(stepcolor_rb) + ',' + str(stepcolor_g) + ',' + str(stepcolor_rb) + ',0)',name = 'Test',showlegend=False))  
#        fig.add_trace(plotlygraphs.Scatter(x=Vx,y=Vyyy[i+1],fill='tonexty', line_color = 'rgba(' + str(stepcolor_rb) + ',' + str(stepcolor_g) + ',' + str(stepcolor_rb) + ',0)',mode='lines',name = 'Test',showlegend=False))

        
        
        
    return fig
    
@app.callback(Output(component_id='chart16', component_property='figure'),
              [Input('ConceptSelection', 'value'),Input('IsoSelection', 'value'),Input('chart16Svintage','value'),Input('chart16Sstep','value'),
               Input('chart16Smode','value'),Input('chart16Spointsize','value'),Input('chart16Syear', 'value'),Input('chart16Sdisplay', 'value')])
def fn_create_chart16(Scon,Sisoselected,Svintage,Sstep,Smode,Spointsize,Swhatyear,Sdisplay):

    Syear = '20' + fn_extract_leftmidright('right',Svintage,2)
        
    if Swhatyear == 'Next':
        Syear = str(int('20' + fn_extract_leftmidright('right',Svintage,2))+1)    
    
    #Smode: Labels, Scatter, Both
    Stitle = 'Dispersion of forecasts around consensus'
    Stitle = Stitle + ' - ' + 'Vintage: ' + Svintage
    Stitle = Stitle + ' - ' + Dcons[Scon]
    Stitle = Stitle + '<br>' + 'Year: ' + Syear
    
    if Swhatyear == 'Cumul':
        Stitle = Stitle + '-' + fn_extract_leftmidright('right',str(int(Syear)+1),2,1) + ' (cumul)'
    if Swhatyear == 'Average':
        Stitle = Stitle + '-' + fn_extract_leftmidright('right',str(int(Syear)+1),2,1) + ' (avg)'
    
    if Sdisplay == 'gap':
        Sx = 'Gap with consensus (%) - (+) Above / (-) Below'
        Sx2 = '.1%'
    if Sdisplay == 'std':
        Sx = 'Gap with consensus (# standard deviations) - (+) Above / (-) Below'
        Sx2 = '0.0'
    
    fig = plotlygraphs.Figure(chart_layout)    
    fig.update_layout({"title": {"text": Stitle,"font": {"size": 14}},'xaxis':{'title':Sx},'yaxis':{'title':'Number of countries'}})
    fig.update_layout({'xaxis':{'tickformat':Sx2},'yaxis':{'tickformat':'0'}})

    Sprovider = 'ihs';Dvals = {}
    
    for Siso in Disos:
    
        #1) Retrieve IHS projection
        Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + Sprovider        
        Vval =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Syear + 'Q4')
        Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + 'cns'        
        Vvalcns =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Syear + 'Q4')        
        Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + 'std'        
        Vvalstd =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',Syear + 'Q4')        
    
        if Swhatyear == 'Cumul' or Swhatyear == 'Average':
            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + Sprovider
            Vval2 =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+1) + 'Q4')        
            if Vval[0]!=None and Vval2[0]!=None:
                Vval[0] = Vval[0]+Vval2[0]
                if Swhatyear == 'Average':
                    Vval[0]=Vval[0]/2
            else:
                Vval[0]=None

            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + 'cns'        
            Vvalcns2 =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+1) + 'Q4')        
            if Vvalcns[0]!=None and Vvalcns2[0]!=None:
                Vvalcns[0] = Vvalcns[0]+Vvalcns2[0]
                if Swhatyear == 'Average':
                    Vvalcns[0]=Vvalcns[0]/2
            else:
                Vvalcns[0]=None

            Smnemonic = Scon + '_' + Siso + '_' + Svintage + '_' + 'std'
            Vvalstd2 =  fn_ping_dictdatabase(DictDatabase,Smnemonic,'4q4q',str(int(Syear)+1) + 'Q4')        
            if Vvalstd[0]!=None and Vvalstd2[0]!=None:
                Vvalstd[0] = Vvalstd[0]+Vvalstd2[0]
                if Swhatyear == 'Average':
                    Vvalstd[0]=Vvalstd[0]/2
            else:
                Vvalstd[0]=None

        if Vval[0]!=None and Vvalcns[0]!=None:
            if Sdisplay == 'gap':
                Dvals[Siso] = Vval[0] - Vvalcns[0]
            if Sdisplay == 'std':
                if Vvalstd[0] !=None:
                    Dvals[Siso] = (Vval[0] - Vvalcns[0])/Vvalstd[0]
    
    print(Dvals)
    maxi = -1000000;mini = 10000000    
    
    for Siso in Dvals:  
        if Dvals[Siso]<=mini:
            mini = Dvals[Siso]
        if Dvals[Siso]>=maxi:
            maxi = Dvals[Siso]

    mini2 = round(mini,3)
    if mini2 > mini:
        mini2 = mini2 - 0.001
    maxi2 = round(maxi,3)
    if maxi2 < maxi:
        maxi2 = maxi2 + 0.001
     
    # initializing start value  
    strt = mini2
    if '%' in Sstep:
        fac = 1/100
        Sstep = Sstep.replace("%", "")
    else:
        fac = 1

    step = float(Sstep)*fac
    fig.update_xaxes(showgrid=True, gridwidth=step, gridcolor='LightGray')
    print(strt);print(step);print(mini2);print(maxi2)
    Vx = [strt + (x * step) for x in range(0,int((maxi2-mini2)*1000)+1)]      

    Vx.append(Vx[len(Vx)-1]+step)
    print(Vx)
    Vcompteurs = [0 for i in range(0,len(Vx)-1)] #len-1
    Dnewdic = {}

    Dregioncolors = {'Western Europe':'blue','CEE':'cyan','North America':'red','Asia Pacific':'green','LATAM':'orange','MENA':'grey','Africa':'brown'}    
    Ddict={'aut':'Western Europe','bel':'Western Europe','bgr':'CEE','chn':'Asia Pacific','hrv':'CEE','cyp':'Western Europe','cze':'CEE','dnk':'Western Europe','est':'CEE','fin':'Western Europe','fra':'Western Europe','deu':'Western Europe','grc':'Western Europe','hun':'CEE','irl':'Western Europe','ita':'Western Europe','jpn':'Asia Pacific','lva':'CEE','ltu':'CEE','lux':'Western Europe','mlt':'Western Europe','nld':'Western Europe','pol':'CEE','prt':'Western Europe','rou':'CEE','svk':'CEE','svn':'CEE','esp':'Western Europe','swe':'Western Europe','gbr':'Western Europe','usa':'North America','are':'MENA','arg':'LATAM','aus':'Asia Pacific','bra':'LATAM','can':'North America','che':'Western Europe','idn':'Asia Pacific','ind':'Asia Pacific','isr':'MENA','kor':'Asia Pacific','kwt':'MENA','mex':'North America','nor':'Western Europe','phl':'Asia Pacific','rus':'CEE','sau':'MENA','tha':'Asia Pacific','tur':'MENA','zaf':'Africa','ago':'Africa','chl':'LATAM','col':'LATAM','dza':'MENA','egy':'MENA','hkg':'Asia Pacific','irn':'MENA','mar':'MENA','mys':'Asia Pacific','nga':'Africa','nzl':'Asia Pacific','per':'LATAM','qat':'MENA','sgp':'Asia Pacific','tun':'MENA','twn':'Asia Pacific','ven':'LATAM','vnm':'Asia Pacific'}
    print('Test 12')
    
    for Siso in Dvals:    
    
        Dval = Dvals[Siso]
        Sregion = Ddict[Siso]
        
        for i in range(1,len(Vx)):

            if Vx[i-1]<=Dval and Vx[i]>Dval:

                Vcompteurs[i-1]=Vcompteurs[i-1]+1
                
                if Sregion in Dnewdic:
                    Dnewdic[Sregion]['x'].append(Vx[i]*0.5 + Vx[i-1]*0.5)
                    Dnewdic[Sregion]['y'].append(Vcompteurs[i-1])
                    Dnewdic[Sregion]['marks'].append(Disos[Siso]['Name'])                                    
                    x = Vx[i]*0.5 + Vx[i-1]*0.5;y=Vcompteurs[i-1];marks= Disos[Siso]['Name']
                else:
                    Dnewdic[Sregion] = {}
                    Dnewdic[Sregion]['x'] = [];Dnewdic[Sregion]['y'] = [];Dnewdic[Sregion]['marks'] = []
                    Dnewdic[Sregion]['x'].append(Vx[i]*0.5 + Vx[i-1]*0.5)
                    Dnewdic[Sregion]['y'].append(Vcompteurs[i-1])
                    Dnewdic[Sregion]['marks'].append(Disos[Siso]['Name'])                    
                    x = Vx[i]*0.5 + Vx[i-1]*0.5;y=Vcompteurs[i-1];marks= Disos[Siso]['Name']
                    
        if Siso == Sisoselected:
            Dnewdic['Isol: ' + Siso] = {}
            Dnewdic['Isol: ' + Siso]['x'] = [];Dnewdic['Isol: ' + Siso]['y'] = [];Dnewdic['Isol: ' + Siso]['marks'] = []
            Dnewdic['Isol: ' + Siso]['x'].append(x)
            Dnewdic['Isol: ' + Siso]['y'].append(y)
            Dnewdic['Isol: ' + Siso]['marks'].append(marks)                    

            
                    
    ipointsize = int(Spointsize);
    if Smode == 'Labels':
        ipointsize = ipointsize + 3
    maxx=-1000   
    
    for Sregion in Dnewdic:

        maxx = max(Dnewdic[Sregion]['x'] + [maxx])
        
        if Sregion == 'Isol: ' + Sisoselected:
            Scolo = 'black'
        else:
            Scolo = Dregioncolors[Sregion]
        
        if Smode == 'Scatter':
            fig.add_trace(plotlygraphs.Scatter(x=Dnewdic[Sregion]['x'],y=Dnewdic[Sregion]['y'],mode='markers',text=Dnewdic[Sregion]['marks'],name = Sregion,marker=dict(color=Scolo,size=ipointsize)))
        if Smode == 'Labels':
            fig.add_trace(plotlygraphs.Scatter(x=Dnewdic[Sregion]['x'],y=Dnewdic[Sregion]['y'],mode='text',text=Dnewdic[Sregion]['marks'],name = Sregion,textfont=dict(size=ipointsize,color=Scolo)))

    Vxx = [];Vyy = []

    for i in range(1,len(Vx)):
        if Vx[i]<=maxx + step:
            Vxx.append(Vx[i]*0.5 + Vx[i-1]*0.5)
            Vyy.append(Vcompteurs[i-1]+2)

    fig.add_trace(plotlygraphs.Scatter(x=Vxx,y=Vyy,mode='lines',name = 'Density',marker=dict(color='black')))
    
    return fig
    



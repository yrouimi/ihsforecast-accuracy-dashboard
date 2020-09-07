#https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20List.html#Textarea
#https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Basics.html
#https://chart-studio.plotly.com/~yves/895/streaming-several-traces-in-one-plot/#code
#https://community.plotly.com/t/how-can-i-determine-how-many-traces-exists-in-my-graph-and-what-are-those/6797
#https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20List.html
#https://stackoverflow.com/questions/57836356/update-plotly-fig-data-after-fig-show-in-python
#https://plotly.com/python/figurewidget/
#https://github.com/plotly/plotly.py/issues/1404
#https://jupyter-dashboards-layout.readthedocs.io/en/latest/using.html
#%load_ext jupyter_spaces

import pyeviews
import datetime as dt;from dateutil.relativedelta import relativedelta
import plotly.graph_objects as plotlygraphs
import plotly
from plotly.offline import iplot
from ipywidgets import interact, widgets
from IPython.display import display
import pythoncom
import dash_daq as daq

#***************************************************************************
#***************************************************************************
#***************************************************************************
#***********************EVIEWS FETCH FUNCTIONS******************************
#***************************************************************************
#***************************************************************************
#***************************************************************************

#pythoncom.CoInitialize()
#eviewsapp=pyeviews.GetEViewsApp(version='EViews.Manager.11',instance='existing', showwindow=True)

def fn_run_eviewsinstruction(eviewsapp,Sinstruction):

    #import pythoncom
    #pythoncom.CoInitialize()
    pyeviews.Run(Sinstruction, app=eviewsapp)
    #pythoncom.CoUninitialize()
    
def fn_get_eviewsvalue(eviewsapp,Sobjectname):
    
    #import pythoncom
    #pythoncom.CoInitialize()    
    Dval=pyeviews.Get(Sobjectname, app=eviewsapp)    
    #pythoncom.CoUninitialize()
    return Dval

def fn_get_eviewsdatapoint(eviewsapp,Sobjectname,Sdate):

    #import pythoncom
    #pythoncom.CoInitialize()
    Sinstruction = '@elem(' + Sobjectname + ',"' + Sdate + '")'
    Dval=pyeviews.Get(Sinstruction, app=eviewsapp)
    #pythoncom.CoUninitialize()
    return Dval

def fn_get_eviewsdatapoints(eviewsapp,Sobjectname,Sdaterange):

    valslist = []

    datelist = fn_create_datelist(Sdaterange,'Q')
    
    for Sdate in datelist:
        
        Dval = fn_get_eviewsdatapoint(eviewsapp,Sobjectname,Sdate)
        valslist.append(Dval)

    return valslist

def fn_build_dictdata(Spattern,Stype):#Retrieve eviews values and store them in a dictionary

    pythoncom.CoInitialize()
    eviewsapp=pyeviews.GetEViewsApp(version='EViews.Manager.11',instance='existing', showwindow=True)
    
    Sinstruction = '=@wlookup("' + Spattern + '","' + Stype + '")'
    Sseries = fn_get_eviewsvalue(eviewsapp, Sinstruction)
    
    Vdates = fn_create_datelist('2010Q1 2023Q4','Q')
    Vdatesshort = fn_create_datelist('2014Q1 2021Q4','Q')
    
    Vseriesname = Sseries.split()
        
    #Build a dictionary of dictionaries
    Ddictfull = {}

    for Smnemonic in Vseriesname:

        if 'ihs' in Smnemonic.lower():
            Vd = Vdates
        else:
            Vd = Vdatesshort
            
        Ddict={}
        
        for Sdate in Vd:
            
            Ddict[Sdate] = fn_get_eviewsdatapoint(eviewsapp,Smnemonic,Sdate)

        Ddictfull[Smnemonic.lower()] = Ddict

    pythoncom.CoUninitialize()
        
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
    
def fn_get_eviewsvalues(eviewsapp,Sobjectname,Soperation,Sdaterange):

    if len(Sdaterange)<=6:Sdaterange = Sdaterange + " " + Sdaterange
    valslist = [];datelist = fn_create_datelist(Sdaterange,'Q')
    fn_init_eviewscalculation(eviewsapp,Sobjectname,Soperation,Sdaterange)
    
    for Sdate in datelist:
        
        Dval = fn_get_eviewsdatapoint(eviewsapp,'yy',Sdate)
        valslist.append(Dval)

    if len(Sdaterange)<=6: #If only one date, then we want the point itself. Otherwise it gives a list
        return Dval     
    else:
        return valslist 

def fn_get_datapoint(eviewsapp,Sobjectname,Soperation,Sdate):

    import pythoncom
    pythoncom.CoInitialize()
    Sinstruction = '@elem(' + Sobjectname + ',"' + Sdate + '")'
    Dval=pyeviews.Get(Sinstruction, app=eviewsapp)
    pythoncom.CoUninitialize()
    return Dval
    
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

if __name__ == '__main__':
    app.run_server()

import physbits
import numpy as np
import math
import dataimport as di
import pathlib
from trmc_network import S11ghz
from curvefit_ks import curve_fit
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots




if False:
    dir = pathlib.Path('y:/math/comsol/ref data/2020-03-09 Cavity Tests')
    dir = pathlib.Path('u:/friedrich/TRMC/200810_TiO2_Sorbonne_2/')
    file1 = 'R_empty cavity_8300-9200_C2_60ms_1s.tdms'
    file2 = 'R_quartz_8300-8700_C2_60ms_1s.tdms'
    #file3 = 'R_AD-155_2L_800C_8300-8700_C2_60ms_1s.tdms' #sample data
    file3 = 'R_AD-155_4L_800C_8300-8700_C2_60ms_1s.tdms'

    # data of empty cavity with solid backplate from march
    file4 = 'c:/Users/scp/nextcloud/develop/python/misc/trmc-impedance/ref_data/2020-03-09 Cavity Tests/R-C2-empty-CuPlate064.tdms'
    d = di.read_tdms(file4)
    d_empty2 = d[1].values

    d = di.read_tdms(dir/file1)
    d_empty = d[0].values
    d = di.read_tdms(dir/file2)
    d_quartz = d[0].values
    d = di.read_tdms(dir/file3)
    d_sample = d[0].values

    x1 = d_empty[:,0] / 1000
    y1 = d_empty[:,1]

    x2 = d_quartz[:,0] / 1000
    y2 = d_quartz[:,1]

    x3 = d_sample[:,0] / 1000
    y3 = d_sample[:,1]

    x4 = d_empty2[:,0] / 1000
    y4 = d_empty2[:,1]


#################


def s11_func(freq_ghz,d1,d2,d_iris,loss_fac,copper_S,layer_t,layer_epsr,layer_sig,sub_t,sub_epsr,sub_sig):
    # helper function for fitting
    global s11
    s11.d1 = d1 #first distance in mm, distance between sample and cavity end
    s11.d2 = d2 # 'complementary' distance in mm
    s11.d_iris=d_iris # iris diameter in mm
    s11.loss_fac=loss_fac #copper loss adjustment 
    s11.layer_t=layer_t # layer thickness in mm
    s11.layer_epsr=layer_epsr #dieelectric constant layer
    #s11.layer_sig = layer_sig # conductance layer S/m
    s11.layer_sig = abs(layer_sig) # conductance layer S/m
    s11.sub_t=sub_t # substrate thickness in mm
    s11.sub_epsr=sub_epsr # substrate (quartz) epsr  
    s11.sub_sig = abs(sub_sig)
    s11.copper_S = abs(copper_S)
    # return np.array([s11.calc(x) for x in freq_ghz]) # freq_ghz is an array! , non numpy version   
    return s11.calc(freq_ghz) 


def  list_partition(list1D, columns=2):
    l = []    
    for k,p in enumerate(list1D):        
        col = k % columns        
        if col == 0  :            
            l.append([p] + [None]*(columns-1))     
            l[-1][0] = p       
        else :
            l[-1][col] = p
    return l

def parms_list(container,plist,kid=0):
    # creates a 
    cols = 2
    pl = list_partition(plist,cols)
    
    with container:
        ct = [None]*len(pl)
        #kid = 1
        for r,row in enumerate(pl):                    
            ct[r] = st.beta_columns(2*cols)
            plist[r*cols]['val'] = ct[r][0].number_input(row[0]['name'],value=float(row[0]['val']),format='%1.4e',key=kid)
            kid +=1
            plist[r*cols]['fixed'] = ct[r][1].checkbox('fixed',value=row[0]['fixed'],key=kid)
            kid +=1
            if cols>1 and row[1] :
                plist[r*2+1]['val'] = ct[r][2].number_input(row[1]['name'],value=float(row[1]['val']),format='%1.4e',key=kid)
                kid +=1
                plist[r*2+1]['fixed'] = ct[r][3].checkbox('fixed',value=row[1]['fixed'],key=kid)
    return(pl)        


s11 = S11ghz()
c = curve_fit(s11_func)
c.set('d1',35.825,False)
c.set('d2',11,True)
c.set('d_iris',9.6,False)
c.set('loss_fac',1e-7,False)
c.set('copper_S',5.5e7,True)
c.set('layer_t',0.001,True)
c.set('layer_epsr',1,True)
c.set('layer_sig',0,True)
c.set('sub_t',1,True) # by adding a substrate with eps=1 we account for the proper total cavity length
c.set('sub_epsr',1,True)
c.set('sub_sig',0,True)


st.beta_set_page_config(layout='wide',initial_sidebar_state='collapsed')
help = st.sidebar.button('Help')

if help :
    s = '''
    # help page
    this thing is in alpha state
    '''
    st.button('return')
    st.markdown(s)

else :

    # set the order of gui elements:
    area_graph = st.beta_container()
    datastream = st.file_uploader('ascii tab data with f in GHz')
    st.number_input('gehts',value=5.5)
    area_control = st.beta_container()
    st.markdown('**parameters:**')
    area_parms = st.beta_container() 
    pl = parms_list(area_parms,c.plist,kid=10000)
    c._calc_reduced()


    with area_control :
        c_cols = st.beta_columns(5)
        btn_calc = c_cols[0].button('calculate')
        if datastream:
            btn_fit = c_cols[1].button('fit')
        fmin = c_cols[2].number_input('fmin',value=6.5,format='%1.4f')
        fmax = c_cols[3].number_input('fmax',value=8.1,format='%1.4f')    
        fstep = c_cols[4].number_input('step',value=0.001,format='%1.4f')


    with area_graph:

        if True :        
            f = np.arange(fmin,fmax,fstep)
            y = c.calc(f)
            fig = px.line(x=f,y=y,log_y=False,title='plotly express',labels={'x':'frequency GHz','y':'S11 reflectivity'})
            st.plotly_chart(fig)
        else:
            fig = px.line(title='plotly express',labels={'x':'frequency GHz','y':'S11 reflectivity'})
            st.plotly_chart(fig)
            #st.markdown('no plot yet') # leaving the container emtpy causes weird problems!



# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 10:28:30 2020

@author: athus
"""

# Installs pyshp (Python Shapefile Library) which provides supports for read/write of shp files:
!pip install pyshp

# Import required libraries
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np 
import os

########################################################################

# Define functions needed to plot data:

#function to convert our 'shapefile' format to a Pandas dataframe format:
def read_shapefile(sf):
    """
    Read a shapefile into a Pandas dataframe with a 'coords' 
    column holding the geometry information.
    """
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shps = [s.points for s in sf.shapes()]    
    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)    
    return df

# data_spatial = read_shapefile(sf)

########################################################################

# Function to define colours of heat map
def calc_color(data, color=None):
           
        if   color == 1:
            colors = 'RdPu'   
            color_sq = ['#fcdcd9','#fbb9bc','#f887ac','#e7499b','#bb0f85','#800177'];   
        elif color == 2:
            colors = 'YlGnBu'   
            color_sq = ['#e8f6b1','#b2e0b6','#64c3be','#2ca0c1','#206cae','#243996'];   
        elif color == 3:
            colors = 'afmhot_r'   
            color_sq = ['#ffffb7','#ffec6d','#ffa424','#da5a00','#921200','#480000'];  
        elif color == 4:
            colors = 'rocket_r'   
            color_sq = ['#f6b48e','#f37651','#e13242','#ac1759','#6f1f57','#35183d'];  
        elif color == 5:
            colors = 'viridis_r'   
            color_sq = ['#9fd938','#49c16d','#1fa187','#277e8e','#365b8c','#46317e']; 
        elif color == 6:
            colors = 'BuPu'   
            color_sq = ['#dbe8f2','#b5cce2','#96acd1','#8c7db9','#894da2','#811580']; 

            
        new_data, bins = pd.cut(data, 6, retbins=True,labels=list(range(6))) 
        color_ton = []
        for val in new_data:
            color_ton.append(color_sq[val]) 
        colors = sns.color_palette(colors, n_colors=np.size(color_sq))
        sns.palplot(colors, 0.6);
        
        # Print range of variable amount per colour:
        for i in range(6):
            print ("\n"+str(i+1)+': '+str(int(bins[i]))+" => "+str(int(bins[i+1])-1))            
        return color_ton, bins;
           
    
########################################################################

# Plotting function:
    
def plot_cities_data(sf, title, cities, data=None,color=None, 
                     print_id=False):

    color_ton, bins = calc_color(data, color)
    df = read_shapefile(sf)
    
    city_name = []
    city_indices = []
    
    for i in range(len((cities))):
        city_name = int(cities.iloc[i])
        city_index = df[df.CDUID == str(city_name)].index
        city_index2 = int(city_index[0])
        city_indices.append(city_index2)        
        
    plot_map_fill_multiples_ids_tone(sf, title, city_indices, 
                                 print_id, 
                                 color_ton, 
                                 bins, 
                                 x_lim = None, 
                                 y_lim = None, 
                                 figsize = (20,18));
    
########################################################################

# Filling map with data by color:
    
def plot_map_fill_multiples_ids_tone(sf, title, city_indices,  
                                     print_id, color_ton, 
                                     bins, 
                                     x_lim = None, 
                                     y_lim = None, 
                                     figsize = (20,18)):
    
        ax = plt.figure(figsize = figsize)
        fig, ax = plt.subplots(figsize = figsize)
        fig.suptitle(title, fontsize=26)
                        
        for shape in sf.shapeRecords():        
            for i in range(len(shape.shape.parts)):
                i_start = shape.shape.parts[i]
                if i==len(shape.shape.parts)-1:
                    i_end = len(shape.shape.points)
                else:
                    i_end = shape.shape.parts[i+1]
                x = [i[0] for i in shape.shape.points[i_start:i_end]]
                y = [i[1] for i in shape.shape.points[i_start:i_end]]
                ax.plot(x,y,'k')  
                
        for id in city_indices:
            shape_ex = sf.shape(id)
            x_lon = np.zeros((len(shape_ex.points),1))
            y_lat = np.zeros((len(shape_ex.points),1))
        
            for ip in range(len(shape_ex.parts)):                
                i_start = shape_ex.parts[ip]
                if ip==len(shape_ex.parts)-1:
                    i_end = len(shape_ex.points)
                else:
                    i_end = shape_ex.parts[ip+1]
                x_lon = [ip[0] for ip in shape_ex.points[i_start:i_end]]
                y_lat = [ip[1] for ip in shape_ex.points[i_start:i_end]]              
                plt.fill(x_lon,y_lat, color_ton[city_indices.index(id)])
            if print_id != False:
                x0 = np.mean(x_lon)
                y0 = np.mean(y_lat)
                plt.text(x0, y0, data_generic.GEO_NAME.iloc[id], fontsize=30)
            plt.axis('off')
            plt.savefig(title + '.png', dpi=600)
            
            
########################################################################

# Mother tongue across the country, by census division:
                
# Load census data csv file. This includes all provinces, CDs and CSDs, split by sex and age groups:
data_census = pd.read_csv(r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\98-400-X2016060_ENG_CSV\98-400-X2016060_English_CSV_data.csv") # Mother tongue
data_census = data_census.rename(columns={'GEO_CODE (POR)':'GEO_CODE'})

# Collapse across age and sex:
allage = data_census[data_census["DIM: Age (7)"] == 'Total - Age'] # Collapse across age groups
allsex = allage[allage["DIM: Sex (3)"] == 'Total - Sex'] # Collapse across sexes

# Filter for variable needed (Arabic)
arabic = allsex[allsex["DIM: Mother Tongue (263)"] == 'Arabic'] # filter for Mother tongue == Arabic

# Filter by census divisions:
data_cd = arabic[arabic["GEO_LEVEL"] == 2]

# take forward only variables of interest:
data_cd = pd.DataFrame(data_cd, columns= ['GEO_CODE','GEO_NAME','Dim: Single and multiple mother tongue responses (3): Member ID: [1]: Total - Single and multiple mother tongue responses (Note: 3)'])
# change variable name to something shorter:
data_cd = data_cd.rename(columns={'Dim: Single and multiple mother tongue responses (3): Member ID: [1]: Total - Single and multiple mother tongue responses (Note: 3)':'Total'})

########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################

# Plot Arabic across map of Canada:
canada = data_cd
data_generic = canada
# Open vector map for Canada (downloaded from census website)
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\lcd_000b16a_e.shp"
assert os.path.exists(shp_path), "Input file does not exist." # Test that path to shp file exists
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot command:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = False # The shape id will be printed
color_pallete = 1 # colormap
plot_cities_data(sf, 'Arabic in Canada', cd_codes, data, color_pallete, print_id)

########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################

# Plot by province:
########################################################################################
########################################################################################
# NF
nf = data_cd[data_cd.iloc[:, 0].between(1001, 1012, inclusive=True)] # NF
data_generic = nf # temp store

# Load NF specific shp file:
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\NF\NF.shp"
assert os.path.exists(shp_path), "Input file does not exist."
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot cfg:                 
cd_codes = nf.GEO_CODE # grab all area codes
data = nf.Total # variable totals:
print_id = True # The shape id will be printed
color_pallete = 1 # colormap

# Plot:
plot_cities_data(sf, 'Arabic in NF', cd_codes, data, color_pallete, print_id)
########################################################################################
########################################################################################
# NS
ns = data_cd[data_cd.iloc[:, 0].between(1201, 1218, inclusive=True)] 
data_generic = ns

# Load NF specific shp file:
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\NS\NS.shp"
assert os.path.exists(shp_path), "Input file does not exist."
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot cfg:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = False # The shape id will be printed
color_pallete = 1 # colormap

# Plot:
plot_cities_data(sf, 'Arabic in NS', cd_codes, data, color_pallete, print_id)
########################################################################################
########################################################################################
# PEI
pei = data_cd[data_cd.iloc[:, 0].between(1101, 1105, inclusive=True)] 
data_generic = pei

# Load NF specific shp file:
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\PEI\PEI.shp"
assert os.path.exists(shp_path), "Input file does not exist."
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot cfg:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = True # The shape id will be printed
color_pallete = 1 # colormap

# Plot:
plot_cities_data(sf, 'Arabic in PEI', cd_codes, data, color_pallete, print_id)
########################################################################################
########################################################################################
# NB
nb = data_cd[data_cd.iloc[:, 0].between(1301, 1315, inclusive=True)] 
data_generic = nb

# Load NF specific shp file:
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\NB\NB.shp"
assert os.path.exists(shp_path), "Input file does not exist."
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot cfg:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = True # The shape id will be printed
color_pallete = 1 # colormap

# Plot:
plot_cities_data(sf, 'Arabic in NB', cd_codes, data, color_pallete, print_id)
########################################################################################
########################################################################################
# QC
qc = data_cd[data_cd.iloc[:, 0].between(2401, 2499, inclusive=True)] 
data_generic = qc

# Load NF specific shp file:
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\QC\QC.shp"
assert os.path.exists(shp_path), "Input file does not exist."
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot cfg:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = False # The shape id will be printed
color_pallete = 3 # colormap

# Plot:
plot_cities_data(sf, 'Arabic in QC', cd_codes, data, color_pallete, print_id)
########################################################################################
########################################################################################
# ON
on = data_cd[data_cd.iloc[:, 0].between(3501, 3560,  inclusive=True)] 
data_generic = on

# Load NF specific shp file:
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\ON\ON.shp"
assert os.path.exists(shp_path), "Input file does not exist."
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot cfg:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = False # The shape id will be printed
color_pallete = 4 # colormap

# Plot:
plot_cities_data(sf, 'Arabic in ON', cd_codes, data, color_pallete, print_id)
########################################################################################
########################################################################################
# MB
mb = data_cd[data_cd.iloc[:, 0].between(4601, 4623,  inclusive=True)] 
data_generic = mb

# Load NF specific shp file:
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\MB\MB.shp"
assert os.path.exists(shp_path), "Input file does not exist."
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot cfg:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = False # The shape id will be printed
color_pallete = 3 # colormap

# Plot:
plot_cities_data(sf, 'Arabic in MB', cd_codes, data, color_pallete, print_id)
########################################################################################
########################################################################################
# SK
sk = data_cd[data_cd.iloc[:, 0].between(4701, 4718, inclusive=True)] 
data_generic = sk

# Load NF specific shp file:
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\SK\SK.shp"
assert os.path.exists(shp_path), "Input file does not exist."
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot cfg:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = False # The shape id will be printed
color_pallete = 3 # colormap

# Plot:
plot_cities_data(sf, 'Arabic in SK', cd_codes, data, color_pallete, print_id)
########################################################################################
########################################################################################
# AB
ab = data_cd[data_cd.iloc[:, 0].between(4801, 4819, inclusive=True)] 
data_generic = ab

# Load NF specific shp file:
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\AB\AB.shp"
assert os.path.exists(shp_path), "Input file does not exist."
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot cfg:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = False # The shape id will be printed
color_pallete = 3 # colormap

# Plot:
plot_cities_data(sf, 'Arabic in AB', cd_codes, data, color_pallete, print_id)
########################################################################################
########################################################################################
# BC
bc = data_cd[data_cd.iloc[:, 0].between(5901, 5959, inclusive=True)] 
data_generic = bc

# Load NF specific shp file:
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lcd_000b16a_e_og\BC\BC.shp"
assert os.path.exists(shp_path), "Input file does not exist."
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot cfg:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = False # The shape id will be printed
color_pallete = 3 # colormap

# Plot:
plot_cities_data(sf, 'Arabic in BC', cd_codes, data, color_pallete, print_id)
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################


# Load another census table and isolate another interesting variable:

data_census = pd.read_csv(r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\98-400-X2016192_ENG_CSV\98-400-X2016192_English_CSV_data.csv") # Visible minority
# Change name of var for easy identification later:

# Collapse by age
allage = data_census[data_census["DIM: Age (15A)"] == 'Total - Age'] # Collapse across age groups
# Collapse by Arab as ethnic background
arab = allage[allage["DIM: Visible minority (15)"] == 'Arab']
# Change name of var for easy identification later:
arab = arab.rename(columns={'GEO_CODE (POR)':'GEO_CODE'})
arab = arab[arab["GEO_LEVEL"] == 1] # Remove census subdivisions


moved1year = arabs[arabs["DIM: Selected demographic, cultural, labour force, educational and income characteristics (900)"] == 'Total - Mobility status 1 year ago - 25% sample data']


egyptian = arab[arab["Member ID: Selected demographic, cultural, labour force, educational and income characteristics (900)"] == 545]



# take forward only variables of interest:
data_cd = pd.DataFrame(egyptian, columns= ['GEO_CODE','GEO_NAME','Dim: Sex (3): Member ID: [1]: Total - Sex'])
# change variable name to something shorter:
data_cd = data_cd.rename(columns={'Dim: Sex (3): Member ID: [1]: Total - Sex':'Total'})
       

########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################

def plot_cities_data_P(sf, title, cities, data=None,color=None, 
                     print_id=False):

    color_ton, bins = calc_color(data, color)
    df = read_shapefile(sf)
    df['PRUID'] = pd.to_numeric(df['PRUID']).round(0).astype(int)
    
    city_name = []
    city_indices = []
        
    for i in range(len((cities))):
        city_name = int(cities.iloc[i])
        city_index = df[df.PRUID == city_name].index
        city_index2 = int(city_index[0])
        city_indices.append(city_index2)        
        
    plot_map_fill_multiples_ids_tone(sf, title, city_indices, 
                                 print_id, 
                                 color_ton, 
                                 bins, 
                                 x_lim = None, 
                                 y_lim = None, 
                                 figsize = (20,18));
    
# Plot Arabic across map of Canada:
data_cd['Total'] = pd.to_numeric(data_cd['Total']).round(0).astype(int)
canada = data_cd
data_generic = canada
# Open vector map for Canada (downloaded from census website)
shp_path = r"C:\Users\athus\Desktop\Ahmed\DS project\canada census 2016\lpr_000b16a_e\lpr_000b16a_e.shp"
assert os.path.exists(shp_path), "Input file does not exist." # Test that path to shp file exists
sf = shp.Reader(shp_path,encoding='latin-1')

# Plot command:                 
cd_codes = data_generic.GEO_CODE # grab all area codes
data = data_generic.Total # variable totals:
print_id = False # The shape id will be printed
color_pallete = 1 # colormap
plot_cities_data_P(sf, 'Arabic in Canada', cd_codes, data, color_pallete, print_id)





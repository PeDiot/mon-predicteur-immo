
import pandas as pd 
import numpy as np 

path = r'C:\Users\flore\OneDrive\Bureau\2023\Drive\_Projects\Business Data Challenge'
df = pd.read_csv(path + '/espaces_verts.csv', sep =';')
pd.set_option("display.max_columns", None)

VARS = ["Nom de l'espace vert", 
        "Typologie d'espace vert", 
        "Catégorie",
        "Code postal",
        "Geo Shape", 
        "Geo point"
        ]

df2 = df.loc[:, df.columns.isin(VARS)]
df2.columns

keep = ['Parc', 'Square']
df3 = df2[df2["Catégorie"].isin(keep)]

n = df2.shape[0]
m = df3.shape[0]
print(f'La base est passé de la taille {n} à {m}')

df4 = df3.reset_index()

def parse_list_of_lists(s):
    """
    Clean Geo Shape column 

    ex. list_of_lists = parse_list_of_lists(df4['Geo Shape'][0])
    """
    try:
          s = s.strip()
          s = s.strip('[]')  
          s = s.strip(']]')
          s = s.strip('[[')
          s = s.strip('{"coordinates":')
          s = s.strip('], "type": "Polygon"}')
          lists = s.split('], [')  # split into individual lists
          result = []
          for lst in lists:
                lst = lst.strip('[]')
                values = lst.split(', ')
                result.append([float(v) for v in values])
    except:
          'could parse_list_of_lists'

    return result

def Geo_Shape_Mean(df):

        result = []
        temp = []
        c = 0 # of rows computed
        n = 0

        for i in (range(0,len(df))):
                
                try:
                       list_of_lists = parse_list_of_lists(df['Geo Shape'][i])
                       column_average = [sum(sub_list) / len(sub_list) for sub_list in zip(*list_of_lists)]
                       temp = str(column_average[0]) + ',' + str(column_average[1])
                       result.append(temp)
                       c += 1 
                       print(f'{round(c / df4.shape[0], 2) *100}% of rows processed.')
                except: 
                       n += 1
                       o = ''
                       result.append(o)
        list_of_lists.clear()
        
        print(f'Complete & the number of rows that have not been processed is {n}') 
        return result

all_distances = Geo_Shape_Mean(df4)
all_distances = pd.DataFrame(all_distances, columns = ['Location'])

all_distances.to_csv(path + '//all_distances_parcs.csv', index = False)
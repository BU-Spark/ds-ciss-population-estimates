import pandas as pd
import numpy as np

file_path = r"D:\MS\Summer 25\Spark\Population Estimates\usa_00214.csv"
df = pd.read_csv(file_path)


def get_age_mom(row, df):
    if pd.notnull(row['MOMLOC']) and row['MOMLOC'] > 0:
        mom = df[(df['SERIAL'] == row['SERIAL']) & (df['PERNUM'] == row['MOMLOC'])]
        if not mom.empty:
            return mom.iloc[0]['AGE']
    return None


def get_age_pop(row, df):
    if pd.notnull(row['POPLOC']) and row['POPLOC'] > 0:
        pop = df[(df['SERIAL'] == row['SERIAL']) & (df['PERNUM'] == row['POPLOC'])]
        if not pop.empty:
            return pop.iloc[0]['AGE']
    return None

def get_age_head(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    if not head.empty:
        return int(head.iloc[0]['AGE'])
    return None

def get_momloc_head(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    if not head.empty:
        return int(head.iloc[0]['MOMLOC'])
    return None

def get_poploc_head(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    if not head.empty:
        return int(head.iloc[0]['POPLOC'])
    return None

def get_sploc_head(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    if not head.empty:
        return int(head.iloc[0]['SPLOC'])
    return None

def get_poverty_head(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    if not head.empty:
        return int(head.iloc[0]['POVERTY'])
    return None

def get_gcrepon_head(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    if not head.empty:
        if head.iloc[0]['GCRESPON'] == 2:
            return 2
        elif head.iloc[0]['GCRESPON'] == 1:
            return 1
        else:
            return 0
        
def get_nchild_head(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    if not head.empty:
        return int(head.iloc[0]['NCHILD'])
    return None

def get_related_mom(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    mom_for_per = row['MOMLOC']
    if mom_for_per == 0:
        return np.NaN
    mom = df[(df['SERIAL'] == row['SERIAL']) & (df['PERNUM'] == mom_for_per)]
    if not mom.empty:
        return mom.iloc[0]['RELATED']
    return np.NaN

def get_related_pop(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    pop_for_per = row['POPLOC']
    if pop_for_per == 0:
        return np.NaN
    pop = df[(df['SERIAL'] == row['SERIAL']) & (df['PERNUM'] == pop_for_per)]
    if not pop.empty:
        return pop.iloc[0]['RELATED']
    return np.NaN

def get_var(row, df, var_name):
    if var_name == 'AGE_MOM_RECREATED':
        return get_age_mom(row, df)
    elif var_name == 'AGE_POP_RECREATED':
        return get_age_pop(row, df)
    elif var_name == 'AGE_HEAD_RECREATED':
        return get_age_head(row, df)
    elif var_name == 'MOMLOC_HEAD_RECREATED':
        return get_momloc_head(row, df)
    elif var_name == 'POPLOC_HEAD_RECREATED':
        return get_poploc_head(row, df)
    elif var_name == 'SPLOC_HEAD_RECREATED':
        return get_sploc_head(row, df)
    elif var_name == 'POVERTY_HEAD_RECREATED':
        return get_poverty_head(row, df)
    elif var_name == 'GCRESPON_HEAD_RECREATED':
        return get_gcrepon_head(row, df)
    elif var_name == 'NCHILD_HEAD_RECREATED':
        return get_nchild_head(row, df)
    elif var_name == 'RELATED_MOM_RECREATED':
        return get_related_mom(row, df)
    elif var_name == 'RELATED_POP_RECREATED':
        return get_related_pop(row, df)

linked_vars = ['AGE_MOM', 'AGE_POP', 'AGE_HEAD', 'MOMLOC_HEAD', 'POPLOC_HEAD', 'SPLOC_HEAD', 'POVERTY_HEAD', 'GCRESPON_HEAD', 'NCHILD_HEAD', 'RELATED_MOM', 'RELATED_POP']
for var in linked_vars:
    df[f'{var}_RECREATED'] = df.apply(lambda row: get_var(row, df, f'{var}_RECREATED'), axis=1)
    print(f'Do values for {var} and {var}_RECREATED match?: {df[f"{var}_RECREATED"].equals(df[var])}') 
# df['AGE_MOM_RECREATED'] = df.apply(lambda row: get_age_mom(row, df), axis=1)
# df['AGE_POP_RECREATED'] = df.apply(lambda row: get_age_pop(row, df), axis=1)
# df['AGE_HEAD_RECREATED'] = df.apply(lambda row: get_age_head(row, df), axis=1)
# df['MOMLOC_HEAD_RECREATED'] = df.apply(lambda row: get_momloc_head(row, df), axis=1)
# df['POPLOC_HEAD_RECREATED'] = df.apply(lambda row: get_poploc_head(row, df), axis=1)
# df['SPLOC_HEAD_RECREATED'] = df.apply(lambda row: get_sploc_head(row, df), axis=1) 


# print(df[[
#     'SERIAL', 'PERNUM', 'AGE',
#     'MOMLOC', 'AGE_MOM', 'AGE_MOM_RECREATED',
#     'POPLOC', 'AGE_POP', 'AGE_POP_RECREATED',
#     'RELATE', 'AGE_HEAD', 'AGE_HEAD_RECREATED',
#     'MOMLOC_HEAD_RECREATED', 'POPLOC_HEAD_RECREATED', 'SPLOC_HEAD_RECREATED'
# ]].head(20))

# print(df[['SERIAL', 'PERNUM', 'AGE', 'MOMLOC', 'AGE_MOM', 'AGE_MOM_RECREATED', 'AGE_POP', 'AGE_POP_RECREATED']].head(20)) 

print(df[['SERIAL', 'PERNUM', 'AGE_HEAD', 'AGE_HEAD_RECREATED']].head(20)) 
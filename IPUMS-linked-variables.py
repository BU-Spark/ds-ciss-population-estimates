import pandas as pd

file_path = "/Users/aparnakalla/Downloads/usa_00214.csv"
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
        return head.iloc[0]['AGE']
    return None

def get_momloc_head(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    if not head.empty:
        return head.iloc[0]['MOMLOC']
    return None

def get_poploc_head(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    if not head.empty:
        return head.iloc[0]['POPLOC']
    return None

def get_sploc_head(row, df):
    head = df[(df['SERIAL'] == row['SERIAL']) & (df['RELATE'] == 1)]
    if not head.empty:
        return head.iloc[0]['SPLOC']
    return None


df['AGE_MOM_RECREATED'] = df.apply(lambda row: get_age_mom(row, df), axis=1)
df['AGE_POP_RECREATED'] = df.apply(lambda row: get_age_pop(row, df), axis=1)
df['AGE_HEAD_RECREATED'] = df.apply(lambda row: get_age_head(row, df), axis=1)
df['MOMLOC_HEAD_RECREATED'] = df.apply(lambda row: get_momloc_head(row, df), axis=1)
df['POPLOC_HEAD_RECREATED'] = df.apply(lambda row: get_poploc_head(row, df), axis=1)
df['SPLOC_HEAD_RECREATED'] = df.apply(lambda row: get_sploc_head(row, df), axis=1)



print(df[[
    'SERIAL', 'PERNUM', 'AGE',
    'MOMLOC', 'AGE_MOM', 'AGE_MOM_RECREATED',
    'POPLOC', 'AGE_POP', 'AGE_POP_RECREATED',
    'RELATE', 'AGE_HEAD_RECREATED',
    'MOMLOC_HEAD_RECREATED', 'POPLOC_HEAD_RECREATED', 'SPLOC_HEAD_RECREATED'
]].head(20))

# print(df[['SERIAL', 'PERNUM', 'AGE', 'MOMLOC', 'AGE_MOM', 'AGE_MOM_RECREATED', 'AGE_POP', 'AGE_POP_RECREATED']].head(20))
import pandas as pd
import numpy as np


def derive_pop_loc_head(df):
    result_df = df.copy()
    result_df['POPLOC_HEAD_acs'] = None

    for serialno, household in df.groupby('SERIALNO'):

        head_records = household[household['RELSHIPP'] == 20]
        
        if len(head_records) == 0:
            continue

        head = head_records.iloc[0]
        head_age = head['AGEP']
        head_sporder = head['SPORDER']
        candidates = household[
            (household['SEX'] == 1)
        ]
        
        if len(candidates) == 0:
            mom_sporder = 0
        else:
            mother_candidates = candidates[candidates['RELSHIPP'] == 29]
            
            if len(mother_candidates) > 0:
                mom_sporder = mother_candidates.iloc[0]['SPORDER']
            else:
                mom_sporder = 0

        household_mask = (result_df['SERIALNO'] == serialno) 
        result_df.loc[household_mask, 'POPLOC_HEAD_acs'] = mom_sporder
    
    return result_df

def derive_mom_loc_head(df):
    result_df = df.copy() 
    result_df['MOM_LOC_HEAD'] = None
    
    for serialno, household in df.groupby('SERIALNO'):
        
        head_records = household[household['RELSHIPP'] == 20]
        if len(head_records) == 0:
            continue

        head = head_records.iloc[0]
        head_age = head['AGEP']
        head_sporder = head['SPORDER']
        candidates = household[
            (household['SEX'] == 2)
        ]
        
        if len(candidates) == 0:
            mom_sporder = 0
        else:
            mother_candidates = candidates[candidates['RELSHIPP'] == 29]
            if len(mother_candidates) > 0:
                mom_sporder = mother_candidates.iloc[0]['SPORDER']
            else:
                mom_sporder = 0
        household_mask = (result_df['SERIALNO'] == serialno) 
        result_df.loc[household_mask, 'MOM_LOC_HEAD'] = mom_sporder
    
    return result_df


def get_gcrespon_head_acs(df):
    result_df = df.copy()
    result_df['GCRESPON_HEAD_acs'] = 0
    for serialno, household in df.groupby('SERIALNO'):
        household_mask = (result_df['SERIALNO'] == serialno)
        head_records = household[household['RELSHIPP'] == 20]
        if head_records.empty:
            continue
        gcr_head = head_records['GCR'].values[0]
        # 1: Yes, 2: No for acs
        # 1: No, 2: Yes for ipums
        flipped_gcr_head = 3 - gcr_head
        # print(type(gcr_head))
        if np.isnan(gcr_head):
            # print(gcr_head)
            flipped_gcr_head = 0
        result_df.loc[household_mask, 'GCRESPON_HEAD_acs'] = flipped_gcr_head
    return result_df

def get_new_serialno(df):
    # result_df = df.copy()
    FLAG_TO_DIGITS = {'HU': '00',
                  'GQ': '01'}          

    hu_mask = df['SERIALNO'].astype(str).str.contains('HU', na=False)
    result_df = df[hu_mask].copy()
    # Apply the conversion only to HU records
    ser = result_df['SERIALNO'].astype(str)            
    result_df['SERIALNO_NEW'] = (
        ser.str[:4]                                   
        + ser.str[4:6].map(FLAG_TO_DIGITS).fillna('99')   
        + ser.str[6:]                                 
    ).astype(np.int64) 
    return result_df

def get_age_head_acs(df):
    result_df = df.copy()
    result_df['AGE_HEAD_acs'] = df['HHLDRAGEP']
    return result_df

def compute_nchild_head(df):
    result_df = df.copy()
    result_df['NCHILD_HEAD_acs'] = 0

    for serialno, household in df.groupby('SERIALNO'):
        head_records = household[household['RELSHIPP'] == 20]
        
        if len(head_records) == 0:
            continue

        head = head_records.iloc[0]
        head_age = head['AGEP']
        head_sporder = head['SPORDER']
        
        children = household[
            # (household['AGEP'] <= head_age - 12)
            (household['RELSHIPP'].isin([25, 26, 27])) 
        ]
        
        nchild_head = len(children)
        
        household_mask = (result_df['SERIALNO'] == serialno)
        result_df.loc[household_mask, 'NCHILD_HEAD_acs'] = nchild_head
    
    return result_df 

def get_poverty_head_acs(df):
    income_factor = 0.407
    result_df = df.copy()
    result_df['POVERTY_HEAD_acs'] = 0
    for serialno, household in df.groupby('SERIALNO'):
        household_mask = (result_df['SERIALNO'] == serialno)
        head_records = household[household['RELSHIPP'] == 20]
        if head_records.empty:
            poverty_head = None
            continue
        poverty_head = head_records['POVPIP'].values[0]
        result_df.loc[household_mask, 'POVERTY_HEAD_acs'] = poverty_head
    return result_df

def derive_sp_loc_head(df):
    result_df = df.copy()
    result_df['SPLOC_HEAD_acs'] = 0  # Default to 0 if no spouse found (to match IPUMS style)

    for serialno, household in df.groupby('SERIALNO'):
        # Step 1: Find the head of household
        head_records = household[household['RELSHIPP'] == 20]
        if len(head_records) == 0:
            continue

        head = head_records.iloc[0]
        head_sporder = head['SPORDER']

        # Step 2: Look for spouse or unmarried partner
        partner_candidates = household[household['RELSHIPP'].isin([21, 22])]
        if len(partner_candidates) > 0:
            sp_sporder = partner_candidates.iloc[0]['SPORDER']
        else:
            sp_sporder = 0  # No partner found

        # Step 3: Assign to all household rows for convenience
        household_mask = (result_df['SERIALNO'] == serialno)
        result_df.loc[household_mask, 'SPLOC_HEAD_acs'] = sp_sporder

    return result_df

def main():
    # Load your data
    pma = pd.read_csv('D:\MS\Summer-25\Spark\Population Estimates\csv_pma\psam_p25.csv')
    hma = pd.read_csv('D:\MS\Summer-25\Spark\Population Estimates\csv_hma\psam_h25.csv')

    merged_ma = pd.merge(pma, hma, on="SERIALNO")
    merged_ma_hu = get_new_serialno(merged_ma)
    file_path = r"D:\MS\Summer-25\Spark\Population Estimates\usa_00214.csv"
    df_mass = pd.read_csv(file_path)
    # df_mass = df[df['STATEICP'] == 3]
    result_merged_ma_hu = merged_ma_hu.copy()
    result_merged_ma_hu = derive_pop_loc_head(result_merged_ma_hu)
    result_merged_ma_hu = derive_mom_loc_head(result_merged_ma_hu)
    result_merged_ma_hu = get_gcrespon_head_acs(result_merged_ma_hu)
    result_merged_ma_hu = get_age_head_acs(result_merged_ma_hu)
    result_merged_ma_hu = compute_nchild_head(result_merged_ma_hu)
    result_merged_ma_hu = get_poverty_head_acs(result_merged_ma_hu)
    result_merged_ma_hu = derive_sp_loc_head(result_merged_ma_hu)
    
    df_mass_res_merged = pd.merge(df_mass,
                        result_merged_ma_hu,
                        left_on=['CBSERIAL', 'PERNUM', 'SEX'],
                        right_on=['SERIALNO_NEW', 'SPORDER', 'SEX'],
                        how='inner')
    
    print(f'Match rate for POVERTY_HEAD: {len(df_mass_res_merged.loc[df_mass_res_merged["POVERTY_HEAD_acs"] == df_mass_res_merged["POVERTY_HEAD"]])/len(df_mass_res_merged)}')
    print(f'Match rate for AGE_HEAD: {len(df_mass_res_merged.loc[df_mass_res_merged["AGE_HEAD_acs"] == df_mass_res_merged["AGE_HEAD"]])/len(df_mass_res_merged)}')
    print(f'Match rate for NCHILD_HEAD: {len(df_mass_res_merged.loc[df_mass_res_merged["NCHILD_HEAD_acs"] == df_mass_res_merged["NCHILD_HEAD"]])/len(df_mass_res_merged)}')
    print(f'Match rate for GCRESPON_HEAD: {len(df_mass_res_merged.loc[df_mass_res_merged["GCRESPON_HEAD_acs"] == df_mass_res_merged["GCRESPON_HEAD"]])/len(df_mass_res_merged)}')
    print(f'Match rate for POPLOC_HEAD: {len(df_mass_res_merged.loc[df_mass_res_merged["POPLOC_HEAD_acs"] == df_mass_res_merged["POPLOC_HEAD"]])/len(df_mass_res_merged)}')
    print(f'Match rate for MOM_LOC_HEAD: {len(df_mass_res_merged.loc[df_mass_res_merged["MOM_LOC_HEAD"] == df_mass_res_merged["MOMLOC_HEAD"]])/len(df_mass_res_merged)}')
    print(f'Match rate for SPLOC_HEAD: {len(df_mass_res_merged.loc[df_mass_res_merged["SPLOC_HEAD_acs"] == df_mass_res_merged["SPLOC_HEAD"]])/len(df_mass_res_merged)}')
    
if __name__ == "__main__":
    main()





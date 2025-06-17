
import pandas as pd
import numpy as np

# Load your data
pma = pd.read_csv('D:\MS\Summer 25\Spark\Population Estimates\csv_pma\psam_p25.csv')
hma = pd.read_csv('D:\MS\Summer 25\Spark\Population Estimates\csv_hma\psam_h25.csv')

merged_ma = pd.merge(pma, hma, on="SERIALNO")
print(f"Merged dataset shape: {merged_ma.shape}")

def derive_mom_loc_head(df):
    """
    Fixed version that uses the input dataframe parameter correctly
    """
    # Create a copy to avoid modifying original data
    result_df = df.copy()  # Use df parameter, not hardcoded merged_ma
    
    # Initialize MOM_LOC_HEAD column
    result_df['MOM_LOC_HEAD'] = None
    
    # Group by household (SERIALNO)
    for serialno, household in df.groupby('SERIALNO'):
        
        # Step 1: Find head of household (RELSHIPP == 20)
        head_records = household[household['RELSHIPP'] == 20]
        
        if len(head_records) == 0:
            # No head of household found, skip this household
            continue
        
        # Take first head if multiple (shouldn't happen in clean data)
        head = head_records.iloc[0]
        head_age = head['AGEP']
        head_sporder = head['SPORDER']
        
        # Step 3: Find mother candidates in same household
        candidates = household[
            (household['SEX'] == 2) # &  # Female
            # (household['AGEP'] <= head_age - 12)  # At least 12 years older than head
        ]
        
        if len(candidates) == 0:
            # No candidates found
            mom_sporder = 0
        else:
            # Step 4: Prioritize RELSHIPP == 29 (mother)
            mother_candidates = candidates[candidates['RELSHIPP'] == 29]
            
            if len(mother_candidates) > 0:
                # Found mother relationship, take first one
                mom_sporder = mother_candidates.iloc[0]['SPORDER']
            else:
                # No mother relationship found, take first candidate that fits age/sex criteria
                mom_sporder = 0
        
        # Assign MOM_LOC_HEAD to the head of household record
        household_mask = (result_df['SERIALNO'] == serialno) 
        result_df.loc[household_mask, 'MOM_LOC_HEAD'] = mom_sporder
    
    return result_df

# Run the function on your merged dataset
# print("Processing MOM_LOC_HEAD...")
# result_data = derive_mom_loc_head(merged_ma)

# # Check the results
# print(f"Final dataset shape: {result_data.shape}")
# print("\nSample of results (heads of household only):")
# heads_sample = result_data[result_data['RELSHIPP'] == 20][['SERIALNO', 'SPORDER', 'AGEP', 'SEX', 'RELSHIPP', 'MOM_LOC_HEAD']].head(10)
# print(heads_sample)

# # Summary statistics
# print(f"\nSummary:")
# total_heads = len(result_data[result_data['RELSHIPP'] == 20])
# heads_with_mom = len(result_data[(result_data['RELSHIPP'] == 20) & (result_data['MOM_LOC_HEAD'].notna())])
# print(f"Total heads of household: {total_heads}")
# print(f"Heads with identified mothers: {heads_with_mom}")
# print(f"Percentage with mothers identified: {heads_with_mom/total_heads*100:.1f}%")



# heads_with_mothers = result_data[
#     (result_data['RELSHIPP'] == 20) & 
#     (result_data['MOM_LOC_HEAD'].notna())
# ]

# print(f"\nFound {len(heads_with_mothers)} heads of household with identified mothers")
# print(heads_with_mothers)

# # verification with IPUMS
# ipums_df = pd.read_csv(r'D:\MS\Summer 25\Spark\Population Estimates\usa_00214.csv')
# ipums_res_merge = pd.concat(ipums_df, result_data, left_on='CBSERIAL', right_on='SERIALNO')
# ipums_res_merge['MOM_LOC_HEAD'].equals(ipums_res_merge['MOMLOC_HEAD'])
# print(ipums_res_merge[['CBSERIAL', 'MOMLOC_HEAD', 'MOM_LOC_HEAD']].head(15))

def get_gcrespon_head_acs(df):
    result_df = df.copy()
    result_df['RESPON_HEAD_acs'] = 0
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
        result_df.loc[household_mask, 'RESPON_HEAD_acs'] = flipped_gcr_head
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
    # for serialno, household in df.groupby('SERIALNO'):
    #     head_records = household[household['RELSHIPP'] == 20]
    #     if head_records.empty:
    #         head_records = None
    #         continue
    #     head_age = head_records['AGEP'].values[0]
    #     # print(head_age)
    #     household_mask = (result_df['SERIALNO'] == serialno)
    #     # print(household_mask)
    #     result_df.loc[household_mask, 'AGE_HEAD_acs'] = head_age
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








# %%
import pandas as pd 
pma = pd.read_csv('/Users/aparnakalla/Downloads/csv_pma/psam_p25.csv')
hma = pd.read_csv('/Users/aparnakalla/Downloads/csv_hma/psam_h25.csv')

merged_ma = pd.merge(pma, hma, on="SERIALNO")

def derive_sp_loc_head(df):
    result_df = df.copy()
    result_df['SP_LOC_HEAD'] = 0  # Default to 0 if no spouse found (to match IPUMS style)

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
        result_df.loc[household_mask, 'SP_LOC_HEAD'] = sp_sporder

    return result_df


result_data = derive_sp_loc_head(merged_ma)

# %%
result_data['SP_LOC_HEAD'].value_counts()

# %%
result_data[result_data['SP_LOC_HEAD'] == 2][['SERIALNO', 'SPORDER', 'RELSHIPP']].head(10)


# %%
file =pd.read_csv('/Users/aparnakalla/Downloads/usa_00003.csv')

file.head(10) 

# %%
df_mass = file[file['STATEICP'] == 3]

# %%
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

# %%
result_data = get_new_serialno(result_data)

# %%
result_data

# %%
result_data[['SERIALNO_NEW','SPORDER']]

# %%
df_mass_pov_head_merged = pd.merge(df_mass,
                        result_data,
                        left_on=['CBSERIAL', 'PERNUM'],
                        right_on=['SERIALNO_NEW', 'SPORDER'],
                        how='inner')
df_mass_pov_head_merged

# %%
df_mass_pov_head_merged['SPLOC_MATCH'] = df_mass_pov_head_merged['SP_LOC_HEAD'] == df_mass_pov_head_merged['SPLOC']


# %%
total = len(df_mass_pov_head_merged)
matches = df_mass_pov_head_merged['SPLOC_MATCH'].sum()
mismatches = total - matches
accuracy = matches / total * 100

print(f"Total records: {total}")
print(f"Matches: {matches}")
print(f"Mismatches: {mismatches}")
print(f"Match rate: {accuracy:.2f}%")


# %%
df_mass_pov_head_merged[df_mass_pov_head_merged['SPLOC_MATCH'] == False][['CBSERIAL', 'PERNUM', 'SP_LOC_HEAD', 'SPLOC']].head(10)


# %%
# Filter only to heads of household
heads_only = df_mass_pov_head_merged[df_mass_pov_head_merged['RELATE'] == 1]

# Now compare SP_LOC_HEAD vs SPLOC for heads only
heads_only['SPLOC_MATCH'] = heads_only['SP_LOC_HEAD'] == heads_only['SPLOC']

# Check match rate
match_rate = heads_only['SPLOC_MATCH'].mean() * 100
print(f"Match rate for heads of household: {match_rate:.2f}%")


# %%




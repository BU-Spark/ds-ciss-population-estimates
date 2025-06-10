
import pandas as pd

# Load your data
pma = pd.read_csv('/Users/aparnakalla/Downloads/csv_pma/psam_p25.csv')
hma = pd.read_csv('/Users/aparnakalla/Downloads/csv_hma/psam_h25.csv')

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
            (household['SEX'] == 2) &  # Female
            (household['AGEP'] <= head_age - 12)  # At least 12 years older than head
        ]
        
        if len(candidates) == 0:
            # No candidates found
            mom_sporder = None
        else:
            # Step 4: Prioritize RELSHIPP == 29 (mother)
            mother_candidates = candidates[candidates['RELSHIPP'] == 29]
            
            if len(mother_candidates) > 0:
                # Found mother relationship, take first one
                mom_sporder = mother_candidates.iloc[0]['SPORDER']
            else:
                # No mother relationship found, take first candidate that fits age/sex criteria
                mom_sporder = candidates.iloc[0]['SPORDER']
        
        # Assign MOM_LOC_HEAD to the head of household record
        head_mask = (result_df['SERIALNO'] == serialno) & (result_df['SPORDER'] == head_sporder)
        result_df.loc[head_mask, 'MOM_LOC_HEAD'] = mom_sporder
    
    return result_df

# Run the function on your merged dataset
print("Processing MOM_LOC_HEAD...")
result_data = derive_mom_loc_head(merged_ma)

# Check the results
print(f"Final dataset shape: {result_data.shape}")
print("\nSample of results (heads of household only):")
heads_sample = result_data[result_data['RELSHIPP'] == 20][['SERIALNO', 'SPORDER', 'AGEP', 'SEX', 'RELSHIPP', 'MOM_LOC_HEAD']].head(10)
print(heads_sample)

# Summary statistics
print(f"\nSummary:")
total_heads = len(result_data[result_data['RELSHIPP'] == 20])
heads_with_mom = len(result_data[(result_data['RELSHIPP'] == 20) & (result_data['MOM_LOC_HEAD'].notna())])
print(f"Total heads of household: {total_heads}")
print(f"Heads with identified mothers: {heads_with_mom}")
print(f"Percentage with mothers identified: {heads_with_mom/total_heads*100:.1f}%")



heads_with_mothers = result_data[
    (result_data['RELSHIPP'] == 20) & 
    (result_data['MOM_LOC_HEAD'].notna())
]

print(f"\nFound {len(heads_with_mothers)} heads of household with identified mothers")
print(heads_with_mothers)



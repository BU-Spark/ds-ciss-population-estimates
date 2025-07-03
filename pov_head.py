"""
Code to calculate poverty head based from ACS data using the logic mentioned in IPUMS' documentation
"""

def get_poverty_threshold(num_people, num_related_children, rp_age):
    """
    Get poverty threshold based on household composition.
    """
    
    # Determine if RP is 65 or older
    rp_elderly = rp_age >= 65
    
    # Poverty threshold lookup table based on the image
    poverty_thresholds = {
        # One person households
        (1, 0, False): 6451,   # One person under 65 years
        (1, 0, True): 5947,    # One person, 65 years or older
        
        # Two people households - RP age matters
        (2, 0, False): 8303,   # Two people, RP under 65 years, no children
        (2, 1, False): 8547,   # Two people, RP under 65 years, one child
        (2, 0, True): 7495,    # Two people, RP 65 years or older, no children
        (2, 1, True): 8515,    # Two people, RP 65 years or older, one child
        
        # Three people households (no age distinction shown in table)
        (3, 0): 9699,   # Three people, no children
        (3, 1): 9981,   # Three people, one child
        (3, 2): 9990,   # Three people, two children
        
        # Four people households
        (4, 0): 12790,  # Four people, no children
        (4, 1): 12999,  # Four people, one child
        (4, 2): 12575,  # Four people, two children
        (4, 3): 12619,  # Four people, three children
        
        # Five people households
        (5, 0): 15424,  # Five people, no children
        (5, 1): 15648,  # Five people, one child
        (5, 2): 15169,  # Five people, two children
        (5, 3): 14798,  # Five people, three children
        (5, 4): 14572,  # Five people, four children
        
        # Six people households
        (6, 0): 17740,  # Six people, no children
        (6, 1): 17811,  # Six people, one child
        (6, 2): 17444,  # Six people, two children
        (6, 3): 17092,  # Six people, three children
        (6, 4): 16569,  # Six people, four children
        (6, 5): 16259,  # Six people, five children
        
        # Seven people households
        (7, 0): 20412,  # Seven people, no children
        (7, 1): 20540,  # Seven people, one child
        (7, 2): 20101,  # Seven people, two children
        (7, 3): 19794,  # Seven people, three children
        (7, 4): 19224,  # Seven people, four children
        (7, 5): 18558,  # Seven people, five children
        (7, 6): 17828,  # Seven people, six children
        
        # Eight people households
        (8, 0): 22830,  # Eight people, no children
        (8, 1): 23031,  # Eight people, one child
        (8, 2): 22617,  # Eight people, two children
        (8, 3): 22253,  # Eight people, three children
        (8, 4): 21738,  # Eight people, four children
        (8, 5): 21084,  # Eight people, five children
        (8, 6): 20403,  # Eight people, six children
        (8, 7): 20230,  # Eight people, seven children
        
        # Nine or more people households
        (9, 0): 27463,  # Nine+ people, no children
        (9, 1): 27596,  # Nine+ people, one child
        (9, 2): 27229,  # Nine+ people, two children
        (9, 3): 26921,  # Nine+ people, three children
        (9, 4): 26415,  # Nine+ people, four children
        (9, 5): 25719,  # Nine+ people, five children
        (9, 6): 25089,  # Nine+ people, six children
        (9, 7): 24933,  # Nine+ people, seven children
        (9, 8): 23973,  # Nine+ people, eight+ children
    }
    
    # Handle 9+ people by mapping to 9
    lookup_people = min(num_people, 9)
    
    # Handle 8+ children by mapping to 8 for households with 9+ people
    if lookup_people >= 9:
        lookup_children = min(num_related_children, 8)
    else:
        lookup_children = num_related_children
    
    # Build lookup key based on household size
    if num_people <= 2:
        # For 1-2 person households, RP age matters
        key = (lookup_people, lookup_children, rp_elderly)
    else:
        # For 3+ person households, RP age doesn't matter (based on table)
        key = (lookup_people, lookup_children)
    
    return poverty_thresholds.get(key, None)


def apply_poverty_threshold_to_dataset(df):
    """
    Apply poverty threshold to your ACS dataset.
    - NP: Number of people in household
    - NRC: Number of related children
    - HHLDRAGEP: Age of household head/responsible person
    """
    result_df = df.copy()
    # result_df['adj_inc'] = result_df['FINCP'] * income_factor
    
    result_df['poverty_threshold'] = result_df.apply(
        lambda row: get_poverty_threshold(
            row['NP'], 
            row['NRC'], 
            row['HHLDRAGEP']
        ), 
        axis=1
    )
    
    adjinc_factor = 1.042311
    income_factor = 0.424
    result_df['adj_inc'] = result_df['FINCP'] * income_factor
    result_df['POVERTY_HEAD_acs'] = (result_df['adj_inc'] / result_df['poverty_threshold']) * 100
    return result_df
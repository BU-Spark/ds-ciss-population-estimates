import pandas as pd
import numpy as np

file_path = r"D:\MS\Summer-25\Spark\Population Estimates\usa_00214.csv"
df = pd.read_csv(file_path)
df_mass = df[df['STATEICP'] == 3]

def construct_sprule(df):
    result_df = df.copy()
    result_df['SPLOC_const'] = 0  
    result_df['SPRULE_const'] = 0  
    
    for serial, household in df.groupby('SERIAL'):
        household = household.copy()
        
        has_householder_partner = (
            household['RELATED'].eq(101).any() and 
            household['RELATED'].eq(1114).any()
        )
        
        if has_householder_partner:
            married_persons = household[
                (household['MARST'].isin([1, 2])) | 
                (household['RELATED'].isin([101, 1114]))
            ].copy()
        else:
            married_persons = household[
                (household['MARST'].isin([1, 2]))
            ].copy()
        
        if len(married_persons) < 2:
            continue 

        spouse_links = []
        
        for idx, person in married_persons.iterrows():
            person_relate = person['RELATED']
            person_sex = person['SEX']
            person_age = person['AGE']
            person_pernum = person['PERNUM']
            person_marst = person['MARST']  # Add MARST info

            potential_spouses = married_persons[
                (married_persons['PERNUM'] != person_pernum)
            ].copy()
            
            if len(potential_spouses) == 0:
                continue

            for sp_idx, spouse in potential_spouses.iterrows():
                spouse_relate = spouse['RELATED']
                spouse_sex = spouse['SEX']
                spouse_age = spouse['AGE']
                spouse_pernum = spouse['PERNUM']
                spouse_marst = spouse['MARST']  # Add MARST info
                
                priority = get_relationship_priority(person_relate, spouse_relate)
                
                if priority > 0:
                    # Calculate MARST priority (lower is better)
                    if person_marst == 1 and spouse_marst == 1:
                        marst_priority = 1  # Both have "married, spouse present"
                    elif (person_marst == 1 and spouse_marst == 2) or (person_marst == 2 and spouse_marst == 1):
                        marst_priority = 2  # One has "married, spouse present", one has "married, spouse absent"
                    else:
                        marst_priority = 3  # Both have "married, spouse absent" or other combinations
                    
                    spouse_links.append({
                        'person_pernum': person_pernum,
                        'spouse_pernum': spouse_pernum,
                        'person_sex': person_sex,
                        'spouse_sex': spouse_sex,
                        'person_age': person_age,
                        'spouse_age': spouse_age,
                        'priority': priority,
                        'marst_priority': marst_priority  # Add MARST priority
                    })
        
        if spouse_links:
            spouse_links_df = pd.DataFrame(spouse_links)
            
            # Sort by relationship priority first, then by MARST priority
            spouse_links_df = spouse_links_df.sort_values(['priority', 'marst_priority'])

            paired_persons = set()

            for priority in sorted(spouse_links_df['priority'].unique()):
                priority_links = spouse_links_df[spouse_links_df['priority'] == priority]
                
                # Within each priority level, process by MARST priority
                for marst_priority in sorted(priority_links['marst_priority'].unique()):
                    marst_priority_links = priority_links[priority_links['marst_priority'] == marst_priority]

                    for _, link in marst_priority_links.iterrows():
                        person_pernum = link['person_pernum']
                        spouse_pernum = link['spouse_pernum']
                        
                        if person_pernum in paired_persons or spouse_pernum in paired_persons:
                            continue
                        
                        person_candidates = marst_priority_links[
                            (marst_priority_links['person_pernum'] == person_pernum) &
                            (~marst_priority_links['spouse_pernum'].isin(paired_persons))
                        ]
                        
                        if len(person_candidates) == 0:
                            continue

                        clarity = get_clarity_level(person_candidates, person_pernum)
                        sprule = int(f"{priority}{clarity}")
                        selected_spouse = person_candidates.iloc[0]['spouse_pernum']
            
                        if person_pernum not in paired_persons and selected_spouse not in paired_persons:
                            # Assign the spouse link (same as before)
                            result_df.loc[result_df['SERIAL'] == serial, 'SPLOC_const'] = result_df.loc[
                                result_df['SERIAL'] == serial, 'SPLOC_const'
                            ].where(
                                result_df.loc[result_df['SERIAL'] == serial, 'PERNUM'] != person_pernum,
                                spouse_pernum
                            )
                            
                            result_df.loc[result_df['SERIAL'] == serial, 'SPRULE_const'] = result_df.loc[
                                result_df['SERIAL'] == serial, 'SPRULE_const'
                            ].where(
                                result_df.loc[result_df['SERIAL'] == serial, 'PERNUM'] != person_pernum,
                                sprule
                            )
                            
                            # Also assign reciprocal link
                            result_df.loc[result_df['SERIAL'] == serial, 'SPLOC_const'] = result_df.loc[
                                result_df['SERIAL'] == serial, 'SPLOC_const'
                            ].where(
                                result_df.loc[result_df['SERIAL'] == serial, 'PERNUM'] != spouse_pernum,
                                person_pernum
                            )
                            
                            result_df.loc[result_df['SERIAL'] == serial, 'SPRULE_const'] = result_df.loc[
                                result_df['SERIAL'] == serial, 'SPRULE_const'
                            ].where(
                                result_df.loc[result_df['SERIAL'] == serial, 'PERNUM'] != spouse_pernum,
                                sprule
                            )
                            
                            paired_persons.add(person_pernum)
                            paired_persons.add(spouse_pernum)
    
    return result_df

def get_relationship_priority(relate1, relate2):

    direct_pairs = [
        (101, 201),   # Householder to Spouse
        (201, 101),   # Spouse to Householder
        (501, 501),   # Parent to Parent
        (301, 401),   # Child to Child-in-law
        (401, 301),   # Child-in-law to Child
        (303, 401),   # Step-child to child-in-law
        (401, 303),   # Child-in-law to Step-child
        (302, 401),   # adopted child to child-in-law
        (401, 302),   # child-in-law to adopted child
        (701, 801),   # Sibling to Sibling-in-law
        (801, 701),   # Sibling-in-law to Sibling
        # (11, 11), # Aunt/Uncle to Aunt/Uncle
        (601, 601),   # Parent-in-law to Parent-in-law
        (1114, 1114), # Partner to Partner
        (1115, 1115), # Housemate to Housemate
        (1114, 1115), # Partner to Housemate
        (1115, 1114), # Housemate to Partner
        (1260, 1260), # other non-relative to other non-relative
    ]
    
    if (relate1, relate2) in direct_pairs:
        return 1

    second_level_pairs = [
        (101, 1114),  # Householder to Partner
        (1114, 101),  # Partner to Householder
    ]
    
    if (relate1, relate2) in second_level_pairs:
        return 2

    third_level_pairs = [
        (1001, 901),  # Other relative to Grandchild
        (901, 1001),  # Grandchild to Other relative
        (1001, 301),  # Other relative to Child
        (301, 1001),  # Child to Other relative
        (1001, 701),  # Other relative to Sibling
        (701, 1001),  # Sibling to Other relative
        (801, 1001),  # Sibling-in-law to Other relative
        (1001, 801),  # Other relative to Sibling-in-law
        # (14, 14), # Non-relative to Non-relative (roomer, housemate)
        (1001, 1001), # other relative to other relative
        (1260, 1115), # other non-relative to housemate
        (1115, 1260), # housemate to other non-relative
        (1260, 1114), # other non-relative to partner
        (1114, 1260), # partner to other non-relative
    ]
    
    if (relate1, relate2) in third_level_pairs:
        return 3

    fourth_level_pairs = [
        (301, 301),   # Child to Child
        (901, 901),   # Grandchild to Grandchild
        (701, 701),   # Sibling to Sibling
        (801, 801),   # Sibling-in-law to Sibling-in-law
        # (12, 10), # Other relative to Grandparent
        # (10, 12), # Grandparent to Other relative
        # (12, 11), # Other relative to Aunt/Uncle
        # (11, 12), # Aunt/Uncle to Other relative
        (1001, 501),  # Other relative to Parent
        (501, 1001),  # Parent to Other relative
        (1001, 101),  # Other relative to Householder
        # (101, 1001),  # Householder to Other relative
    ] 
    
    if (relate1, relate2) in fourth_level_pairs:
        return 4
    
    fifth_level_pairs = [
        (101, 1001),  # Householder to Other relative
        (1001, 101),  # Other relative to Householder
        (101, 1260),  # Householder to other non-relative
        (1260, 101),  # other non-relative to Householder
        #(12, 1),  # Other relative to Householder
        # (1, 14),  # Householder to Non-relative
        # (14, 1),  # Non-relative to Householder
    ]
    
    if (relate1, relate2) in fifth_level_pairs:
        return 5
    
    return 0 

def get_clarity_level(candidates_df, person_pernum):
    person_candidates = candidates_df[candidates_df['person_pernum'] == person_pernum]
    
    if len(person_candidates) == 0:
        return 1

    total_candidates = len(person_candidates)

    person_sex = person_candidates.iloc[0]['person_sex']
    opposite_sex_candidates = person_candidates[
        person_candidates['spouse_sex'] != person_sex
    ] 

    if total_candidates == 1:
        return 1

    if len(opposite_sex_candidates) == 1:
        return 2

    if len(opposite_sex_candidates) > 1:
        unique_ages = len(opposite_sex_candidates['spouse_age'].unique())
        if unique_ages == len(opposite_sex_candidates):
            return 3
        else:
            return 4

    return 1

def main():
    df_with_sprule = construct_sprule(df_mass)
    if 'SPRULE' in df_mass.columns:
        original_sprule = df_mass['SPRULE']
        constructed_sprule = df_with_sprule['SPRULE_const']
        match_rate = (original_sprule == constructed_sprule).mean()
        print(f"SPRULE match rate: {match_rate:.3f}")
    return df_with_sprule

if __name__ == "__main__":
    result = main() 

<h1 align="center">
  <br>
  <a href="https://www.bu.edu/spark/" target="_blank"><img src="https://www.bu.edu/spark/files/2023/08/logo.png" alt="BUSpark" width="200"></a>
  <br>
  CISS Molly Richards: Doubled -Up Estimate Coding <change to project name>
  <br>
</h1>

<h4 align="center"> A codebase for recreating the Linked Variables provided by IPUMS </h4> <change to repo short description>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#project-description">Project Description</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#next-steps">Next Steps</a>
</p>

## Key Features
This repository provides you with a codebase to recreate the following linked variables in the IPUMS and ACS microdata datasets:-
  - MOMLOC_HEAD - Mother's location in the household [of head]
  - POPLOC_HEAD - Father's location in the household [of head]
  - SPLOC_HEAD - Spouse's location in household [of head]
  - NCHILD_HEAD - Number of own children in the household [of head]
  - RELATE_HEAD - Relationship to household head [of head; general version] (Redundant Variable)
  - AGE_HEAD - Age [of head]
  - POVERTY_HEAD - Poverty status [of head]
  - GCRESPON_HEAD - Responsible for grandchildren [of head]

`IPUMS-linked-variables.py` provides you with the functions to recreate the above linked variables within the IPUMS dataset and validate their accuracy \
`acs-linked-variables.py` provides you with functions to recreate the above linked variables within the ACS dataset and validate their accuracy \
`pov_head.py` provides you with the functions to compute the POVERTY_HEAD of each household according to IPUMS' documentation \
`sprule.py` provides you with the functions to compute SPRULE within the IPUMS dataset and validate those values


 
## How To Use

To clone and run this application, you'll need <a href="https://git-scm.com" target="_blank">Git</a>
From your command line:

```bash
# Clone this repository
$ git clone https://github.com/BU-Spark/ds-ciss-population-estimates.git
```
The colab notebook mentioned in [this link](https://colab.research.google.com/drive/1RueEWVTUj839praUTcWMOMicdaRVRf2i#scrollTo=HpGnyuqne2We) provides you with detailed instructions to compute these variables in the ACS dataset and use them for analysis.
 
## Project Description

This project aims to improve how we measure “doubled-up homelessness,” which is when people temporarily stay with family or friends because they don’t have a stable place to live. Dr. Richard worked with community partners to use public American Community Survey (ACS) (Census Bureau) data to estimate doubling up. However, the estimates can have low levels of reliability due to the small sample size of the public-use ACS files. To address this limitation, Dr. Richard wants to apply to use the larger, restricted-use datasets, but needs help creating variables (described more below) not directly provided within this dataset (but that can be created using source variables). Broadly, the goal of the project is to develop the code needed to get more precise estimates of how many people are affected by this form of homelessness. 

## Documentation

The ACS dataset, specifically the ACS PUMS dataset (American Community Survey Public Use Microdata Sample), is a detailed, individual-level dataset from the U.S. Census Bureau. It provides anonymized information about people and households across the United States, including data on age, race, education, income, employment, housing, and more. 
The IPUMS dataset (Integrated Public Use Microdata Series) is a collection of high-quality, anonymized data from population censuses and surveys including the ACS Data. It is created by harmonizing the raw ACS data to make it easier to use and compare. IPUMS adds consistent variable names, clear documentation, and relationship links (like identifying who lives with whom). In short IPUMS repackages census and survey data making it simpler to use and ready for analysis.

Logic to compute these variables in the ACS dataset for each person in a household:-
- MOMLOC_HEAD: This variable shows the location of the mother of the head in the household
    - Process records grouped by household using the SERIALNO identifier
    - Within each household, find the household head (person with RELSHIPP = 20)
    - Search within the same household for female members (SEX = 2) who could plausibly be the mother
    - Among these candidates, check for people with a parental relationship with the head of household (RELSHIPP = 29)
    - If found, assign this person (SPORDER) as the MOMLOC_HEAD 
    - All members of a household in the dataset will have the same MOMLOC_HEAD
- POPLOC_HEAD: This variable shows the location of the father of the head in the household
    - The logic is the same as MOMLOC_HEAD but in step 3, search for male members (SEX = 1)
- SPLOC_HEAD: This variable shows the location of the spouse or partner of the head of household in the household
Process records grouped by household using the SERIALNO identifier
    - Within each household, find the household head (person with RELSHIPP = 20)
    - Search within the same household for a spouse or unmarried partner of the head (RELSHIPP = 21, 22, 23, 24)
    - If found, assign this person’s SPORDER as the SPLOC_HEAD, If no partner is found, set SPLOC_HEAD = 0
    - All members of a household in the dataset will have the same SP_LOC_HEAD
- NCHILD_HEAD: This variable shows the number of children of the head of the household
    - Process records grouped by household using the SERIALNO identifier
    - Within each household, find the household head (RELSHIPP = 20)
    - Identify household members with a child relationship to the head (RELSHIPP in [25, 26, 27], i.e., biological, step, or adopted children)
    - Count the number of such children and assign it as NCHILD_HEAD
    - All members of a household in the dataset will have the same NCHILD_HEAD
- AGE_HEAD: This variable shows the age of the head of the household
    - Use the HHLDRAGEP column directly from the ACS dataset (which stores the age of the household head) for each person
    - Assign this value to the variable AGE_HEAD
    - All members of a household will have the same AGE_HEAD
- POVERTY_HEAD: This variable shows the poverty status of the head of household
    - Process records grouped by household using the SERIALNO identifier
    - Within each household, find the household head (RELSHIPP = 20)
    - Extract the POVPIP (poverty status computed by ACS) value, from the ACS dataset, for the head of household
    - All members of a household in the dataset will have the same POVERTY_HEAD
    - This does not follow the logic mentioned in the IPUMS documentation due to high amount of inaccuracies in the computation 
- GCRESPON_HEAD: This variable indicates whether the household head is currently responsible for most of the basic needs of any grandchild(ren) under the age of 18 living in the same house
    - Process records grouped by household using the SERIALNO identifier
    - Within each household, find the head of household (RELSHIPP = 20)
    - Retrieve the value of the GCR field for the head (1 = Yes, 2 = No in ACS PUMS)
- RELATED_MOM: This variable shows the relationship of a person’s identified mother to the head of the household
    - For each person in the dataset, check if they have a valid link to a mother in the household (i.e., a non-zero value in the mother location pointer variable - ‘MOMLOC’)
    - If so, find the person within the same household whose person number matches the mother's location
    - Retrieve that person’s relationship to the head of the household
    - If no valid mother link exists or the mother is not found in the household, assign as missing
- RELATED_POP: This variable shows the relationship of a person’s identified father to the head of the household
    - The logic is the same as RELATED_MOM but in step 1, we check for a valid link to a father in the household (using the ‘POPLOC’ variable)
- AGE_MOM: This variable shows the age of a person’s identified mother in the household
    - For each person in the dataset, Check if they have a valid mother pointer (i.e., a non-zero, non-missing value in the mother location variable - ‘MOMLOC’)
    - If valid, locate the person within the same household whose person number matches the mother’s location
- AGE_POP: This variable shows the age of a person’s identified father in the household
    - The logic is the same as AGE_MOM but in step 1, we check for a valid link to a father in the household (using the ‘POPLOC’ variable)

RELATED_MOM, RELATED_POP, AGE_MOM, AGE_POP are variables that cannot be computed within the ACS dataset since the location of each person’s father and mother (MOMLOC and POPLOC) cannot be computed in that dataset which in turn requires the location of each person’s spouse in the household.

A detailed documentation is provided [here](https://docs.google.com/document/d/1qOHAGf4ztCqCUrJPbrIceaizuHiwB0Wpw7NjWjRs304/edit?tab=t.0).


## Next Steps

The next steps for this project would be computing the variables `MOMLOC` and `POPLOC` in ACS to implement the logic for the block Linked Variables. 
- A good place to start this process would be to implement a logic to find all the relationships provided in IPUMS within the ACS dataset which will help us compute variables like SPLOC, MOMLOC and POPLOC from the ACS dataset.



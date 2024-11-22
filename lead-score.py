"""
NAME: Zoe Carovano
DATE: November 22nd, 2024
FILE: lead_score.py
DESC: Calculates an algorithm to score leads from -100 to 100 
      on how likely they are to result in a closed deal based on 
      relevant attributes.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

"""
Iterates through lead data to count instances of unique values of a specified 
attribute and if the leads with these values are closed or non-closed deals.
Logs these instances in a table called a count table.
This is used to find correlations between attribute values and deal status.
Example: Could be used to count instances of Equity, would create a count 
table like this:
                  |  Closed Deal    |  Non-closed Deal
High Equity       |      25         |       45
Medium Equity     |      100        |       25
Low/No Equity     |      12         |       100
"""
def create_count_table(lead_data, attribute_name):

    # Initialize count table.
    data = []
    col_names = ['Closed Deal', 'Non-closed Deal']
    row_names = []
    count_table = pd.DataFrame(data, columns=col_names, index=row_names)

    # Initialize null table (a table which shows which of the lead data's attributes
    # are null)
    null_table = lead_data.isnull()

    # For each lead in the lead data:
    for lead in lead_data.index:
        # Find current lead's attribute value.
        attr_value = lead_data[attribute_name][lead]
        #If current attribute's value is not null, proceed.
        if (not (null_table[attribute_name][lead])):
            # If current attribute's value is not logged in the count table 
            # already, initialize a new row in the count table for this new value.
            if attr_value not in count_table.index:
                count_table.loc[attr_value] = [0, 0]
            # If deal status is not null:
            if (not (null_table['DEAL STATUS'][lead])):
                if lead_data['DEAL STATUS'][lead] in ['Seller Contract Received-Deal For Sale', 'Closed Deal-No Further Action']:
                    closed_count = count_table['Closed Deal'][attr_value]
                    count_table['Closed Deal'][attr_value] = closed_count + 1
                # Otherwise, current lead resulted in a non-closed deal. Add to 
                # count at (attribute value, Non-closed Deal) in count table.
                else:
                    nonclosed_count = count_table['Non-closed Deal'][attr_value]
                    count_table['Non-closed Deal'][attr_value] = nonclosed_count + 1

    return(count_table)

"""
Using the count table, creates a table that represents the counts of each 
unique attribute's values as a percentage of the total non-null leads of 
that deal type.
Example: Could be used to find the percentage of all closed deals 
with a given Equity type, as well as the percentage of all non-closed 
deals with that Equity type, resulting in a percent table like this:
                  |  Closed Deal    |  Non-closed Deal
High Equity       |      25%        |       10%
Medium Equity     |      50%        |       60%
Low/No Equity     |      25%        |       30%
"""
def create_percent_table(count_table):

    # Sum all non-null closed deals.
    total_closed_count = count_table['Closed Deal'].sum()
    #Sum all non-null non-closed deals.
    total_nonclosed_count = count_table['Non-closed Deal'].sum()

    # Make a deep copy of the count table to create the structure 
    # for the percent table.
    percent_table = count_table.copy(deep=True)

    # Divide all values from the count table column 'Closed Deal' by the total number of 
    # closed deals to get a fraction of closed deals with that attribute type. 
    percent_table['Closed Deal'] = percent_table['Closed Deal'].div(total_closed_count)
    # Divide all values from the count table column 'Non-closed Deal' by the total 
    # number of non-closed deals to get a fraction of non-closed deals with that 
    # attribute type. 
    percent_table['Non-closed Deal'] = percent_table['Non-closed Deal'].div(total_nonclosed_count)

    # Multiply all fractions by 100 to represent as percentages.
    percent_table = percent_table.mul(100)

    return percent_table

# Creates a bar graph to represent an attribute's percent or count table.
def create_bar_graph(table, attribute_name):

    # Create count graph.
    count_bar_graph = table.plot.bar()

    # Rotate x-axis attribute labels.
    count_bar_graph.set_xticklabels(table.index, rotation=20, ha='right')

    # Title graph.
    count_bar_graph.set_title(attribute_name + " Effect on Deal Status")

    plt.show()

# Take each percentage and find the difference between the closed and 
# non-closed deal percentages for the same attribute type.
def create_weight_table(percent_table):

    # Initialize weight table.
    weight_table = pd.DataFrame()

    # Subtract Non-closed deal percentage from Closed Deal percentage 
    # with same attribute type.
    weight_table['Difference'] = percent_table['Closed Deal'] - percent_table['Non-closed Deal']
    
    return weight_table

"""
Finds score scaler. The score scaler is multiplied by the lead score to 
normalize it on a scale from 0-200, perfect score gets 200, worst score gets 0
(Null handling: If an attr has null value, uses average weight)
"""
def find_score_scaler(att_weight_tables):
    perfect_score = 0
    worst_score = 0
    
    # For each attributes' corresponding weight table:
    for att_weight_table in att_weight_tables:
        # Add 100 to each weight to make them all positive
        att_weight_table[1]['Difference'] = att_weight_table[1]['Difference'] + 100
        # Find largest weight in current weight table.
        att_max = att_weight_table[1]['Difference'].max()
        # Find smallest weight in current weight table.
        att_min = att_weight_table[1]['Difference'].min()
        # Add current attr's largest weight to perfect score.
        perfect_score = perfect_score + att_max
        # Add current attr's smallest weight to worst score.
        worst_score = worst_score + att_min

    # Subtract worst score from perfect score to get the score range.
    score_range = perfect_score - worst_score
    # Divide 200 by the score range to get the score scaler, used to 
    # scale lead scores to within a range of 200.
    score_scaler = 200 / score_range

    return (score_scaler, worst_score)

#Find weighted score of a lead.
def find_lead_score(lead, att_weight_tables, score_scaler, worst_score):
    lead_score = 0
    null_table = lead.isnull()

    # For each attr's coorresponding weight table:
    for att_weight in att_weight_tables:
        # Get value for current attribute (ex/ "High Equity")
        lead_att_val = lead[att_weight[0]]
        curr_att_weight_table = att_weight[1]
        # If null:
        if null_table[att_weight[0]]:
            #Take the average of all the weights and use that as the weight.
            att_val_weight = curr_att_weight_table['Difference'].mean()
        #If value is present, use the specified weight.
        else:
            att_val_weight = curr_att_weight_table.loc[lead_att_val, 'Difference']
        # Add attribute value's weight to lead score.
        lead_score = lead_score + att_val_weight
    
    # Scale score with score scaler.
    lead_score = lead_score - worst_score
    lead_score = lead_score * score_scaler

    # Scale from -100 to 100.
    lead_score = lead_score - 100

    return lead_score

# Find and print likelihood of closing given a lead score.
def print_likelihood(lead_score):
    likelihood = ""
    if 75 <= lead_score >= 100:
        likelihood = "extremely likely"
    elif 50 <= lead_score < 75:
        likelihood = "quite likely"
    elif 25 <= lead_score < 50:
        likelihood = "relatively likely"
    elif 0 < lead_score < 25:
        likelihood = "somewhat likely"
    elif lead_score == 0:
        likelihood = "neither likely nor unlikely"
    elif -25 < lead_score < 0:
        likelihood = "somewhat unlikely"
    elif -50 < lead_score <= -25:
        likelihood = "relatively unlikely"
    elif -75 < lead_score <= -50:
        likelihood = "quite unlikely"
    elif -100 <= lead_score <= -50:
        likelihood = "extremely unlikely"
        
    print("Lead is\033[1m", likelihood, "\033[0mto result in a closed deal.")

def main():

    # Load Excel spreadsheet into pandas dataframe.
    lead_data = pd.read_excel('trial4.xlsx')

    # Pick lead attribute(s) to collect data on to create weights.
    attributes = ['Equity', 'Property Condition', 'Occupancy', 'How Soon Would You Like to Settle?', 'Property Type', 'Assigned  To - Ac Manager - name']
    att_weight_tables = []
    # For each attribute:
    for att in attributes:
        # Count how many closed and nonclosed deals are associated with each 
        # attribute value.
        count_table = create_count_table(lead_data, att)

        # Create a table of percentages to represent the proportions of each 
        # (attr, deal status) combo there are.
        percent_table = create_percent_table(count_table)

        # Display the percent table as a bar graph.
        # create_bar_graph(percent_table, attribute_name)

        # Create weights for all represented attr values.
        weight_table = create_weight_table(percent_table)
        att_weight_tables.append([att, weight_table])
    
    # Scale the scores between 0 and 100.
    (score_scaler, worst_score) = find_score_scaler(att_weight_tables)

    #Analyze a lead with the now calculated lead scoring algorithm.
    curr_lead = lead_data.iloc[8]
    print("The lead we are analyzing:")
    print(curr_lead)
    lead_score = find_lead_score(curr_lead, att_weight_tables, score_scaler, worst_score)
    lead_score = round(lead_score)
    print("Lead score of:\033[1m", lead_score, "\033[0m\n(Calculated between -100 and 100)")

    # Find and output likelihood of closing using lead score.
    print_likelihood(lead_score)

main()

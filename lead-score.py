import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#Count all unique value instances in lead data.
def count_one_attribute(lead_data, attribute_name):
    
    print(lead_data[attribute_name].value_counts())

#Used to compare string attribute instances with closed and non-closed deal occurances.
def count_attribute_with_deal(lead_data, attribute_name):

    #Initialize count table.
    data = []
    col_names = ['Closed Deal', 'Non-closed Deal']
    row_names = []
    count_table = pd.DataFrame(data, columns=col_names, index=row_names)

    null_table = lead_data.isnull()
    #For each row, check if is in count table.
    for lead in lead_data.index:
        prop_value = lead_data[attribute_name][lead]
        #If value is not null, proceed.
        if (not (null_table[attribute_name][lead])):
            #If property value not in rows column already, add row.
            if prop_value not in count_table.index:
                count_table.loc[prop_value] = [0, 0]
            
            # If lead is a closed deal, add to count of Closed Deal column.
            closed_deal_options = ['Seller Contract Received-Deal For Sale', 'Closed Deal-No Further Action']
            if lead_data['DEAL STATUS'][lead] in closed_deal_options:
                closed_count = count_table['Closed Deal'][prop_value]
                count_table['Closed Deal'][prop_value] = closed_count + 1
            # Otherwise, add to count of Non-closed Deal column.
            else:
                nonclosed_count = count_table['Non-closed Deal'][prop_value]
                count_table['Non-closed Deal'][prop_value] = nonclosed_count + 1

    return(count_table)

def create_percent_table(count_table):
    #Create a table of all the percentages of each attribute there are
    total_closed_count = count_table['Closed Deal'].sum()
    total_nonclosed_count = count_table['Non-closed Deal'].sum()

    percent_table = count_table.copy(deep=True)

    percent_table['Closed Deal'] = percent_table['Closed Deal'].div(total_closed_count)
    percent_table['Non-closed Deal'] = percent_table['Non-closed Deal'].div(total_nonclosed_count)
    percent_table = percent_table.mul(100)

    return percent_table

def create_bar_graph(count_table, attribute_name):
    # Create count graph
    count_bar_graph = count_table.plot.bar()

    # Rotate x-axis attribute labels
    count_bar_graph.set_xticklabels(count_table.index, rotation=20, ha='right')

    # Title graph
    count_bar_graph.set_title(attribute_name + " Effect on Deal Status")

    plt.show()

def create_weight_table(percent_table):
    #Take each percentage and find the difference between the closed and nonclosed deal percentages for the same attribute type.
    weight_table = pd.DataFrame()

    weight_table['Difference'] = percent_table['Closed Deal'] - percent_table['Non-closed Deal']
    return weight_table

def scale_weights(weight_table):
    # 1. add 100 to each weight to make them all positive
    weight_table['Difference'] = weight_table['Difference'] + 100

"""
1. add 100 to each weight to make them all positive
perfect_score = add up highest possible weight percentages from each category
lowest_score = add up lowest possible weight percentages from each category
lowest score needs to end up being 0, perfect score needs to end up being 100
score_range = perfect_score - lowest_score
goal is for range to be 100
x = 100/ score_range
- x is the score_scaler
score_scaler is applied to the lead score to normalize it on a scale from 
0-100, perfect score gets 100, worst score gets 0

how to handle nulls?

put in a 50 percent chance by default
how to find a 50 percent chance weight?
sum up all the weights in that attribute's weight table.
divide by the number of weights to get the average.
input that as the weight.

"""
def find_score_range(att_weight_tables):
    perfect_score = 0
    worst_score = 0
    
    for att_weight in att_weight_tables:
        att_max = att_weight[1]['Difference'].max()
        att_min = att_weight[1]['Difference'].min()
        perfect_score = perfect_score + att_max
        worst_score = worst_score + att_min
    score_range = perfect_score - worst_score
    score_scaler = 100 / score_range

    return (score_scaler, worst_score)

def average_weights(weight_table):
    return

def find_lead_score(lead, att_weight_tables, score_scaler, worst_score):
    # Go through single row, add up score.
    lead_score = 0
    null_table = lead.isnull()

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
    
    # Scale score with score scaler
    lead_score = lead_score - worst_score
    lead_score = lead_score * score_scaler

    #scales to -100 to 100
    lead_score = lead_score - 50
    lead_score = lead_score * 2

    return lead_score

def main():

    # Load Excel spreadsheet into pandas dataframe.
    lead_data = pd.read_excel('trial4.xlsx')

    # Pick a lead attribute to collect data on.
    attributes = ['Equity', 'Property Condition', 'Occupancy', 'How Soon Would You Like to Settle?', 'Property Type', 'Assigned  To - Ac Manager - name']
    att_weight_tables = []
    # Go through all attributes in attribute list. Find weights for each value in attributes' respective dataframe.
    for att in attributes:
        # Count how many closed and nonclosed deals are associated with each attribute value.
        count_table = count_attribute_with_deal(lead_data, att)

        # Create a table of the percentage times of each permutation between deal 
        # status and the attribute.
        percent_table = create_percent_table(count_table)

        weight_table = create_weight_table(percent_table)
        att_weight_tables.append([att, weight_table])

    #Add 100
    for att_weight in att_weight_tables:
        scale_weights(att_weight[1])
    
    (score_scaler, worst_score) = find_score_range(att_weight_tables)

    curr_lead = lead_data.iloc[8]
    print("The lead we are analyzing:")
    print(curr_lead)
    lead_score = find_lead_score(curr_lead, att_weight_tables, score_scaler, worst_score)
    lead_score = round(lead_score)
    print("Lead score of:\033[1m", lead_score, "\033[0m\n(Calculated between -100 and 100)")

    likelihood = ""
    #How good is the given lead score?
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

    # Display the percent table as a bar graph.\033[1mHello World!\033[0m
    #create_bar_graph(percent_table, attribute_name)

main()

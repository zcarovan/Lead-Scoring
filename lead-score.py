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
                #print(prop_value + " is not in the count table yet. Adding")
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
                #print("nonclosed_count: ", nonclosed_count)

    return(count_table)

def create_percent_table(count_table):
    #Create a table of all the percentages of each attribute there are
    total_closed_count = count_table['Closed Deal'].sum()
    total_nonclosed_count = count_table['Non-closed Deal'].sum()

    print("closed deal count: ", total_closed_count)
    print("non-closed deal count: ", total_nonclosed_count)

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

def main():

    # Load Excel spreadsheet into pandas dataframe.
    lead_data = pd.read_excel('trial4.xlsx')

    # Pick a lead attribute to collect data on.
    attribute_name = 'Seller Situation'

    # Count how many closed and nonclosed deals are associated with each attribute value.
    count_table = count_attribute_with_deal(lead_data, attribute_name)
    print(count_table)

    # Create a table of the percentage times of each permutation between deal 
    # status and the attribute.
    percent_table = create_percent_table(count_table)
    print(percent_table)

    # Display the percent table as a bar graph.
    create_bar_graph(percent_table, attribute_name)

main()
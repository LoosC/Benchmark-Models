import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import getDataToBePlotted
import petab
import seaborn as sns
#sns.set()


data_file_path = "https://raw.githubusercontent.com/LoosC/Benchmark-Models/" \
               "hackathon/hackathon_contributions_new_data_format/" \
               "Isensee_JCB2018/measurementData_Isensee_JCB2018.tsv"

condition_file_path = "https://raw.githubusercontent.com/LoosC/" \
                    "Benchmark-Models/hackathon/hackathon_contributions_" \
                    "new_data_format/Isensee_JCB2018/" \
                    "experimentalCondition_Isensee_JCB2018.tsv"

visualization_file_path = "https://raw.githubusercontent.com/LoosC/"\
                        "Benchmark-Models/visualization/hackathon_contributions"\
                        "_new_data_format/Isensee_JCB2018/visualizationSpecific"\
                        "ation_Isensee_JCB2018.tsv"

# import measurement data
measurement_data = petab.get_measurement_df(data_file_path)

# import experimental condition
experimental_condition = petab.get_condition_df(condition_file_path)

# import visualization specification
visualization_specification = pd.DataFrame.from_csv(
        visualization_file_path, sep="\t", index_col=None)

# Set Colormap
#ccodes = ['#8c510a','#bf812d','#dfc27d','#f6e8c3','#c7eae5','#80cdc1','#35978f','#01665e']
sns.set_palette("colorblind")

# get unique plotIDs
uni_plotIds, plotInd = np.unique(visualization_specification.plotId, return_index=True)

# Initiate subplots
num_subplot = len(uni_plotIds)
num_row = np.round(np.sqrt(num_subplot))
num_col = np.ceil(num_subplot / num_row)

# Set Options for plots
plt.rcParams['font.size'] = 10                  # possible options: see: plt.rcParams.keys()
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['figure.figsize'] = [20,10]

fig, ax = plt.subplots(int(num_row), int(num_col), squeeze=False) #, figsize=(20,10))



# loop over unique plotIds
for i_plot_id, var_plot_id in enumerate(uni_plotIds):

    # setting axis indices
    axx = int(np.ceil((i_plot_id+1)/ num_col))-1
    axy = int(((i_plot_id+1) - axx * num_col))-1

    # get indices for specific plotId
    ind_plot = visualization_specification['plotId'] == var_plot_id


    for i in visualization_specification[ind_plot].index.values:
        # get datasetID and independent variable of first entry of plot1
        dataset_id = visualization_specification.datasetId[i]
        indep_var = visualization_specification.independentVariable[i]

        # define index to reduce measurement_data to data linked to datasetId
        ind_dataset = measurement_data['datasetId'] == dataset_id

        # gather simulationConditionIds belonging to datasetId
        uni_condition_id = np.unique(measurement_data[ind_dataset].simulationConditionId)
        clmn_name_unique = 'simulationConditionId'

        # Case seperation indepParameter custom, time or condition
        if indep_var not in ['time', "condition"]:

            # extract conditions (plot input) from condition file
            ind_cond = experimental_condition.index.isin(uni_condition_id)
            conditions = experimental_condition[ind_cond][indep_var]

            ms = getDataToBePlotted.getDataToBePlotted(visualization_specification, measurement_data, uni_condition_id,
                                                       i, clmn_name_unique)
            # set xScale
            if visualization_specification.xScale[i] == 'lin':
                ax[axx, axy].set_xscale("linear")
            elif visualization_specification.xScale[i] == 'log10':
                ax[axx, axy].set_xscale("log")
            elif visualization_specification.xScale[i] == 'order':        # equidistant
                ax[axx, axy].set_xscale("linear")
                # check if conditions are monotone decreasing or increasing
                if np.all(np.diff(conditions) < 0):             # monotone decreasing
                    xlabel = conditions[::-1]                   # reversing
                    conditions = range(len(conditions))[::-1]   # reversing
                    ax[axx, axy].set_xticks(range(len(conditions)), xlabel)
                elif np.all(np.diff(conditions) > 0):
                    print('monotone increasing')
                    xlabel = conditions
                    conditions = range(len(conditions))
                    ax[axx, axy].set_xticks(range(len(conditions)), xlabel)
                else:
                    print('Error: x-conditions do not coincide, some are mon. increasing, some monotonically decreasing')


            if visualization_specification.plotTypeData[i] == 'MeanAndSD':
                ax[axx, axy].errorbar(conditions, ms['mean'], ms['sd'], linestyle='-', marker='.',
                                        label = visualization_specification[ind_plot].legendEntry[i])
            elif visualization_specification.plotTypeData[i] == 'MeanAndSEM':
                ax[axx, axy].errorbar(conditions, ms['mean'], ms['sem'], linestyle='-', marker='.',
                                      label=visualization_specification[ind_plot].legendEntry[i])
            elif visualization_specification.plotTypeData[i] == 'replicate':  # plotting all measurement data
                for ii in range(0,len(ms['repl'])):
                    for k in range(0,len(ms.repl[ii])):
                        ax[axx, axy].plot(conditions[conditions.index.values[ii]], ms.repl[ii][ms.repl[ii].index.values[k]],
                                          'x')
            ax[axx, axy].legend()
            ax[axx, axy].set_title(visualization_specification.plotName[i])


        elif indep_var == 'condition':

            ms = getDataToBePlotted.getDataToBePlotted(visualization_specification, measurement_data, uni_condition_id, i,
                                                       clmn_name_unique)
            # barplot
            x_pos = range(len(visualization_specification[ind_plot]))       # how many x-values (how many bars)
            x_name = visualization_specification[ind_plot].legendEntry[i]

            ax[axx, axy].bar(x_name, ms['mean'], yerr=ms['sd'])
            ax[axx, axy].set_title(visualization_specification.plotName[i])

        elif indep_var == 'time':

            # obtain unique observation times
            uni_times = np.unique(measurement_data[ind_dataset].time)
            clmn_name_unique = 'time'

            # group measurement values for each conditionId/unique time
            ms = getDataToBePlotted.getDataToBePlotted(visualization_specification, measurement_data, uni_times, i,
                                                       clmn_name_unique)

            ax[axx, axy].errorbar(uni_times, ms['mean'], ms['sd'], linestyle='-', marker='.',
                         label=visualization_specification[ind_plot].legendEntry[i]
                         )
            ax[axx, axy].legend()
            ax[axx, axy].set_title(visualization_specification.plotName[i])

    ax[axx, axy].set_xlabel(visualization_specification.independentVariableName[i])


plt.show()
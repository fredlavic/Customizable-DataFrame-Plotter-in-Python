# -*- coding: utf-8 -*-
"""
@author: Frédérik Lavictoire
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def stacked_bar_graph(ax, dataframes, x_var, y_var,
                      years_to_compare, data_to_compare,
                      data_label_dict, color_dict,
                      scenario_names, baseline_year,
                      baseline_name, specific_variable_title=False,
                      specific_variable_name=False, legend_position=False,
                      year_height=3):
    """


    Parameters
    ----------
    ax : axes._axes.Axes
        AN AXES OBJECT ENCAPSULATES ALL THE ELEMENTS OF AN INDIVIDUAL
        (SUB-)PLOT IN A FIGURE.
    dataframes : list of DataFrame
        LIST OF THE DATAFRAMES THAT WILL BE OUTPUT IN THE GRAPH BASED ON
        DIFFERENT SCENARIOS.
    x_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE X AXIS IN THE GRAPH. USUALLY,
        THIS VARIABLE IS REPRESENTS YEARS.
    y_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE Y AXIS IN THE GRAPH.
    years_to_compare : list of str
        SPECIFIC YEARS TO COMPARE. HAS TO BE RELATED TO x_var.
    data_to_compare : list of str
        SPECIFIC DATA TO COMPARE. HAS TO BE RELATED TO y_var. THE ORDER
        OF THIS LIST WILL DETERMINE THE PLOT ORDER FROM BOTTOM TO TOP.
    data_label_dict : dict
        LABELS THAT WE WANT TO BE DISPLAYED IN THE GRAPH BASED ON THE
        ORIGINAL NAMES IN THE CONTAINER OBJECT.
    color_dict : dict
        COLORS THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN THE
        CONTAINER OBJECT.
    scenario_names : list of str
        LABELS OF THE DIFFERENT SCENARIOS WE WANT DISPLAYED. NEEDS TO BE IN
        THE SAME ORDER OF SCENARIOS AS IN THE dataframes list.
    baseline_year : str
        BASELINE YEAR FOR THE FIRST BAR IN THE GRAPH.
    baseline_name : str
        BASELINE NAME.
    specific_variable_title : str, optional
        VARIABLE THAT WE WANT TO BE DISPLAYED. NARROWS DOWN THE DISPLAYED
        RESULTS. The default is False.
    specific_variable_name : str, optional
        SPECIFIC VARIABLE TO NARROW DOWN THE DISPLAYED RESULTS. HAS TO BE
        RELATED TO specific_variable_title. The default is False.
    legend_position : tuple, optional
        USE IF YOU WANT TO SPECIFY THE LEGEND POSITION. THE FORMAT IS (X,Y).
    year_height : float, optional
        SPECIFY THIS NUMBER IF YOU WANT THE YEARS TO BE DISPLAYED HIGHER OR
        LOWER.

    Returns
    -------
    df_to_analyze : DataFrame
        DataFrame of the graph output.

    """

    df_list = []
    for i, scenarios in enumerate(dataframes):  # For every scenario
        df = scenarios
        # Add a mark to identify which scenario it is
        df['Scenario'] = scenario_names[i]

        # To only show the years and data to compare
        df = df[df[x_var].isin(years_to_compare)]
        df = df[df[y_var].isin(data_to_compare)]

        # If we want to look at only one country for example
        if specific_variable_title and specific_variable_name:
            df = df.loc[df[specific_variable_title] == specific_variable_name]

        # To have only one bar for the baseline year
        if (scenario_names[i] != baseline_name):
            df = df.loc[df[x_var] != baseline_year]

        df['plot order'] = i  # To plot the bars in the right order

        if 'value' in df.columns:  # Either 'level' or 'value'
            df = df.pivot_table(index=[x_var, 'Scenario', 'plot order'],
                                columns=y_var, values='value')
        else:
            df = df.pivot_table(index=[x_var, 'Scenario', 'plot order'],
                                columns=y_var, values='level')
        df_list.append(df)

    df_to_analyze = pd.concat(df_list)
    df_to_analyze = df_to_analyze.fillna(value=0)
    df_to_analyze = df_to_analyze.sort_values(by=[x_var, 'plot order'])

    # Setting all the labels that will be shown in the right order
    scenario_labels = [df_to_analyze.index[i][1]
                       for i in range(len(df_to_analyze))]
    # Position of the years and vertical grey lines
    year_positions, vline_positions = [0], []
    bottom = np.zeros(len(df_to_analyze))
    scenario_positions = np.zeros(len(df_to_analyze))

    for i, data in enumerate(data_to_compare):  # For all the types of data
        position = 0
        data_label = data_label_dict[data]
        color = color_dict[data]
        for j in range(len(df_to_analyze)):  # For all the bars to plot
            df = df_to_analyze.iloc[j]  # Select each row

            # If we have a new cluster, do a bigger space
            if (df.name[1] == scenario_names[0]) and j != 0:
                vline_positions.append(position)
                position += 1

                if len(scenario_names) % 2 != 0:  # If odd number of scenarios
                    year_positions.append(position+int(len(scenario_names)/2))
                else:  # If even number of scenario
                    year_positions.append(position+len(scenario_names)/2-0.5)
            scenario_positions[j] = position

            if j == 0:  # To avoid multiple legends for the same data
                ax.bar(position, df[data], width=0.5, bottom=bottom[j],
                       color=color, label=data_label, zorder=3)
            else:
                ax.bar(position, df[data], width=0.5, bottom=bottom[j],
                       color=color, zorder=3)
            bottom[j] += df[data]
            position += 1

    # Remove repetitions from loop
    year_positions = year_positions[:len(years_to_compare)]
    vline_positions = vline_positions[:len(years_to_compare) - 1]

    # Add a text box to show the year for multiple scenarios
    for i, year in enumerate(years_to_compare):
        ax.text(year_positions[i], (ax.get_ylim()[0] -
                                    ax.get_ylim()[1])/year_height,
                year, ha='center')

        if i >= 1:  # Add the gray lines
            ax.annotate('', xy=(vline_positions[i - 1], 0),
                        xycoords='data',
                        xytext=(vline_positions[i - 1],
                                (ax.get_ylim()[0] -
                                 ax.get_ylim()[1])/year_height),
                        arrowprops=dict(arrowstyle="-",
                                        color='lightgray'))
    # Add scenario names and legend
    ax.set_xticks(scenario_positions, scenario_labels, rotation=90)
    handles, labels = ax.get_legend_handles_labels()
    if legend_position:  # Specify legend position
        ax.legend(reversed(handles), reversed(labels),
                  bbox_to_anchor=legend_position)
    else:
        ax.legend(reversed(handles), reversed(labels))

    return df_to_analyze


def graph_2_variables(kind, ax, dataframe, x_var, y_var,
                      years_to_compare, data_to_compare,
                      data_label_dict, color_dict, linestyle=False,
                      marker_dict=False, linewidth = False,
                      legend_position=False):
    """


    Parameters
    ----------
    kind : str
        CHOOSES THE TYPE OF GRAPH TO PLOT.
        CAN BE EITHER line, area, bar or barh.
    ax : axes._axes.Axes
        AN AXES OBJECT ENCAPSULATES ALL THE ELEMENTS OF AN INDIVIDUAL
        (SUB-)PLOT IN A FIGURE.
    dataframe : DataFrame
        DATAFRAME THAT WILL BE OUTPUT IN THE GRAPH.
    x_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE X AXIS IN THE GRAPH.
        USUALLY, THIS VARIABLE IS REPRESENTS YEARS.
    y_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE Y AXIS IN THE GRAPH.
    years_to_compare : list of str
        SPECIFIC YEARS TO COMPARE. HAS TO BE RELATED TO x_var.
    data_to_compare : list of str
        SPECIFIC DATA TO COMPARE. HAS TO BE RELATED TO y_var.
    data_label_dict : dict
        LABELS THAT WE WANT TO BE DISPLAYED IN THE GRAPH BASED ON THE
        ORIGINAL NAMES IN THE CONTAINER OBJECT.
    color_dict : dict
        COLORS THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN THE
        CONTAINER OBJECT.
    linestyle : dict, optional
        LINESTYLE THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    marker_dict : dict, optional
        MARKERSTYLES THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    linewidth : dict, optional
        LINEWIDTH THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    legend_position : tuple, optional
        USE IF YOU WANT TO SPECIFY THE LEGEND POSITION. THE FORMAT IS (X,Y).

    Returns
    -------
    df_to_plot : DataFrame
        DataFrame of the graph output.

    """

    df = dataframe
    df = df[df[x_var].isin(years_to_compare)]
    df = df[df[y_var].isin(data_to_compare)]
    df = df.astype({x_var: int})  # So that the years are numbers and not str
    df_list = []
    legend = []
    for data in data_to_compare:
        df_to_analyze = df.loc[df[y_var] == data]

        # Adding markers
        if marker_dict and kind == 'line':
            if 'value' in df_to_analyze.columns:
                df_to_analyze.plot(kind='scatter', x=x_var, y='value',
                                   ax=ax, legend=False,
                                   color=color_dict[data],
                                   marker=marker_dict[data], s=20)
            else:
                df_to_analyze.plot(kind='scatter', x=x_var, y='level',
                                   ax=ax, legend=False,
                                   color=color_dict[data],
                                   marker=marker_dict[data], s=20)
        if 'value' in df_to_analyze.columns:
            df_to_analyze = df_to_analyze.pivot_table(index=[x_var],
                                                      columns=y_var,
                                                      values='value')
        else:
            df_to_analyze = df_to_analyze.pivot_table(index=[x_var],
                                                      columns=y_var,
                                                      values='level')
        df_list.append(df_to_analyze)
        legend.append(data_label_dict[data])

    df_to_plot = pd.concat(df_list, axis=1)
    if kind == 'line':
        if linestyle and linewidth:# If we specify the linestyle and linewidth
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linestyle = linestyle[column],
                                        linewidth = linewidth[column])
        elif linestyle: # If we specify the linestyle
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linestyle = linestyle[column])
        elif linewidth: # If we specify the linewidth
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linewidth = linewidth[column])
        else: # If we do not specify either linestyle nor linewidth
            df_to_plot.plot(kind=kind, ax=ax, color=color_dict, legend=False)
    else: # If not a line graph
        df_to_plot.plot(kind=kind, ax=ax, color=color_dict, legend=False)

    handles, labels = ax.get_legend_handles_labels()
    if legend_position:  # Specify legend position
        ax.legend(reversed(handles), reversed(legend),
                  bbox_to_anchor=legend_position)
    else:
        ax.legend(reversed(handles), reversed(legend))

    return df_to_plot


def graph_3_variables(kind, ax, dataframe, x_var, y_var, z_var,
                      years_to_compare, y_var_to_compare, z_var_to_compare,
                      y_var_label_dict, color_dict, z_var_label_dict,
                      linestyle=False, marker_dict=False,
                      linewidth = False, legend_position=False):
    """


    Parameters
    ----------
    kind : str
        CHOOSES THE TYPE OF GRAPH TO PLOT.
        CAN BE EITHER line, area, bar or barh.
    ax : axes._axes.Axes
        AN AXES OBJECT ENCAPSULATES ALL THE ELEMENTS OF AN INDIVIDUAL
        (SUB-)PLOT IN A FIGURE.
    dataframe : Container object
        GDX FILE THAT WILL BE OUTPUT IN THE GRAPH.
    x_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE X AXIS IN THE GRAPH. USUALLY,
        THIS VARIABLE IS REPRESENTS YEARS.
    y_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE Y AXIS IN THE GRAPH.
    z_var : str
        OTHER VARIABLE THAT WILL BE DISPLAYED ON THE Y AXIS IN THE GRAPH.
    years_to_compare : list of str
        SPECIFIC YEARS TO COMPARE. HAS TO BE RELATED TO x_var.
    data_to_compare : list of str
        SPECIFIC DATA TO COMPARE. HAS TO BE RELATED TO y_var.
    z_var_to_compare : list of str
        SPECIFIC DATA TO COMPARE. HAS TO BE RELATED TO z_var.
    y_var_label_dict : dict
        LABELS THAT WE WANT TO BE DISPLAYED IN THE GRAPH BASED ON THE
        ORIGINAL NAMES IN THE CONTAINER OBJECT.
    color_dict : dict
        COLORS THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN THE
        CONTAINER OBJECT.
    z_var_label_dict : dict
        LABELS THAT WE WANT TO BE DISPLAYED IN THE GRAPH BASED ON THE
        ORIGINAL NAMES IN THE CONTAINER OBJECT.
    linestyle : dict, optional
        LINESTYLE THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    marker_dict : dict, optional
        MARKERSTYLES THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    linewidth : dict, optional
        LINEWIDTH THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    legend_position : tuple, optional
        USE IF YOU WANT TO SPECIFY THE LEGEND POSITION. THE FORMAT IS (X,Y).

    Returns
    -------
    df_to_plot : DataFrame
        DataFrame of the graph output.

    """

    df = dataframe
    df = df[df[x_var].isin(years_to_compare)]
    df = df[df[y_var].isin(y_var_to_compare)]
    df = df.astype({x_var: int})
    df_list = []
    legend = []
    for data in y_var_to_compare:
        for data_z in z_var_to_compare:
            df_to_analyze = df.loc[(df[y_var] == data) & (df[z_var] == data_z)]

            if marker_dict and kind == 'line':
                if 'value' in df_to_analyze.columns:

                    df_to_analyze.plot(kind='scatter', x=x_var,
                                       y='value', ax=ax,
                                       legend=False,
                                       color=color_dict[(data,  data_z)],
                                       marker=marker_dict[(data,  data_z)],
                                       s=20)
                else:
                    df_to_analyze.plot(kind='scatter', x=x_var,
                                       y='level', ax=ax,
                                       legend=False,
                                       color=color_dict[(data,  data_z)],
                                       marker=marker_dict[(data,  data_z)],
                                       s=20)
            if 'value' in df_to_analyze.columns:
                df_to_analyze = df_to_analyze.pivot_table(index=[x_var],
                                                          columns=[
                                                              y_var, z_var],
                                                          values='value')
            else:
                df_to_analyze = df_to_analyze.pivot_table(index=[x_var],
                                                          columns=[
                                                              y_var, z_var],
                                                          values='level')
            df_list.append(df_to_analyze)
            legend.append(y_var_label_dict[data] + ' ' +
                          z_var_label_dict[data_z])

    df_to_plot = pd.concat(df_list, axis=1)

    if kind == 'line':
        if linestyle and linewidth:# If we specify the linestyle and linewidth
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linestyle = linestyle[column],
                                        linewidth = linewidth[column])
        elif linestyle: # If we specify the linestyle
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linestyle = linestyle[column])
        elif linewidth: # If we specify the linewidth
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linewidth = linewidth[column])
        else: # If we do not specify either linestyle nor linewidth
            df_to_plot.plot(kind=kind, ax=ax, color=color_dict, legend=False)
    else: # If not a line graph
        df_to_plot.plot(kind=kind, ax=ax, color=color_dict, legend=False)

    handles, labels = ax.get_legend_handles_labels()
    if legend_position:  # Specify legend position
        ax.legend(reversed(handles), reversed(legend),
                  bbox_to_anchor=legend_position)
    else:
        ax.legend(reversed(handles), reversed(legend))

    return df_to_plot


def graph_mulitple_scenarios_2_variables(kind, ax, dataframes, x_var, y_var,
                                         years_to_compare, data_to_compare,
                                         data_label_dict, color_dict,
                                         scenario_names, linestyle=False,
                                         marker_dict=False,
                                         linewidth = False,
                                         legend_position=False):
    """


    Parameters
    ----------
    kind : str
        CHOOSES THE TYPE OF GRAPH TO PLOT.
        CAN BE EITHER line, area, bar or barh.
    ax : axes._axes.Axes
        AN AXES OBJECT ENCAPSULATES ALL THE ELEMENTS OF AN INDIVIDUAL
        (SUB-)PLOT IN A FIGURE.
    dataframes : list
        LIST OF THE GDX FILES THAT WILL BE OUTPUT IN THE GRAPH BASED ON
        DIFFERENT SCENARIOS.
    x_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE X AXIS IN THE GRAPH. USUALLY,
        THIS VARIABLE IS REPRESENTS YEARS.
    y_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE Y AXIS IN THE GRAPH.
    years_to_compare : list of str
        SPECIFIC YEARS TO COMPARE. HAS TO BE RELATED TO x_var.
    data_to_compare : list of str
        SPECIFIC DATA TO COMPARE. HAS TO BE RELATED TO y_var.
    data_label_dict : dict
        LABELS THAT WE WANT TO BE DISPLAYED IN THE GRAPH BASED ON THE
        ORIGINAL NAMES IN THE CONTAINER OBJECT.
    color_dict : dict
        COLORS THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN THE
        CONTAINER OBJECT.
    scenario_names : list of str
        LABELS OF THE DIFFERENT SCENARIOS WE WANT DISPLAYED. NEEDS TO BE IN
        THE SAME ORDER OF SCENARIOS AS IN THE dataframes list.
    linestyle : dict, optional
        LINESTYLE THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    marker_dict : dict, optional
        MARKERSTYLES THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    linewidth : dict, optional
        LINEWIDTH THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    legend_position : tuple, optional
        USE IF YOU WANT TO SPECIFY THE LEGEND POSITION. THE FORMAT IS (X,Y).

    Returns
    -------
    df_to_plot : DataFrame
        DataFrame of the graph output.

    """

    df_list = []
    for i, scenario in enumerate(dataframes):
        df = scenario
        df['Scenario'] = scenario_names[i]
        df = df[df[x_var].isin(years_to_compare)]
        df = df[df[y_var].isin(data_to_compare)]
        df = df.astype({x_var: int})
        df_list.append(df)

    df_to_analyze = pd.concat(df_list)
    df_list = []
    legend = []
    for data in data_to_compare:
        for scenario in scenario_names:
            df = df_to_analyze.loc[(df_to_analyze.Scenario == scenario) &
                                   (df_to_analyze[y_var] == data)]

            if marker_dict and kind == 'line':
                if 'value' in df_to_analyze.columns:

                    df.plot(kind='scatter', x=x_var, y='value', ax=ax,
                            legend=False,
                            color=color_dict[(data,  scenario)],
                            marker=marker_dict[(data,  scenario)],
                            s=20)
                else:
                    df.plot(kind='scatter', x=x_var, y='level', ax=ax,
                            legend=False,
                            color=color_dict[(data,  scenario)],
                            marker=marker_dict[(data,  scenario)],
                            s=20)
            if 'value' in df.columns:
                df = df.pivot_table(index=[x_var],
                                    columns=[y_var, 'Scenario'],
                                    values='value')
            else:
                df = df.pivot_table(index=[x_var],
                                    columns=[y_var, 'Scenario'],
                                    values='level')
            df_list.append(df)
            legend.append(data_label_dict[data] + ' ' + scenario)

    df_to_plot = pd.concat(df_list, axis=1)
    if kind == 'line':
        if linestyle and linewidth:# If we specify the linestyle and linewidth
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linestyle = linestyle[column],
                                        linewidth = linewidth[column])
        elif linestyle: # If we specify the linestyle
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linestyle = linestyle[column])
        elif linewidth: # If we specify the linewidth
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linewidth = linewidth[column])
        else: # If we do not specify either linestyle nor linewidth
            df_to_plot.plot(kind=kind, ax=ax, color=color_dict, legend=False)
    else: # If not a line graph
        df_to_plot.plot(kind=kind, ax=ax, color=color_dict, legend=False)

    handles, labels = ax.get_legend_handles_labels()
    if legend_position:  # Specify legend position
        ax.legend(reversed(handles), reversed(legend),
                  bbox_to_anchor=legend_position)
    else:
        ax.legend(reversed(handles), reversed(legend))

    return df_to_plot


def graph_mulitple_scenarios_3_variables(kind, ax, dataframes, x_var, y_var,
                                         z_var, years_to_compare,
                                         y_var_to_compare, z_var_to_compare,
                                         y_var_label_dict, color_dict,
                                         z_var_label_dict, scenario_names,
                                         linestyle=False, marker_dict=False,
                                         linewidth = False,
                                         legend_position=False):
    """


    Parameters
    ----------
    kind : str
        CHOOSES THE TYPE OF GRAPH TO PLOT.
        CAN BE EITHER line, area, bar or barh.
    ax : axes._axes.Axes
        AN AXES OBJECT ENCAPSULATES ALL THE ELEMENTS OF AN INDIVIDUAL
        (SUB-)PLOT IN A FIGURE.
    dataframes : list
        LIST OF THE GDX FILES THAT WILL BE OUTPUT IN THE GRAPH BASED ON
        DIFFERENT SCENARIOS.
    x_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE X AXIS IN THE GRAPH. USUALLY,
        THIS VARIABLE IS REPRESENTS YEARS.
    y_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE Y AXIS IN THE GRAPH.
    z_var : str
        OTHER VARIABLE THAT WILL BE DISPLAYED ON THE Y AXIS IN THE GRAPH.
    years_to_compare : list of str
        SPECIFIC YEARS TO COMPARE. HAS TO BE RELATED TO x_var.
    data_to_compare : list of str
        SPECIFIC DATA TO COMPARE. HAS TO BE RELATED TO y_var.
    z_var_to_compare : list of str
        SPECIFIC DATA TO COMPARE. HAS TO BE RELATED TO z_var.
    y_var_label_dict : dict
        LABELS THAT WE WANT TO BE DISPLAYED IN THE GRAPH BASED ON THE
        ORIGINAL NAMES IN THE CONTAINER OBJECT.
    color_dict : dict
        COLORS THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN THE
        CONTAINER OBJECT.
    z_var_label_dict : dict
        LABELS THAT WE WANT TO BE DISPLAYED IN THE GRAPH BASED ON THE
        ORIGINAL NAMES IN THE CONTAINER OBJECT.
    scenario_names : list of str
        LABELS OF THE DIFFERENT SCENARIOS WE WANT DISPLAYED. NEEDS TO BE IN
        THE SAME ORDER OF SCENARIOS AS IN THE dataframes list.
    linestyle : dict, optional
        LINESTYLE THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    marker_dict : dict, optional
        MARKERSTYLES THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    linewidth : dict, optional
        LINEWIDTH THAT WILL BE DISPLAYED BASED ON THE ORIGINAL NAMES IN
        THE CONTAINER OBJECT FOR A LINE GRAPH.
    legend_position : tuple, optional
        USE IF YOU WANT TO SPECIFY THE LEGEND POSITION. THE FORMAT IS (X,Y).

    Returns
    -------
    df_to_plot : DataFrame
        DataFrame of the graph output.

    """

    df_list = []
    for i, scenario in enumerate(dataframes):
        df = scenario
        df['Scenario'] = scenario_names[i]
        df = df[df[x_var].isin(years_to_compare)]
        df = df[df[y_var].isin(y_var_to_compare)]
        df = df[df[z_var].isin(z_var_to_compare)]
        df = df.astype({x_var: int})
        df_list.append(df)

    df_to_analyze = pd.concat(df_list)
    df_list = []
    legend = []
    for data_y in y_var_to_compare:
        for data_z in z_var_to_compare:
            for scenario in scenario_names:
                df = df_to_analyze.loc[(df_to_analyze.Scenario == scenario) &
                                       (df_to_analyze[y_var] == data_y) &
                                       (df_to_analyze[z_var] == data_z)]

                if marker_dict and kind == 'line':
                    if 'value' in df_to_analyze.columns:
                        df.plot(kind='scatter', x=x_var, y='value',
                                ax=ax, legend=False,
                                color=color_dict[(data_y,  data_z, scenario)],
                                marker=marker_dict[(
                                    data_y,  data_z, scenario)],
                                s=20)
                    else:
                        df.plot(kind='scatter', x=x_var, y='level',
                                ax=ax, legend=False,
                                color=color_dict[(data_y,  data_z, scenario)],
                                marker=marker_dict[(
                                    data_y,  data_z, scenario)],
                                s=20)
                if 'value' in df.columns:
                    df = df.pivot_table(index=[x_var],
                                        columns=[y_var, z_var, 'Scenario'],
                                        values='value')
                else:
                    df = df.pivot_table(index=[x_var],
                                        columns=[y_var, z_var, 'Scenario'],
                                        values='level')
                df_list.append(df)
                legend.append(y_var_label_dict[data_y] + ' ' +
                              z_var_label_dict[data_z] + ' ' + scenario)

    df_to_plot = pd.concat(df_list, axis=1)
    if kind == 'line':
        if linestyle and linewidth:# If we specify the linestyle and linewidth
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linestyle = linestyle[column],
                                        linewidth = linewidth[column])
        elif linestyle: # If we specify the linestyle
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linestyle = linestyle[column])
        elif linewidth: # If we specify the linewidth
            for column in df_to_plot.columns:
                df_to_plot[column].plot(kind=kind, ax=ax, color=color_dict,
                                        legend=False,
                                        linewidth = linewidth[column])
        else: # If we do not specify either linestyle nor linewidth
            df_to_plot.plot(kind=kind, ax=ax, color=color_dict, legend=False)
    else: # If not a line graph
        df_to_plot.plot(kind=kind, ax=ax, color=color_dict, legend=False)

    handles, labels = ax.get_legend_handles_labels()
    if legend_position:  # Specify legend position
        ax.legend(reversed(handles), reversed(legend),
                  bbox_to_anchor=legend_position)
    else:
        ax.legend(reversed(handles), reversed(legend))

    return df_to_plot


def verification(gdx_files, name, x_var, y_var, years_to_compare,
                 data_to_compare, z_var=False, z_var_to_compare=False):
    """


    Parameters
    ----------
    gdx_files : list
        LIST OF THE GDX FILES THAT WILL BE OUTPUT IN THE GRAPH BASED ON
    x_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE X AXIS IN THE GRAPH. USUALLY,
        THIS VARIABLE IS REPRESENTS YEARS.
    y_var : str
        VARIABLE THAT WILL BE DISPLAYED ON THE Y AXIS IN THE GRAPH.
    z_var : str
        OTHER VARIABLE THAT WILL BE DISPLAYED ON THE Y AXIS IN THE GRAPH.
    years_to_compare : list of str
        SPECIFIC YEARS TO COMPARE. HAS TO BE RELATED TO x_var.
    data_to_compare : list of str
        SPECIFIC DATA TO COMPARE. HAS TO BE RELATED TO y_var.
    z_var : str, optional
        OTHER VARIABLE THAT WILL BE DISPLAYED ON THE Y AXIS IN THE GRAPH.
        The default is False.
    z_var_to_compare : list of str, optional
        SPECIFIC DATA TO COMPARE. HAS TO BE RELATED TO z_var.
        The default is False.

    Returns
    -------
    bool
        WILL CHECK IF THE name IS IN THE gdx_files, THEN WILL CHECK IF
        x_var, y_var, years_to_compare, data_to_compare, z_var AND
        z_var_to_compare ARE IN THE DATAFRAME ASSOCIATED WITH THE name. IF
        ONE ERROR IS FOUND, WILL DISPLAY CUSTOMIZED MESSAGE TO
        HELP FIND THE MISTAKE, ELSE IT WILL OUTPUT A LIST OF DATAFRAMES.

    """
    df_list = []
    for files in gdx_files:
        try:
            files[name].records
        except AttributeError:
            print(name + ' is not in one of the gdx file you gave.')
            print('Look at the gdx dictionnary to find what are the values')
            return False

        df = files[name].records
        try:
            df[x_var]
        except KeyError:
            print(x_var + ' is not a column label in this dataframe.')
            print('Here are your options:')
            print(df.columns)
            return False
        try:
            df[y_var]
        except KeyError:
            print(y_var + ' is not a column label in this dataframe.')
            print('Here are your options:')
            print(df.columns)
            return False

        for years in years_to_compare:
            if sum(df[x_var] == years) == 0:
                print('One of the data you want to analyze can\'t be found')
                print('Here are your options for ' + x_var)
                print(df[x_var].drop_duplicates())
                return False

        for data in data_to_compare:
            if sum(df[y_var] == data) == 0:
                print('One of the data you want to analyze can\'t be found')
                print('Here are your options for ' + y_var)
                print(df[y_var].drop_duplicates())
                return False

        if z_var and z_var_to_compare:
            try:
                df[z_var]
            except KeyError:
                print(z_var + ' is not a column label in this dataframe.')
                print('Here are your options:')
                print(df.columns)
                return False

            for data in z_var_to_compare:
                if sum(df[z_var] == data) == 0:
                    print('The data you want to analyze can\'t be found')
                    print('Here are your options for ' + z_var)
                    print(df[z_var].drop_duplicates())
                    return False

        df_list.append(files[name].records)

    return df_list


def data_description(data_container):
    """


    Parameters
    ----------
    data_container : Container object
        GDX FILE STORED AS A DATA CONTAINER FROM THE TRANSFER MODULE

    Returns
    -------
    list of DataFrames
        LIST OF DATAFRAMES GIVING A SUMMARY OF THE CONTAINER FILES. SHOWS
        ALL THE ALIASES, EQUATIONS, PARAMETERS, SETS AND VARIABLES
    data_dict : dict
        DICTIONNARY SHOWING THE COMPLETE NAME OF ALL THE DATA WITH THE
        ABREVIATED VERSION.

    """

    # DataFrame with all the aliases
    desc_aliases = data_container.describeAliases()
    # DataFrame with all the equations
    desc_equations = data_container.describeEquations()
    # DataFrame with all the parameters
    desc_parameters = data_container.describeParameters()
    # DataFrame with all the set
    desc_sets = data_container.describeSets()
    # DataFrame with all the variables
    desc_variables = data_container.describeVariables()
    # Dictionnary of all the names
    data_dict = {data_container.data[data].name: data_container.data[data]
                 .description for data in data_container.data}

    return [desc_aliases, desc_equations, desc_parameters, desc_sets,
            desc_variables], data_dict

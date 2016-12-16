"""Functions to assist in making matplotlib and bokeh plots."""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def datetime_to_hour(date_time):
    """Convert a datetime object to the fractional hour of the day as a float (03:15pm --> 15.25)"""
    return date_time.hour + date_time.minute / 60. + date_time.second / 3600. \
           + date_time.microsecond / (3600. * 1e6)




def filter_days(df_or_series, days_of_week=None, months=None):
    """Return a slice of **df_or_series** that only includes the desired days and months.

    Args:
        df_or_series (DataFrame or Series): Object that you want to filter out certain days and months. The index must be of type *DatetimeIndex*.
        days_of_week (int, list, or string): If *int* or *list* of ints, return only days of the week that match the *int(s)*, starting with Sunday as 0, and Saturday as 6. If *string*, there are two options: 'weekday' corresponds to Monday -> Friday. 'weekend' corresponds to Saturday and Sunday.

    Returns:
        slice (DataFrame or Series):
    """

    df_temp = pd.DataFrame(index=df_or_series.index)
    if months:
        if type(months) == int:
            months = [months]
        df_temp['month'] = df_temp.index.month
        df_temp = df_temp[df_temp['month'].isin(months)]
    if days_of_week:
        # TODO: add 'holidays' option
        if type(days_of_week) == int:
            days_of_week = [days_of_week]
        elif days_of_week in ['weekday', 'wkday']:
            days_of_week = [0, 1, 2, 3, 4]
        elif days_of_week in ['weekend', 'wkend']:
            days_of_week = [5, 6]
        df_temp['dayofweek'] = df_temp.index.dayofweek
        df_temp = df_temp[df_temp['dayofweek'].isin(days_of_week)]

    return df_or_series.loc[df_temp.index]


def intervals_per_day(df_or_series):
    """Returns how many rows per day there are in **df_or_series**"""
    res = df_or_series.index[1] - df_or_series.index[0]
    return int((3600 * 24) / res.seconds)


def dataframe_plotter(df, title='', xlabel='', ylabel='', height_per_plot=3,
                      width=12.4, subplots=False, secondary_y=False,
                      secondary_ylabel='', dots=True, plot_type='line',
                      x_label_rotation=0, linewidth=1):
    """Helper function to plot data from a pandas DataFrame or Series

    Args:
        df (DataFrame or Series): Data to plot. Must have a datetimeindex.
        title (str or list): If *str*, print above the plot. If *list* and
            **subplots** != False, prints each string in the *list* above the
            corresponding subplot.
        xlabel (str): Prints below the plot.
        ylabel (str or list): If *str*, print on yaxis of the plot. If *list*
            and **subplots** != False, prints each string in the *list* on the
            corresponding yaxis.
        height_per_plot (float):  Height per plot.
        width (float): Total width of plot in inches
        subplots (bool or list of lists): If True, print each column in **df** on a
            separate plot. If *list of lists*, each sublist should contain the
            column names from df that you want on each subsequent plot.
        secondary_y (str, list, or list of lists): If **subplots** == False, **secondary_y** must be a *str* or *list
            of strings*, where each string is a column in df that you want on
            the right axis. If **subplots** is a *list of lists*, **secondary_y** must
            be a *list of lists*, where each internal list contains the
            strings of the column names that will be placed on each plot's
            right axis.
        secondary_ylabel (str or list): Labels to place on the right axis.
        dots (bool): If True, include dots on the lines at each data point.
        plot_type (str): Either 'line', 'average', 'overlay', or 'bar'. If
            'line', make a line plot. If 'average', plot the average value at
            each time of the day on a 0 to 24 hour x-axis. If 'overlay', plot
            each day on top of a single plot that has a 0 to 24 hour x-axis. If
            'bar', make a bar plot. 'average' and 'overlay' require that the index of the DataFrame is a datetimeindex.
        x_label_rotation (int): angle the xlabels will be printed at. 0 --> horizontal,  90 --> verticle.
        linewidth (int): width of the line for line plots.

    Examples:
        >>> import pandas as pd
        >>> # Create some fake data
        >>> data = pd.DataFrame({'col1': list(range(10))})
        >>> data['col2'] = data['col1'] ** 2 / 10
        >>> data['col3'] = data['col1'] ** 3 / 700
        >>> data['col4'] = data['col1'] ** 4 / 1000
        >>> data.index = pd.date_range('2/15/1990', \
periods=len(data), freq='H')

        One plot. 'col3' on right yaxis.

        >>> dataframe_plotter(data, title='One plot example', \
xlabel='Datetime', ylabel='Fake data', secondary_y='col3', \
secondary_ylabel='col3')

        One subplot for each column.

        >>> dataframe_plotter(data, ylabel=['col1', 'col2', 'col3', 'col4'], \
subplots=True)

        Two subplots. The first plot has 'col1' and 'col2' on the left side.
        The second plot has 'col3' on the left and 'col4' on the right.

        >>> dataframe_plotter(data, ylabel=['col1 and col2', 'col3'], \
subplots=[['col1', 'col2'], ['col3']],secondary_y=[[], ['col4']], \
secondary_ylabel=['', 'col4'])

        Two barplots.

        >>> dataframe_plotter(data, title=['Kittens', 'Puppies'], \
subplots=[['col1', 'col3'], ['col2', 'col4']])

    """

    if type(df) is pd.Series:
        df = pd.DataFrame(df)

    if subplots == True:
        subplots = [[col] for col in df.columns]
    elif subplots == False:
        subplots = [list(df.columns)]

    if type(secondary_y) is str:
        secondary_y = [[secondary_y]]

    if secondary_y == False:
        secondary_y = [[]]

    if dots:
        marker = '.'
    else:
        marker = ''

    nb_plots = len(subplots)

    def _str_to_sparse_list(string_or_list, length, list_of_lists=False):
        sparse_list = [''] * length
        if type(string_or_list) is str:
            string_or_list = [string_or_list]
        for i in range(len(string_or_list)):
            if list_of_lists:
                sparse_list[i] = [string_or_list[i]]
            else:
                sparse_list[i] = string_or_list[i]
        return sparse_list

    title = _str_to_sparse_list(title, nb_plots)
    ylabel = _str_to_sparse_list(ylabel, nb_plots)
    secondary_ylabel = _str_to_sparse_list(secondary_ylabel, nb_plots)

    height = height_per_plot * nb_plots
    f, ax = plt.subplots(nb_plots, sharex=True, figsize=(width, height))
    if nb_plots == 1:
        ax = [ax]
        if type(secondary_y[0]) is str:
            secondary_y = [secondary_y]
        for col2 in secondary_y[0]:
            subplots[0].remove(col2)
    else:
        secondary_y = _str_to_sparse_list(secondary_y, nb_plots)

    if plot_type == 'bar':
        df['x_axis'] = np.arange(len(df))

    ax2 = [''] * nb_plots
    for i in range(nb_plots):
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'black', 'lime', 'orange',
                  'fuchsia', 'orangered', 'steelblue', 'darkgoldenrod']
        if plot_type == 'bar':
            ax[i].set_xticks((df['x_axis'] + 0.45).values)
            ax[i].set_xticklabels(list(df.index))
            width = 0.9 / len(subplots[i])
            ax[i].grid(b=True, which='both', axis='y')
        else:
            ax[i].grid(b=True, which='both')

        if type(subplots[i]) == str:
            subplots[i] = [subplots[i]]
        for col, f in zip(subplots[i], range(len(subplots[i]))):
            if plot_type == 'overlay':
                overlay_days_plotter(df[col], ax[i], col, colors.pop(0))
            elif plot_type == 'average':
                average_day_plotter(df[col], ax[i], col, colors.pop(0),
                                    marker=marker)
            elif plot_type == 'bar':
                ax[i].bar(df.x_axis + f * width, df[col], width=width,
                          label=col, color=colors.pop(0))
            else:
                ax[i].plot(df.index, df[col], label=col, marker=marker,
                           linewidth=linewidth)

        if len(secondary_y[i]) > 0:
            ax2[i] = ax[i].twinx()
            # http: // matplotlib.org / mpl_examples / color / named_colors.pdf
            colors = ['lime', 'orange', 'fuchsia', 'orangered', 'steelblue',
                      'darkgoldenrod']
            ax2[i].set_prop_cycle(color=colors)
            if type(secondary_y[i]) == str:
                secondary_y[i] = [secondary_y[i]]
            for col2 in secondary_y[i]:
                if plot_type == 'overlay':
                    overlay_days_plotter(df[col2], ax2[i], col2, colors.pop(0))
                elif plot_type == 'average':
                    average_day_plotter(df[col2], ax2[i], col2,
                                        colors.pop(0), marker=marker)
                elif plot_type == 'bar':
                    raise (
                        "secondary y is not supported when plot_type=='bar'")
                else:
                    ax2[i].plot(df.index, df[col2], label=col2, marker=marker,
                                linewidth=linewidth)

            handles, labels = ax2[i].get_legend_handles_labels()
            ax2[i].legend(handles, labels)
            ax2[i].set_ylabel(secondary_ylabel[i], fontsize=13)
            ax2[i].grid(None)

        ax[i].set_title(title[i], fontsize=18)
        ax[i].set_ylabel(ylabel[i], fontsize=13)
        handles, labels = ax[i].get_legend_handles_labels()
        ax[i].legend(handles, labels, loc='upper left')

    xlabels = ax[-1].get_xticklabels()
    plt.setp(xlabels, rotation=x_label_rotation)
    ax[-1].set_xlabel(xlabel, fontsize=15)


def overlay_days_plotter(series, plot=plt, label=None, color='blue'):
    dates = [str(d) for d in np.unique(series.index.date)]
    for date in dates:
        plot.plot(datetime_to_hour(series.loc[date].index),
                  series.loc[date].values, color=color, linewidth=0.2)
    plot.set_xticks(np.arange(0, 24, 1))

    if label:
        plot.plot(0, 0, color=color, label=label, linewidth=1)
    plot.set_xlim([0, 24])


def average_day_plotter(series, plot=plt, label=None, color='blue',
                        marker='.'):
    df = series.to_frame()
    df['hour'] = datetime_to_hour(series.index)
    gp = df.groupby('hour').mean()
    plot.plot(gp.index, gp.values, color=color, label=label, marker=marker)
    plot.set_xticks(np.arange(0, 24, 1))
    plot.set_xlim([0, 24])


def filter_days_plotter(series, days_of_week=None, months=None,
                        plot_type='overlay', width=12.4, height=5):
    # TODO: handle lists of days_of_week and months
    f, ax = plt.subplots(1, sharex=True, figsize=(width, height))
    ax = [ax]
    title = ''
    if months:
        title = 'Months: {}.'.format(months)
    if days_of_week:
        title = '{} Days of week: {}'.format(title, days_of_week)

    s = filter_days(series, days_of_week, months)
    i = 0
    if plot_type == 'overlay':
        overlay_days_plotter(s, ax[i])
    elif plot_type == 'average':
        average_day_plotter(s, ax[i])

    ax[i].set_xlabel("Hour", fontsize=15)
    ax[i].set_ylabel(s.name, fontsize=13)
    ax[i].set_title(title, fontsize=18)
    ax[i].grid(b=True, which='both')



if __name__ == "__main__":
    # x = np.array([0, 1, 2, 3])
    # y = np.array([20, 21, 22, 23])
    # plt.bar(x, y)
    # plt.show()
    index = pd.date_range('2016-01-01', '2017-01-01', freq='H')
    df = pd.DataFrame(np.arange(len(index)), index=index,
                      columns=['linear'])



    x = np.arange(len(df))
    df['sin_year'] = np.sin(1 * 2 * np.pi * x / len(df))
    df['sin_month'] = np.sin(12 * 2 * np.pi * x / len(df))
    df['sin_day'] = np.sin(365 * 2 * np.pi * x / len(df))
    df['cos_year'] = np.cos(1 * 2 * np.pi * x / len(df))
    df['cos_month'] = np.cos(12 * 2 * np.pi * x / len(df))
    df['cos_day'] = np.cos(365 * 2 * np.pi * x / len(df))
    df['10sin_month'] = 10 * df['sin_month'] + df['sin_day']
    df['10cos_month'] = 10 * df['cos_month'] + df['cos_day']

    dataframe_plotter(df, title='Single Plot', ylabel='All columns', xlabel='Datetime')
    dataframe_plotter(df, subplots=True, title=['First plot', 'Seconds plot'], xlabel='Datetime')

    sub = ['sin_year']
    title = ['test']
    dataframe_plotter(df, subplots=True, plot_type='bar', height_per_plot=3, title=title)

    dataframe_plotter(df, subplots=sub[:2], plot_type='bar', height_per_plot=3)
    dataframe_plotter(df, subplots=sub[:1], plot_type='bar', height_per_plot=3)
    cons_sites = [10017472, 10017490]
    # dfs = load_csv_consumption_sites(cons_sites, squeeze=True)
    # days_of_week = [1, 3]
    days_of_week = 'wkday'
    days_of_week = 1
    # days_of_week = None
    months = [2]
    # months=None
    # overlay_days_plotter2(dfs[cons_sites[1]], days_of_week=days_of_week,
    #                      months=months, line_plot=False)
    data = one_year_scaled_with_prod_shifted(232142, 10084450, dt.timedelta(
        minutes=30), dt.datetime(2013, 1, 1))
    data = data.head(300)
    filter_days_plotter(data['consumption'], days_of_week=[3, 4], months=1)
    # overlay_days_plotter(data['consumption'])
    average_day_plotter(data['consumption'])
    data['c2'] = data['consumption'] * 2
    data['p2'] = data['production'] * 2
    dataframe_plotter(data, overlay_days=True, secondary_y='c2')
    data = pd.read_pickle('../data/test/df_cons_fake_prod').head(1000)
    data['net_i'] = data['cons'] - data['prod']
    data['net'] = data['net_i'] / 100
    data['net2'] = data['net'] * 2
    dataframe_plotter(data['net'], title='Plot series', dots=False)
    #
    plt.figure(0)
    dataframe_plotter(data, title='test', xlabel='Datetime', ylabel='wH',
                      secondary_y=['prod', 'net'], subplots=False, width=12,
                      height_per_plot=8)
    plt.figure(1)
    dataframe_plotter(data, title=['test', '', 'hi'], xlabel='Datetime',
                      ylabel=['wH', 'test'],
                      secondary_y=['prod', 'net'], subplots=True, width=12,
                      height_per_plot=8)
    #
    bokeh_plotter(data['net'], title='Plot_series', show_plot=True,
                  output_file_name='t.html')
    p = bokeh_plotter(data, show_plot=False,
                      output_file_name='t.html')
    p2 = bokeh_plotter(data, show_plot=False,
                       output_file_name='t2.html')
    g = gridplot([[p], [p2]])
    show(g)
    bokeh_plotter(data, output_file_name='plot2.html',
                  secondary_y=['net_i', 'cons'], title='test',
                  ylabel='wH, prod and net', xlabel='Datetime',
                  secondary_ylabel='wH, net_i and cons', width=1300,
                  )
    import pandas as pd
    from enphase.plotting_tools import dataframe_plotter

    # Create some fake data
    data = pd.DataFrame({'col1': list(range(10))})
    data['col2'] = data['col1'] ** 2
    data['col3'] = data['col1'] ** 3
    data.index = pd.date_range('2/15/1990', periods=len(data), freq='H')

    dataframe_plotter(data, title='One plot example',
                      xlabel='Datetime', ylabel='Fake data',
                      secondary_y='col3')

    dataframe_plotter(data, ylabel=['col1', 'col2', 'col3'],
                      secondary_y=['col1', 'col3'], subplots=True)
    print("END")

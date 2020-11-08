# ------------------------------------Import Libraries-----------------------------------------

def global_import(modulename, shortname=None):

  modulename = modulename.strip()

  if shortname is None:
    shortname = modulename.split('.')[-1]

  if '.' in modulename:
    if modulename.count('.') > 1:
      print('Too complicated, cannot handle now.')
      return 1

    top_level_module = modulename.split('.')[0]

    globals()[top_level_module] = __import__(top_level_module)
    globals()[shortname] = eval(modulename)
    return 0

  else:
    globals()[shortname] = __import__(modulename)
    return 0


def import_libraries():
  global_import('warnings')
  warnings.simplefilter(action='ignore', category=FutureWarning)
  global_import('pandas', 'pd')
  global_import('numpy', 'np')
  global_import('seaborn', 'sns')
  global_import('matplotlib.pyplot', 'plt')

  global_import('re')
  pd.set_option('display.max_columns', 100)
  pd.set_option('display.max_rows', 100)
  global default_dpi
  default_dpi = 90
  print('Importing Done')


# -------------------------------------Data Selection----------------------------------------------


def load_data(which_year):
  '''Provide the census year you will to load (choose from 1850, 1880, 1910)'''
  try:
    df = pd.read_csv('/content/drive/My Drive/census_' + str(which_year) + '.csv', low_memory=False)
    return df
  except FileNotFoundError as e:
    print('File Not Found! Please check if you have created Shortcuts for the data files\nin your "My Drive" folder and if you have run the first cell in this notebook.\nLink to the data folder: https://drive.google.com/drive/folders/19dZe5h63fdCYNnW421woQv4Z09QABjam')
  except NameError as e:
    print('Function not defined yet! Please check if you have run the first cell in this notebook.')


def build_criteria_from_string(string, data):

  if ' is not ' in string or ' != ' in string:
    string = string.replace(' is not ', ' != ')
    col = string.split('!=')[0].strip()
    value = string.split('!=')[1].strip()
    value = float(value) if value.isnumeric() else value
    return build_criteria(col, value, data, equal_or_not=False)
  elif ' is ' in string or ' = ' in string:
    string = string.replace(' is ', ' = ')
    col = string.split('=')[0].strip()
    value = string.split('=')[1].strip()
    value = float(value) if value.isnumeric() else value
    return build_criteria(col, value, data, equal_or_not=True)


def build_criteria(col, value, data, equal_or_not=True):
  if equal_or_not:
    return data[col] == value
  else:
    return data[col] != value


def get_multiple_criteria(string, data):
  multiple_criteria = [c.strip() for c in string.split(',')]
  multiple_criteria = [c + ' = 1' if (' = ' not in c) and (' is ' not in c) and (c in data.columns) else c for c in multiple_criteria]
  multiple_criteria_filters = [build_criteria_from_string(c, data) for c in multiple_criteria]
  combined_filter = pd.Series([True] * len(data))
  for filter in multiple_criteria_filters:
    combined_filter = combined_filter & filter
  return combined_filter


def select_data(criteria_string, data):
  '''Provide a comma separated criteria_string, and specify which dataframe (df) to select from'''
  criteria_filter = get_multiple_criteria(criteria_string, data)
  return data[criteria_filter].copy()

# -------------------------------------Smart Data Description-------------------------------------------

def describe(col, data, top_k=-1, thres=90, return_full=False, plot_top_k=-1, plot_type='', bins=-1):

  if data[col].isnull().mean() > 0:
    print(f"Notice: {np.round(data[col].isnull().mean()*100,3)}% of the entries have no records for this field.\n")

  data_numeric_columns = data.dtypes[data.dtypes.apply(lambda x: np.issubdtype(x, np.number))].index.tolist()

  if col in data_numeric_columns:
    if bins == -1:
      print(f'Change the default width of histogram bars by setting "bins = <a number>".\n')
      bins = 50
    plt.figure(figsize=(9, 6), dpi=default_dpi)
    plt.hist(data[col].dropna(), bins=bins)
    plt.title(f"Distribution of the {col}")
    return

  ser = data[col].value_counts()
  ser.name = 'Absolute Number'

  percentage_ser = np.round(ser / len(data) * 100, 2)
  percentage_ser.name = 'Proportion in Data (%)'

  cumsum_percentage_ser = percentage_ser.cumsum()
  cumsum_percentage_ser.name = 'Cumulative Proportion (%)'

  full_value_counts_df = pd.concat([ser, percentage_ser, cumsum_percentage_ser], axis=1)

  if plot_top_k > top_k:
    top_k = plot_top_k

  if top_k == -1:
    top_k = sum(cumsum_percentage_ser <= thres) + 1
    top_k = max(5, top_k)
    top_k = min(20, top_k)

  value_counts_df = full_value_counts_df if return_full else full_value_counts_df[:top_k]

  if top_k < len(full_value_counts_df) and not return_full:
    print(f'{len(full_value_counts_df)-top_k} more rows are available, add "return_full = True" if you want to see all.\n')

  plot_top_k = 10 if plot_top_k == -1 else plot_top_k
  graph_df = value_counts_df['Proportion in Data (%)'][:plot_top_k].copy()

  if plot_type == '':
    plot_type = 'bar' if graph_df.sum() < thres else 'pie'

  if plot_type == 'pie':

    fig, ax = plt.subplots(figsize=(9, 6), dpi=default_dpi, subplot_kw=dict(aspect="equal"))

    values = graph_df.values.tolist()
    names = graph_df.index.tolist()

    def func(pct, allvals):
      absolute = int(pct / 100. * np.sum(allvals))
      return "{:.1f}%".format(pct, absolute)

    wedges, texts, autotexts = ax.pie(values, autopct=lambda pct: func(pct, values), textprops=dict(color="w"))

    for w in wedges:
      w.set_edgecolor('white')

    ax.legend(wedges, names,
              title="Categories",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.8, 1))

    plt.setp(autotexts, size=12, weight="bold")

    ax.set_title(f"Relative Proportion of Top {len(graph_df)} {col}" if len(graph_df) < len(full_value_counts_df) else f"Proportion of {col}")

  if plot_type == 'bar':
    plt.figure(figsize=(9, 6), dpi=default_dpi)
    graph_df.plot(kind='bar')
    plt.title(f"Barplot of the Top {len(graph_df)} {col} - (y axis shows percentage)")

  print()

  return value_counts_df

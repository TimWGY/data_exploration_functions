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
  print('Importing Done')

# -------------------------------------Data Selection----------------------------------------------


def build_criteria_from_string(string, data):
  string = string.replace(' is ', ' = ')
  col = string.split('=')[0].strip()
  value = string.split('=')[1].strip()
  value = int(value) if value.isnumeric() else value
  return build_criteria(col, value, data)


def build_criteria(col, value, data):
  return data[col] == value


def get_multiple_criteria(string, data):
  multiple_criteria = [c.strip() for c in string.split(',')]
  multiple_criteria = [c + ' = 1' if (' = ' not in c) and (' is ' not in c) and (c in data.columns) else c for c in multiple_criteria]
  multiple_criteria_filters = [build_criteria_from_string(c, data) for c in multiple_criteria]
  combined_filter = pd.Series([True] * len(data))
  for filter in multiple_criteria_filters:
    combined_filter = combined_filter & filter
  return combined_filter


def select_data(criteria_string, data):
  criteria_filter = get_multiple_criteria(criteria_string, data)
  return data[criteria_filter].copy()

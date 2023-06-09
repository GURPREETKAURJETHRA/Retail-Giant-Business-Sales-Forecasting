import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import OneHotEncoder
import pickle
import math
from sklearn.model_selection import RandomizedSearchCV

# defining a function to load and clean store dataset
def store_data():
  # creating dataframes and store csv data
  path = './data/store.csv'
  df = pd.read_csv(path, index_col=0)

  # filling the missing values with median
  df["CompetitionDistance"].fillna(value = df.CompetitionDistance.median(), inplace=True)

  # filling the missing values with mode
  df["CompetitionOpenSinceMonth"].fillna(value = df.CompetitionOpenSinceMonth.mode()[0], inplace=True)
  df["CompetitionOpenSinceYear"].fillna(value = df.CompetitionOpenSinceYear.mode()[0], inplace=True)

  # filling the missing values with value 0
  df["Promo2SinceWeek"].fillna(value = 0, inplace=True)
  df["Promo2SinceYear"].fillna(value = 0, inplace=True)
  df["PromoInterval"].fillna(value = 0, inplace=True)

  # convert CompetitionOpenSinceMonth, CompetitionOpenSinceYear, Promo2SinceWeek, Promo2SinceYear
  # from float to int
  df = df.astype({"CompetitionOpenSinceMonth":int, "CompetitionOpenSinceYear":int, "Promo2SinceWeek":int, "Promo2SinceYear":int})

  return df

# defining a function to load and clean sales dataset
def sales_data():
  # creating dataframes and store csv data
  path = './data/Rossmann Stores Data.csv'
  df = pd.read_csv(path, index_col=0, low_memory=False)

  # date should be converted from object to datetime
  df['Date'] = pd.to_datetime(df['Date'])
  # convert StateHoliday values to int
  df["StateHoliday"].replace({'0':0, 'a':1, 'b':1, 'c':1}, inplace=True)

  # split the date column into month and year
  df['WeekOfYear'] = df['Date'].dt.isocalendar().week
  df['Month'] = df['Date'].dt.month
  df['Year'] = df['Date'].dt.year

  return df

# defining a function to load dates of Easter
def easter_data():
  # creating dataframes and easter dates csv data
  path = './data/Easter_dates_data.csv'
  df = pd.read_csv(path, index_col=0)
  return df

# defining a function check whether a date is state holiday or not
def isStateHoliday(sales_date: pd.Timestamp, easter_df: pd.DataFrame):
  easter_df = easter_data()
  easter_date = datetime.strptime(str(sales_date.year) + '/' + 
                str(easter_df[easter_df['Year'] == sales_date.year]['Month'].values[0]) + '/' + 
                str(easter_df[easter_df['Year'] == sales_date.year]['Day'].values[0]), "%Y/%m/%d")

  if (sales_date.month == 1 and sales_date.day in [1, 6] or
      sales_date.month == 5 and sales_date.day == 1 or
      sales_date.month == 8 and sales_date.day == 15 or
      sales_date.month == 10 and sales_date.day in [3, 31] or
      sales_date.month == 11 and sales_date.day == 1 or
      sales_date.month == 12 and sales_date.day in [25, 26]):
    return 1

  if (sales_date == easter_date - timedelta(days=3) or sales_date == easter_date + timedelta(days=1) or
      sales_date == easter_date + timedelta(days=38) or sales_date == easter_date + timedelta(days=49) or
      sales_date == easter_date + timedelta(days=59)):
    return 1

  if int(sales_date.strftime('%V')) == 47 and sales_date.weekday() + 1 == 3:
    return 1

  return 0

# defining a function check whether a date is school holiday or not
def isSchoolHoliday(weekOfYear: int, dayOfWeek: int, sales_df: pd.DataFrame):
  avg = sales_df.groupby(['WeekOfYear', 'DayOfWeek'])['SchoolHoliday'].mean()

  all = [1, 31, 32, 38, 39]
  no = [3, 4, 9, 12, 17, 19, 24, 25, 26, 38, 39, 40, 46, 47, 48, 49, 50, 51]
  thurs_fri = [5]

  if weekOfYear in all:
    return avg[weekOfYear][dayOfWeek]
  elif weekOfYear in no:
    return 0
  elif weekOfYear in thurs_fri:
    if dayOfWeek in [4, 5]:
      return avg[weekOfYear][dayOfWeek]
  else:
    if dayOfWeek <= 5:
      return avg[weekOfYear][dayOfWeek]
  
  return 0

# defining a function check whether a store is open or not
def isOpen(isStateHoliday: int, isSchoolHoliday: float, sales_df: pd.DataFrame):
  isSchoolHoliday = isSchoolHoliday >= 0.5
  open_df = sales_df.loc[:, ['StateHoliday', 'SchoolHoliday', 'Open']].sort_values('Open', ascending=False).reset_index().groupby(['StateHoliday', 'SchoolHoliday', 'Open']).count().reset_index()
  opened = open_df[(open_df['StateHoliday'] == isStateHoliday) & (open_df['SchoolHoliday'] == isSchoolHoliday) & (open_df['Open'] == 1)]['Store'].values[0]
  closed = open_df[(open_df['StateHoliday'] == isStateHoliday) & (open_df['SchoolHoliday'] == isSchoolHoliday) & (open_df['Open'] == 0)]['Store'].values[0]
  open_ratio = opened / (opened + closed)
  return 1

# defining a function to create new features in parameter dataframe
def create_new_features(parameter_df: pd.DataFrame):
  # create a new feature which shows the number of months passed since competition started
  parameter_df['CompetitionOpenNumMonths'] = (parameter_df['Year'] - parameter_df['CompetitionOpenSinceYear']) * 12 + (parameter_df['Month'] - parameter_df['CompetitionOpenSinceMonth'])

  # create a new feature which shows the number of weeks passed since promo 2 started
  parameter_df['Promo2NumWeeks'] = (parameter_df['Year'] - parameter_df['Promo2SinceYear']) * 52 + (parameter_df['WeekOfYear'] - parameter_df['Promo2SinceWeek'])

  # change negative values of CompetitionOpenNumMonths to 0
  parameter_df['CompetitionOpenNumMonths'] = parameter_df['CompetitionOpenNumMonths'].apply(lambda x: 0 if x < 0 else x)

  # change the value of Promo2NumWeeks to 0 where Promo2 is 0
  parameter_df.loc[parameter_df['Promo2'] == 0, 'Promo2NumWeeks'] = 0

  # change negative values of Promo2NumWeeks to 0
  parameter_df['Promo2NumWeeks'] = parameter_df['Promo2NumWeeks'].apply(lambda x: 0 if x < 0 else x)

  return parameter_df

# defining a function to binary encode day of week
def binary_encode_dayOfWeek(parameter_df: pd.DataFrame):
  parameter_df['DayOfWeek_0'] = parameter_df['DayOfWeek'].apply(lambda x : 1 if x in [1, 2, 6, 7] else 0)
  parameter_df['DayOfWeek_1'] = parameter_df['DayOfWeek'].apply(lambda x : 1 if x in [3, 4, 6, 7] else 0)
  parameter_df['DayOfWeek_2'] = parameter_df['DayOfWeek'].apply(lambda x : 1 if x in [1, 3, 5, 6] else 0)

  parameter_df.drop('DayOfWeek', axis=1, inplace=True)

  return parameter_df

# defining a function to binary encode day of week
def binary_encode_weekOfYear(parameter_df: pd.DataFrame):
  parameter_df['WeekOfYear_0'] = parameter_df['WeekOfYear'].apply(lambda x : 1 if x >= 32 else 0)
  parameter_df['WeekOfYear_1'] = parameter_df['WeekOfYear'].apply(lambda x : 1 if x <= 16 or x in range(32, 37) else 0)
  parameter_df['WeekOfYear_2'] = parameter_df['WeekOfYear'].apply(lambda x : 1 if x <= 8 or x in range(17, 25) or x in range(37, 45) else 0)
  parameter_df['WeekOfYear_3'] = parameter_df['WeekOfYear'].apply(lambda x : 1 if math.ceil(x / 4) % 2 != 0 else 0)
  parameter_df['WeekOfYear_4'] = parameter_df['WeekOfYear'].apply(lambda x : 1 if math.ceil(x / 2) % 2 != 0 else 0)
  parameter_df['WeekOfYear_5'] = parameter_df['WeekOfYear'].apply(lambda x : 1 if x % 2 != 0 else 0)

  parameter_df.drop('WeekOfYear', axis=1, inplace=True)

  return parameter_df

# defining a function to perform feature engineering on parameter_dataframe
def feature_engineering(parameter_df: pd.DataFrame):
  # dropping unnecessary features
  parameter_df.drop(['CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear',	
                     'Promo2',	'Promo2SinceWeek',	'Promo2SinceYear', 'Year',	
                     'Month'], axis=1, inplace=True)

  # convert DayOfWeek, Open, StateHoliday, SchoolHoliday and WeekOfYear to int
  parameter_df = parameter_df.astype({"DayOfWeek":int, "Open":int, "StateHoliday":int, "SchoolHoliday":int, "WeekOfYear":int})

  # square root transformation of competition open number of months and 
  # promo 2 number of weeks to transform them to normal distribution
  parameter_df['CompetitionOpenNumMonths'] = np.sqrt(parameter_df['CompetitionOpenNumMonths'])
  parameter_df['Promo2NumWeeks'] = np.sqrt(parameter_df['Promo2NumWeeks'])

  # log transformation of competition distance to transform it to normal distribution
  parameter_df['CompetitionDistance'] = np.log(parameter_df['CompetitionDistance'])

  # binary encoding day of week and week of year
  parameter_df = binary_encode_dayOfWeek(parameter_df)
  parameter_df = binary_encode_weekOfYear(parameter_df)

  # one hot encoding store type and assortment
  ohe = OneHotEncoder(sparse_output=False, dtype=int)
  ohe.fit(parameter_df[['StoreType', 'Assortment']])
  encoded_features = list(ohe.get_feature_names_out(['StoreType', 'Assortment']))
  parameter_df[encoded_features] = ohe.transform(parameter_df[['StoreType', 'Assortment']])
  parameter_df.drop(['StoreType', 'Assortment'], axis=1, inplace=True)

  # dummying promo interval
  parameter_df = pd.get_dummies(parameter_df, columns=['PromoInterval'])

  # dropping PromoInterval_Jan,Apr,Jul,Oct, StoreType_c & Assortment_b to avoid dummy variable trap
  parameter_df.drop(['PromoInterval_Jan,Apr,Jul,Oct', 'StoreType_c', 'Assortment_b'], axis=1, inplace=True)

  return parameter_df

# defining a function to get the sales of the mentioned store for the given date
def get_sales(store: int, sales_date: pd.Timestamp, store_df: pd.DataFrame, sales_df: pd.DataFrame, easter_df: pd.DataFrame, model: RandomizedSearchCV):
  # extacting day of week, year, month and week of year from the given date
  dayOfWeek = sales_date.weekday() + 1
  year = sales_date.year
  month = sales_date.month
  weekOfYear = int(sales_date.strftime('%V'))

  stateHoliday = isStateHoliday(sales_date, easter_df)
  schoolHoliday = isSchoolHoliday(weekOfYear, dayOfWeek, sales_df)
  open = isOpen(stateHoliday, schoolHoliday, sales_df)

  # defining the dataframe for storing parameters of each store and 
  # adding initial parameters extracted from sales date
  # along with competition distance
  parameter_df = pd.DataFrame(columns=['DayOfWeek', 'Open', 'StateHoliday', 'SchoolHoliday'])
  for i in range(store_df.shape[0]):
    parameter_df.loc[parameter_df.shape[0]] = [dayOfWeek, open, stateHoliday, schoolHoliday]
  parameter_df = pd.concat([parameter_df.reset_index().drop('index', axis=1), store_df.reset_index().drop('Store', axis=1)], axis=1)
  
  # adding date details extracted from sales date
  date_details_df = pd.DataFrame(columns=['Year', 'Month', 'WeekOfYear'])
  for i in range(store_df.shape[0]):
    date_details_df.loc[date_details_df.shape[0]] = [year, month, weekOfYear]
  parameter_df = pd.concat([parameter_df.reset_index().drop('index', axis=1), date_details_df.reset_index().drop('index', axis=1)], axis=1)
  
  # creating new features from extacted year, month and week number
  parameter_df = create_new_features(parameter_df)

  # perform feature engineering on parameter dataframe
  parameter_df = feature_engineering(parameter_df)

  # predict sales
  sales = model.predict(parameter_df)

  # sales was square root transformed 
  # during feature engineering for model training
  # it needs to be squared to get correct values
  sales = np.square(sales)

  # return total sales from all the stores
  return sales[store - 1]

# defining a function to get the total sales of the mentioned store for the given range of dates
def get_total_sales(store: int, sales_date_string_from: str, sales_date_string_to: str, store_df: pd.DataFrame, sales_df: pd.DataFrame, easter_df: pd.DataFrame, ml_model: RandomizedSearchCV):
  sales_dates = pd.date_range(sales_date_string_from, sales_date_string_to).tolist()

  predicted_sales = {}
  for dt in sales_dates:
    predicted_sales[dt] = get_sales(store, dt, store_df, sales_df, easter_df, ml_model)

  return predicted_sales

# def main():
#   store = store_data()
#   sales = sales_data()
#   easter = easter_data()
#   ml_model = pickle.load(open('./models/ml_model.pkl', 'rb'))

#   print(get_total_sales(1, '2023-01-26', '2023-01-28', store, sales, easter, ml_model))

# if __name__ == "__main__":
#   main()
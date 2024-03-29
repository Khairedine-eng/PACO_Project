from Paco_Project.Code_Fix.csv_to_sql_server import create_database_connection
from Paco_Project.Code_Fix.csv_to_sql_server import fetch_table_data
from Paco_Project.Code_Fix.Data_Preparation import split_data
from Paco_Project.Code_Fix.Data_Processing import retrieve_data
from Paco_Project.Test.Sarimax.ARIMAX import *
import pandas as pd

import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error

def main():
    # Database connection details
    server_name = 'DESKTOP-9PEK18E'
    database_name = 'Paco_data'
    schema_name = 'DATA'
    table_name = 'BMW'

    # Create the database connection
    engine = create_database_connection(server_name, database_name, schema_name)

    # Fetch all data from the "BMW" table
    df = fetch_table_data(engine, table_name)

    if df is not None:
        #print(df)
        #print(df.info())
        #print(df.describe())

        raw_df = retrieve_data(df)

        if raw_df is not None:
            # Specify years to filter
            years_to_filter = [2022, 2023]  # Add more years as needed

            # Filter data for specified years
            filtered_df = raw_df[raw_df['Year'].isin(years_to_filter)]

            # Drop unnecessary columns
            columns_to_drop = ['Sales Bud', 'Sales Act ', ' Sales Actual/Budget', 'NH Actual/Budget', 'Efficiency Bud ',
                                   'Efficiency Act', 'Efficiency Actual/Budget']
            filtered_df.drop(columns=columns_to_drop, inplace=True)

            # Further processing or analysis can be done here

            #print(filtered_df.head())
            #print(filtered_df.dtypes)
            filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], format='%d/%m/%Y')

            # Convert numeric columns to float and replace commas with periods
            numeric_cols = ['NH Budget', 'NH Actual','Production Calendar', 'Customer Calendar', 'ADC Calendar',
                            'Customer Consumption Last 12 week', 'Stock Plant : TIC Tool', 'CLIENT FORCAST S1',
                            'HC DIRECT', 'HC INDIRECT', 'ABS P', 'ABS NP', 'FLUCTUATION']

            filtered_df[numeric_cols] = filtered_df[numeric_cols].replace(',', '.', regex=True).astype(float)

            # Separate target variable (y)
            y = filtered_df['NH Actual'].replace(',', '.', regex=True).astype(float)

            # Select exogenous variables (X)
            X = filtered_df.drop(columns=['NH Actual', 'Date'])

            # Fill missing values with 0
            X.fillna(0, inplace=True)


            # Example: Print X and y
            #print("Exogenous Variables (X):")
            #print(X)
            #print("\nTarget Variable (y):")
            #print(y)
            #print(X.dtypes)
            #print(y.dtypes)

            # Convert X and y to Pandas DataFrames
            X = pd.DataFrame(X)
            y = pd.DataFrame(y)

            # Verify the data types of X and y
            print("Data types of X and y after conversion:")
            print(X.dtypes)
            print(y.dtypes)
            print(X.describe())
            print(y.describe())


            X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

            # Example: Print the shapes of train and test sets
            print("Train set shapes:")
            print("X_train:", X_train.shape)
            print("y_train:", y_train.shape)
            print("\nTest set shapes:")
            print("X_test:", X_test.shape)
            print("y_test:", y_test.shape)

            model = fit_sarimax(X_train, y_train, order=(1, 0, 1), seasonal_order=(0, 0, 0, 0))

            # Generate predictions on test data
            y_pred = model.predict(X_test)

            # Plot actual vs predicted
            plt.figure(figsize=(10, 6))
            plt.plot(y_test.index, y_test, label='Actual', color='blue')
            plt.plot(y_test.index, y_pred, label='Predicted', color='red')
            plt.title('Actual vs Predicted (Test Data)')
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.legend()
            plt.show()

            # Evaluate the model
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            print("Mean Absolute Error (MAE):", mae)
            print("Mean Squared Error (MSE):", mse)

            # Plot residuals
            residuals = y_test - y_pred
            plt.figure(figsize=(10, 6))
            plt.plot(y_test.index, residuals, label='Residuals', color='green')
            plt.title('Residuals (Test Data)')
            plt.xlabel('Date')
            plt.ylabel('Residual')
            plt.legend()
            plt.show()

            # Check for autocorrelation in residuals
            sm.graphics.tsa.plot_acf(residuals, lags=30)
            plt.show()



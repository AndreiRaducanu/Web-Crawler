from flask import Flask, render_template, request
import pandas as pd
import time
import os
import threading

app = Flask(__name__)

# Global variable to store the DataFrame
df = None

# Function to load the CSV data into the DataFrame
def load_data():
    global df
    current_directory = os.path.dirname(__file__)
    test_txt_path = os.path.join(current_directory, '..', 'combined_data.csv')
    try:
        df = pd.read_csv(test_txt_path)
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or does not contain any data.")

# Thread function to periodically reload the data
def data_reload_thread():
    while True:
        load_data()
        time.sleep(15)  # Reload data every 60 seconds

# Start the data reload thread
data_thread = threading.Thread(target=data_reload_thread)
data_thread.daemon = True
data_thread.start()

@app.route('/')
def index():
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # Filter DataFrame based on the selected price range
    filtered_data = df[(df['Price'] >= min_price) & (df['Price'] <= max_price)]

    # Pass the filtered data to the template
    return render_template('index.html', data=filtered_data.to_dict(orient='records'))

if __name__ == '__main__':
    load_data()  # Initial data load
    app.run(debug=True)

from flask import Flask, render_template, request
import pandas as pd
import time
import os

app = Flask(__name__)


# Simulate data acquisition delay
def simulate_data_acquisition():
    print("Simulating data acquisition...")
    time.sleep(1)  # Sleep for 30 seconds


# Load the CSV data into a DataFrame
current_directory = os.path.dirname(__file__)
test_txt_path = os.path.join(current_directory, '..', 'combined_data.csv')
simulate_data_acquisition()
df = pd.read_csv(test_txt_path)


@app.route('/')
def index():
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # Filter DataFrame based on the selected price range
    filtered_data = df[(df['Price'] >= min_price) & (df['Price'] <= max_price)]

    # Pass the filtered data to the template
    return render_template('index.html', data=filtered_data.to_dict(orient='records'))  # noqa E501


if __name__ == '__main__':
    app.run(debug=True)

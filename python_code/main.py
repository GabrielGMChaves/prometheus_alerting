import pandas as pd
from datetime import datetime
from flask import Flask

app = Flask(__name__)


def convert_to_openmetrics(record):
    status = record["status"]
    time = record["time"]
    qty = record["f0_"]
    input_datetime = datetime.strptime(str(time), "%Y-%m-%d %H:%M:%S")
    formatted_datetime = input_datetime.strftime("%a, %d %b %Y %H:%M:%S GMT")
    milliseconds_since_epoch = int(input_datetime.timestamp() * 1000)
    openmetrics_string = f"{status}{{time=\"{formatted_datetime}\"}} {qty} {milliseconds_since_epoch}"
    print(openmetrics_string)
    return openmetrics_string

def gather_info(status):
    global filtered_transactions 
    global default_data
    default_data = {
    "f0_": 0,
    "status": status,
    "time": datetime.now().strftime('%Y-%m-%d %H:%M') + ':00'
    }

    transactions1 = pd.read_csv("python_code/transactions_1_cleaned.csv")
    transactions1['time'] = pd.to_datetime(transactions1['time'])
    today_date = datetime.now().date()
    transactions1['time'] = transactions1['time'].apply(lambda x: x.replace(year=today_date.year, month=today_date.month, day=today_date.day))
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M') + ':00'

    filtered_transactions = transactions1[(transactions1['time'] == current_datetime) & (transactions1['status'] == status)]
    
    if filtered_transactions.empty:
        return convert_to_openmetrics(default_data)
    else:
        return convert_to_openmetrics(filtered_transactions.to_dict(orient='records')[0])
    
@app.route('/denied')
def get_denied_transactions():
    return gather_info('denied')


@app.route('/failed')
def get_failed_transactions():
    return gather_info('failed')


@app.route('/reversed')
def get_reversed_transactions():
    return gather_info('reversed')


if __name__ == '__main__':
    app.run(debug=True)
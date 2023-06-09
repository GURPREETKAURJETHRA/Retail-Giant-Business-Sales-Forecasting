from flask import Flask, request, app, jsonify, render_template
from helper import get_total_sales, store_data, sales_data, easter_data
import pickle
import traceback

store_df = store_data()
sales_df = sales_data()
easter_df = easter_data()

ml_model = pickle.load(open('./models/ml_model.pkl', 'rb'))

# initializing app
application = Flask(__name__)

# defining index page
@application.route('/')
def index():
    return render_template('index.html')

# defining an api for predicting sales
@application.route('/predict_api', methods=['POST', 'GET'])
def predict_api():
    print("Method:",request.method)
    try:
        if request.method == 'POST':
            data = [x for x in request.form.values()]
            print("Data:", data)
            store_id = int(data[0])
            from_date = str(data[1])
            to_date = str(data[2])

            total_sales = list(get_total_sales(store_id, from_date, to_date, store_df, sales_df, easter_df, ml_model).values())
            print("Output:", total_sales)
            return render_template('index.html', total = '$ ' + str(round(sum(total_sales))), average = '$ ' + str(round(sum(total_sales)/len(total_sales))))
        else:
            return render_template('index.html')
    except Exception as e:
        print("Error")
        print(type(e))
        print(e)
        print(traceback.print_exc())


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=3000)
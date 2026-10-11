# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
app = Flask("SuperKart")

# Load the trained machine learning model from the correct folder path
model = joblib.load("deployment_files/SuperKart_prediction_model_v1_0.joblib")

# Define a route for the home page (GET request)
@app.route("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API!"

# Define an endpoint for single product prediction (POST request)
@app.route("/v1/price", methods=["POST"])
def predict_price():
    # Get the JSON data from the request body
    product_data = request.get_json()

    # Extract and construct the exact DataFrame features expected by the pipeline
    sample = {
        "Product_Weight": product_data["Product_Weight"],
        "Product_Sugar_Content": product_data["Product_Sugar_Content"],
        "Product_Allocated_Area": product_data["Product_Allocated_Area"],
        "Product_Type": product_data["Product_Type"],
        "Product_MRP": product_data["Product_MRP"],
        "Store_Id": product_data.get("Store_Id", "Unknown"),
        "Store_Size": product_data["Store_Size"],
        "Store_Location_City_Type": product_data["Store_Location_City_Type"],
        "Store_Type": product_data["Store_Type"],
        "Store_Age": product_data["Store_Age"],
        "Product_Id_Prefix": product_data["Product_Id_Prefix"]
    }

    # Convert into a Pandas DataFrame
    input_data = pd.DataFrame([sample])

    # Make prediction using the model pipeline (outputs log sales/sales)
    predicted_sales = model.predict(input_data)[0]
    predicted_sales = round(float(predicted_sales), 2)

    return jsonify({"Predicted Sales": predicted_sales})

# Define an endpoint for batch prediction (POST request)
@app.route("/v1/pricebatch", methods=["POST"])
def predict_batch():
    # Get the uploaded CSV file from the request
    file = request.files["file"]

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Align columns using the mapping we designed for the batch CSV
    column_mapping = {
        "Product_Id_char": "Product_Id_Prefix",
        "Store_Age_Years": "Store_Age",
        "Product_Type_Category": "Product_Type"
    }
    processed_data = input_data.rename(columns=column_mapping)
    
    if "Store_Id" not in processed_data.columns:
        processed_data["Store_Id"] = "Unknown"

    # Make predictions
    predictions = model.predict(processed_data).tolist()
    predictions = [round(float(p), 2) for p in predictions]

    # Return predictions as JSON
    return jsonify({"predictions": predictions})

# Run the Flask application if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)

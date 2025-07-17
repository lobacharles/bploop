import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import mysql.connector
from datetime import datetime, timedelta
import json

class BusinessPredictor:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = self._connect_db()

    def _connect_db(self):
        return mysql.connector.connect(
            host=self.db_config['host'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database']
        )

    def get_business_data(self, business_id):
        query = """
        SELECT metric_date, revenue, employee_count, customer_count
        FROM business_metrics
        WHERE business_id = %s
        ORDER BY metric_date
        """
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(query, (business_id,))
        data = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(data)

    def predict_arima(self, data, forecast_periods=12):
        # Prepare the time series data
        ts_data = data.set_index('metric_date')['revenue']
        
        # Fit ARIMA model
        model = ARIMA(ts_data, order=(1,1,1))
        model_fit = model.fit()
        
        # Make predictions
        forecast = model_fit.forecast(steps=forecast_periods)
        
        # Calculate confidence intervals
        conf_int = model_fit.get_forecast(steps=forecast_periods).conf_int()
        
        return {
            'predictions': forecast.tolist(),
            'lower_ci': conf_int.iloc[:, 0].tolist(),
            'upper_ci': conf_int.iloc[:, 1].tolist()
        }

    def predict_moving_average(self, data, window=3, forecast_periods=12):
        # Calculate moving average
        ma = data['revenue'].rolling(window=window).mean()
        
        # Use the last MA value as the forecast
        last_ma = ma.iloc[-1]
        forecast = [last_ma] * forecast_periods
        
        return {
            'predictions': forecast,
            'window': window
        }

    def save_predictions(self, business_id, predictions, model_type):
        cursor = self.conn.cursor()
        
        # Get the last prediction date
        query = """
        SELECT MAX(prediction_date) as last_date
        FROM business_predictions
        WHERE business_id = %s
        """
        cursor.execute(query, (business_id,))
        last_date = cursor.fetchone()[0] or datetime.now().date()
        
        # Insert new predictions
        insert_query = """
        INSERT INTO business_predictions 
        (business_id, prediction_date, predicted_revenue, confidence_score, prediction_model)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        for i, pred in enumerate(predictions['predictions']):
            pred_date = last_date + timedelta(days=30 * (i + 1))
            confidence = 0.8  # This should be calculated based on model performance
            
            cursor.execute(insert_query, (
                business_id,
                pred_date,
                pred,
                confidence,
                model_type
            ))
        
        self.conn.commit()
        cursor.close()

    def analyze_business_trends(self, business_id):
        data = self.get_business_data(business_id)
        
        if len(data) < 12:  # Need at least 12 months of data
            return None
        
        # Generate predictions using both models
        arima_pred = self.predict_arima(data)
        ma_pred = self.predict_moving_average(data)
        
        # Save predictions
        self.save_predictions(business_id, arima_pred, 'ARIMA')
        self.save_predictions(business_id, ma_pred, 'MovingAverage')
        
        return {
            'arima': arima_pred,
            'moving_average': ma_pred
        }

    def close(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    # Example usage
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'pasig_business_analytics'
    }
    
    predictor = BusinessPredictor(db_config)
    try:
        # Example: Analyze trends for business ID 1
        results = predictor.analyze_business_trends(1)
        print(json.dumps(results, indent=2))
    finally:
        predictor.close() 
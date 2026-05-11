import os
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
import joblib
from app.data.cosmos_client import CosmosDataClient
from app.utils.constants import FULL_THRESHOLD

class AIService:
    def __init__(self, data_client: CosmosDataClient):
        self.data_client = data_client
        self.model_path = 'app/models/ml/fill_rate_model.pkl'
        self.model = self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path): return joblib.load(self.model_path)
        return None

    def train_predictive_model(self, days: int = 10):
        raw_data = self.data_client.get_all_telemetry_records(days=days)
        if not raw_data: raise ValueError("No telemetry data found.")

        df = pd.DataFrame(raw_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by=['deviceId', 'timestamp'])
        training_rows = []

        for device_id, group in df.groupby('deviceId'):
            records = group.to_dict('records')
            for i in range(len(records) - 1):
                cur, nxt = records[i], records[i + 1]
                delta_fill = nxt['fill_level'] - cur['fill_level']
                delta_time = (nxt['timestamp'] - cur['timestamp']).total_seconds() / 3600.0

                if delta_fill > 0 and delta_time > 0:
                    training_rows.append({
                        'hour_of_day': cur['timestamp'].hour,
                        'day_of_week': cur['timestamp'].weekday(),
                        'fill_rate': delta_fill / delta_time
                    })

        train_df = pd.DataFrame(training_rows)
        if len(train_df) < 10: raise ValueError("Not enough valid filling events.")

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(train_df[['hour_of_day', 'day_of_week']], train_df['fill_rate'])

        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(model, self.model_path)
        self.model = model
        return {"status": "success"}

    def simulate_future_state(self, all_bins, target_date: datetime) -> list:
        now = datetime.now()
        hours_ahead = max(0, (target_date.timestamp() - now.timestamp()) / 3600.0)
        predicted_rate = 0.5
        if self.model:
            predicted_rate = self.model.predict([[now.hour, now.weekday()]])[0]
        if predicted_rate <= 0.1: predicted_rate = 0.5

        simulated_bins = []
        for b in all_bins:
            future_fill = min(100, int(b.fill_level + (predicted_rate * hours_ahead)))
            simulated_bins.append({"id": b.id, "latitude": b.latitude, "longitude": b.longitude, "fill_level": future_fill})
            
        return simulated_bins
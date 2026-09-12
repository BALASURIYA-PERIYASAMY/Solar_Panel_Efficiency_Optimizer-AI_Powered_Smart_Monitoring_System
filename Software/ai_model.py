import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

class SolarPowerModel:
    def __init__(self, model_path='solar_model.pkl'):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def load_data(self, csv_file):
        """Load solar data from CSV file"""
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(csv_file, encoding='latin-1')
                except UnicodeDecodeError:
                    df = pd.read_csv(csv_file, encoding='cp1252')
            return df
        else:
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    def preprocess_data(self, df):
        """
        Preprocess data for model training
        Assumes CSV has columns like: temperature, humidity, irradiance, power_output
        """
        df = df.dropna()
        
        df_numeric = df.apply(pd.to_numeric, errors='coerce')
        
        df_numeric = df_numeric.dropna(how='all')
        
        df_numeric = df_numeric.dropna(axis=1, how='all')
        
        print(f"Data shape after preprocessing: {df_numeric.shape}")
        print(f"Available columns: {list(df_numeric.columns)}")
        
        # Identify target column
        target_columns = [col for col in df_numeric.columns if col.lower() in ['power_output', 'power', 'target', 'actual_power']]
        
        if not target_columns:
            target_column = df_numeric.columns[-1]
        else:
            target_column = target_columns[0]
        
        # Features are all columns EXCEPT the target column
        feature_columns = [col for col in df_numeric.columns if col != target_column]
        
        print(f"Features: {feature_columns}")
        print(f"Target: {target_column}")
        
        if len(df_numeric) == 0:
            raise ValueError("No valid numeric data found after preprocessing!")
        
        # Drop rows where target column has NaN values
        df_numeric = df_numeric.dropna(subset=[target_column])
        
        # Also drop any rows with NaN in features
        df_numeric = df_numeric[feature_columns + [target_column]].dropna()
        
        print(f"Data shape after removing NaN values: {df_numeric.shape}")
        
        X = df_numeric[feature_columns].values
        y = df_numeric[target_column].values
        
        print(f"X shape: {X.shape}, y shape: {y.shape}")
        print(f"NaN in X: {np.isnan(X).sum()}, NaN in y: {np.isnan(y).sum()}")
        
        return X, y, feature_columns
    
    def train(self, csv_file):
        """Train the model"""
        print("Loading data...")
        df = self.load_data(csv_file)
        
        print("Preprocessing data...")
        X, y, self.feature_columns = self.preprocess_data(df)
        
        print("Splitting data...")
        # Adjust test_size for small datasets
        test_size = 0.2 if len(X) > 10 else max(0.1, 2/len(X))
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        print("Scaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print("Training model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"\nModel Training Complete!")
        print(f"MSE: {mse:.4f}")
        print(f"R² Score: {r2:.4f}")
        
        self.is_trained = True
        self.save_model()
    
    def predict(self, features):
        """Make predictions"""
        if not self.is_trained:
            self.load_model()
        
        features = np.array(features).reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)
        
        return prediction[0]
    
    def save_model(self):
        """Save trained model"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }, self.model_path)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model"""
        if os.path.exists(self.model_path):
            data = joblib.load(self.model_path)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_columns = data['feature_columns']
            self.is_trained = True
            print(f"Model loaded from {self.model_path}")
        else:
            raise FileNotFoundError(f"Model file not found: {self.model_path}")


if __name__ == "__main__":
    # Initialize model
    model = SolarPowerModel()
    
    # Train on your solar data
    try:
        model.train('solar_data.csv')
        
        # Example prediction
        print("\nExample prediction (adjust features based on your data):")
        sample_features = [25.5, 65.0, 800.0]  # Example: temperature, humidity, irradiance
        prediction = model.predict(sample_features)
        print(f"Predicted solar power output: {prediction:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")

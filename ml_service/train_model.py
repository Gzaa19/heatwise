import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import json


# EPA AQI Breakpoints for pollutant concentrations (μg/m³)
AQI_BREAKPOINTS = {
    'co': [
        {'C_low': 0, 'C_high': 4400, 'I_low': 0, 'I_high': 50},
        {'C_low': 4400, 'C_high': 9400, 'I_low': 51, 'I_high': 100},
        {'C_low': 9400, 'C_high': 12400, 'I_low': 101, 'I_high': 150},
        {'C_low': 12400, 'C_high': 15400, 'I_low': 151, 'I_high': 200},
        {'C_low': 15400, 'C_high': 30400, 'I_low': 201, 'I_high': 300},
        {'C_low': 30400, 'C_high': 50400, 'I_low': 301, 'I_high': 500},
    ],
    'no2': [
        {'C_low': 0, 'C_high': 40, 'I_low': 0, 'I_high': 50},
        {'C_low': 40, 'C_high': 80, 'I_low': 51, 'I_high': 100},
        {'C_low': 80, 'C_high': 180, 'I_low': 101, 'I_high': 150},
        {'C_low': 180, 'C_high': 280, 'I_low': 151, 'I_high': 200},
        {'C_low': 280, 'C_high': 400, 'I_low': 201, 'I_high': 300},
        {'C_low': 400, 'C_high': 1000, 'I_low': 301, 'I_high': 500},
    ],
    'o3': [
        {'C_low': 0, 'C_high': 60, 'I_low': 0, 'I_high': 50},
        {'C_low': 60, 'C_high': 120, 'I_low': 51, 'I_high': 100},
        {'C_low': 120, 'C_high': 180, 'I_low': 101, 'I_high': 150},
        {'C_low': 180, 'C_high': 240, 'I_low': 151, 'I_high': 200},
        {'C_low': 240, 'C_high': 600, 'I_low': 201, 'I_high': 500},
    ],
    'pm2_5': [
        {'C_low': 0, 'C_high': 12, 'I_low': 0, 'I_high': 50},
        {'C_low': 12, 'C_high': 35.4, 'I_low': 51, 'I_high': 100},
        {'C_low': 35.4, 'C_high': 55.4, 'I_low': 101, 'I_high': 150},
        {'C_low': 55.4, 'C_high': 150.4, 'I_low': 151, 'I_high': 200},
        {'C_low': 150.4, 'C_high': 250.4, 'I_low': 201, 'I_high': 300},
        {'C_low': 250.4, 'C_high': 500.4, 'I_low': 301, 'I_high': 500},
    ],
    'pm10': [
        {'C_low': 0, 'C_high': 54, 'I_low': 0, 'I_high': 50},
        {'C_low': 54, 'C_high': 154, 'I_low': 51, 'I_high': 100},
        {'C_low': 154, 'C_high': 254, 'I_low': 101, 'I_high': 150},
        {'C_low': 254, 'C_high': 354, 'I_low': 151, 'I_high': 200},
        {'C_low': 354, 'C_high': 424, 'I_low': 201, 'I_high': 300},
        {'C_low': 424, 'C_high': 604, 'I_low': 301, 'I_high': 500},
    ],
}


def calculate_sub_aqi(concentration, breakpoints):
    """Calculate sub-AQI for a single pollutant using EPA formula"""
    for bp in breakpoints:
        if bp['C_low'] <= concentration <= bp['C_high']:
            aqi = ((bp['I_high'] - bp['I_low']) / (bp['C_high'] - bp['C_low'])) * (concentration - bp['C_low']) + bp['I_low']
            return aqi
    return breakpoints[-1]['I_high']


def calculate_aqi(co, no2, o3, pm2_5, pm10):
    """Calculate overall AQI (maximum of all sub-AQIs)"""
    sub_aqis = {
        'co': calculate_sub_aqi(co, AQI_BREAKPOINTS['co']),
        'no2': calculate_sub_aqi(no2, AQI_BREAKPOINTS['no2']),
        'o3': calculate_sub_aqi(o3, AQI_BREAKPOINTS['o3']),
        'pm2_5': calculate_sub_aqi(pm2_5, AQI_BREAKPOINTS['pm2_5']),
        'pm10': calculate_sub_aqi(pm10, AQI_BREAKPOINTS['pm10']),
    }
    return max(sub_aqis.values())


def generate_realistic_data(n_samples: int = 3000) -> pd.DataFrame:
    """Generate realistic synthetic data based on Jakarta/tropical climate patterns"""
    np.random.seed(42)
    
    # Temperature ranges for tropical urban areas (Jakarta)
    # Morning (5-9): 24-28°C, Midday (10-14): 30-35°C, Afternoon (15-18): 28-33°C, Night (19-4): 25-29°C
    time_period = np.random.choice(['morning', 'midday', 'afternoon', 'night'], n_samples, 
                                    p=[0.2, 0.3, 0.25, 0.25])
    
    temperature = np.zeros(n_samples)
    humidity = np.zeros(n_samples)
    
    for i, period in enumerate(time_period):
        if period == 'morning':
            temperature[i] = np.random.uniform(24, 28)
            humidity[i] = np.random.uniform(70, 90)
        elif period == 'midday':
            temperature[i] = np.random.uniform(30, 36)
            humidity[i] = np.random.uniform(50, 70)
        elif period == 'afternoon':
            temperature[i] = np.random.uniform(28, 33)
            humidity[i] = np.random.uniform(60, 80)
        else:  # night
            temperature[i] = np.random.uniform(25, 29)
            humidity[i] = np.random.uniform(75, 95)
    
    # Add some noise
    temperature += np.random.normal(0, 1.5, n_samples)
    temperature = np.clip(temperature, 20, 40)
    humidity += np.random.normal(0, 5, n_samples)
    humidity = np.clip(humidity, 30, 100)
    
    # Pollutant concentrations - realistic ranges for Jakarta
    # CO: typically 200-1500 μg/m³ in urban areas
    co = np.random.lognormal(mean=6.5, sigma=0.8, size=n_samples)
    co = np.clip(co, 100, 20000)
    
    # NO2: typically 20-100 μg/m³ in urban areas
    no2 = np.random.lognormal(mean=3.5, sigma=0.6, size=n_samples)
    no2 = np.clip(no2, 5, 300)
    
    # O3: typically 30-150 μg/m³ (higher during sunny periods)
    o3_base = np.random.lognormal(mean=4.0, sigma=0.5, size=n_samples)
    # Higher O3 during midday (photochemical smog)
    o3_factor = np.where(time_period == 'midday', 1.5, 1.0)
    o3 = o3_base * o3_factor
    o3 = np.clip(o3, 10, 250)
    
    # PM2.5: typically 15-80 μg/m³ in Jakarta
    pm2_5 = np.random.lognormal(mean=3.2, sigma=0.6, size=n_samples)
    pm2_5 = np.clip(pm2_5, 5, 200)
    
    # PM10: typically 30-150 μg/m³
    pm10 = pm2_5 * np.random.uniform(1.5, 3.0, n_samples)
    pm10 = np.clip(pm10, 10, 400)
    
    # Calculate AQI based on EPA formula
    aqi = np.array([
        calculate_aqi(co[i], no2[i], o3[i], pm2_5[i], pm10[i])
        for i in range(n_samples)
    ])
    
    # Add small noise but keep realistic
    aqi += np.random.normal(0, 2, n_samples)
    aqi = np.clip(aqi, 0, 500)
    
    data = pd.DataFrame({
        'temperature': temperature,
        'humidity': humidity,
        'co': co,
        'no2': no2,
        'o3': o3,
        'pm2_5': pm2_5,
        'pm10': pm10,
        'aqi': aqi
    })
    
    return data


def build_model(input_shape: int) -> keras.Model:
    """Build neural network model for AQI prediction"""
    model = keras.Sequential([
        layers.Input(shape=(input_shape,)),
        layers.Dense(128, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01)),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01)),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu'),
        layers.Dense(16, activation='relu'),
        layers.Dense(1, activation='linear')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='mse',
        metrics=[keras.metrics.MeanAbsoluteError(name='mae')]
    )
    
    return model


def train_and_save_model():
    """Train the model and save artifacts"""
    print("=" * 60)
    print("HeatWise AQI Prediction Model Training")
    print("TensorFlow version:", tf.__version__)
    print("=" * 60)
    
    # Create artifacts directory
    artifacts_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # Generate training data
    print("\n[1/5] Generating realistic synthetic training data...")
    data = generate_realistic_data(n_samples=3000)
    print(f"      Generated {len(data)} samples")
    print(f"      Features: {list(data.columns[:-1])}")
    print(f"      Target: aqi")
    print(f"\n      Data Statistics:")
    print(data.describe().round(2))
    
    # Prepare features and target
    feature_columns = ['temperature', 'humidity', 'co', 'no2', 'o3', 'pm2_5', 'pm10']
    X = data[feature_columns].values
    y = data['aqi'].values
    
    # Scale features using StandardScaler
    print("\n[2/5] Scaling features...")
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X_scaled[:split_idx], X_scaled[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    print(f"\n[3/5] Splitting data...")
    print(f"      Training samples: {len(X_train)}")
    print(f"      Validation samples: {len(X_val)}")
    
    # Build model
    print("\n[4/5] Building neural network model...")
    model = build_model(input_shape=X.shape[1])
    model.summary()
    
    # Train model
    print("\n[5/5] Training model...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32,
        verbose=1,
        callbacks=[
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=7,
                min_lr=0.00001
            )
        ]
    )
    
    # Evaluate model
    val_loss, val_mae = model.evaluate(X_val, y_val, verbose=0)
    print(f"\n      Final Validation Loss (MSE): {val_loss:.4f}")
    print(f"      Final Validation MAE: {val_mae:.4f}")
    
    # Save model using native Keras format
    model_path = os.path.join(artifacts_dir, 'heat_wise_model.keras')
    model.save(model_path)
    print(f"\n      Model saved to: {model_path}")
    
    # Also save as SavedModel format for better compatibility
    savedmodel_path = os.path.join(artifacts_dir, 'heat_wise_saved_model')
    model.save(savedmodel_path, save_format='tf')
    print(f"      SavedModel saved to: {savedmodel_path}")
    
    # Save scaler parameters
    scaler_params = {
        'mean': scaler.mean_.tolist(),
        'scale': scaler.scale_.tolist(),
        'feature_names': feature_columns
    }
    
    scaler_path = os.path.join(artifacts_dir, 'scaler_params.json')
    with open(scaler_path, 'w') as f:
        json.dump(scaler_params, f, indent=2)
    print(f"      Scaler params saved to: {scaler_path}")
    
    # Save model info
    model_info = {
        'training_samples': len(X_train),
        'validation_samples': len(X_val),
        'final_val_loss': float(val_loss),
        'final_val_mae': float(val_mae),
        'epochs_trained': len(history.history['loss']),
        'feature_columns': feature_columns,
        'tensorflow_version': tf.__version__,
        'model_format': 'keras'
    }
    
    info_path = os.path.join(artifacts_dir, 'model_info.json')
    with open(info_path, 'w') as f:
        json.dump(model_info, f, indent=2)
    print(f"      Model info saved to: {info_path}")
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    
    return model, history


if __name__ == "__main__":
    train_and_save_model()

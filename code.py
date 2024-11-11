import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Initialize parameters
num_rows = 100
start_date = datetime(2024, 10, 1, 8, 0, 0)

# Generate data
data = {
    "Index": range(1, num_rows + 1),
    "Timestamp": [start_date + timedelta(days=i) for i in range(num_rows)],
    "Water": np.random.randint(480, 531, size=num_rows),  # Water in mL
    "Surrounding": np.round(np.random.uniform(22.5, 24.5, size=num_rows), 1),  # Temperature in °C
    "Humidity": np.random.randint(59, 67, size=num_rows),  # Humidity in percentage
    "SR-04": np.round(np.random.uniform(0.45, 0.51, size=num_rows), 2),  # Soil moisture level (normalized)
    "Gas": np.random.randint(410, 421, size=num_rows),  # Gas concentration in ppm
    "Growth": np.round(np.linspace(0.2, 10.0, num_rows), 1)  # Simulated plant growth over time
}

# Create DataFrame
df = pd.DataFrame(data)

# Define path and save to CSV
csv_path = './sensor_growth_data.csv'
df.to_csv(csv_path, index=False)

csv_path  # Output path to confirm

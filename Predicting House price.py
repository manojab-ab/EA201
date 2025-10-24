import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Step 1: Create dataset
data = {
    'Area': [1200, 1400, 1600, 1700, 1850],
    'Rooms': [3, 4, 3, 5, 4],
    'Distance': [5, 3, 8, 2, 4],
    'Age': [10, 3, 20, 15, 7],
    'Price': [120, 150, 130, 180, 170]
}

df = pd.DataFrame(data)
print("Dataset:\n", df)

# Step 2: Define features (X) and target (y)
X = df[['Area', 'Rooms', 'Distance', 'Age']]
y = df['Price']

# Step 3: Train Linear Regression model
model = LinearRegression()
model.fit(X, y)

# Step 4: Display model parameters
print("\nIntercept (b0):", model.intercept_)
print("Coefficients (b1, b2, b3, b4):", model.coef_)

# Step 5: Predict prices for all houses
y_pred = model.predict(X)
df['Predicted Price'] = y_pred
print("\nPredicted Prices:\n", df)

# Step 6: Calculate model accuracy (R² score)
r2 = r2_score(y, y_pred)
print("\nModel R² Score:", round(r2, 3))

# Step 7: Predict price for a new house
# Example: Area=1500 sqft, Rooms=3, Distance=4 km, Age=5 years
# Step 7: Predict price for a new house
# Example: Area=1500 sqft, Rooms=3, Distance=4 km, Age=5 years
new_house = [[1500, 3, 4, 5]]
predicted_price = model.predict(new_house)
print("\nPredicted Price for New House (Rs Lacs):", round(predicted_price[0], 2))

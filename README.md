# Basketball_ML

A machine learning project that combines a basketball game simulation with polynomial regression to predict optimal shooting parameters.

## Overview

This project consists of three main components:
1. An interactive basketball game where players can manually shoot baskets
2. A data collection and model training system using polynomial regression
3. A testing environment to validate the trained model

## Project Structure

```
Basketball_ML/
├── training_game.py      # Interactive basketball game for data collection
├── poly_regression.ipynb # Jupyter notebook for model training
├── test_model.py      # Game environment for testing the trained model
├── data.csv             # Collected game data
└── model.pkl            # Exported trained model
```

## Features

### Training Game (`training_game.py`)
- Interactive basketball shooting game
- Manual control of shooting parameters (speed and angle)
- Automatic data collection after each shot
- Data stored in CSV format with the following parameters:
  - Speed
  - Angle
  - Rim_center_x (basket position)

### Model Training (`poly_regression.ipynb`)
- Jupyter notebook environment for data analysis and model training
- Uses scikit-learn library for polynomial regression
- Processes collected game data from data.csv
- Exports the trained model as a pickle file

### Model Testing (`test_model.py`)
- Testing environment for the trained model
- Imports the trained polynomial regression model
- Allows validation of model predictions in the game environment

## Getting Started

### Prerequisites
```bash
pip install numpy pandas pickle pygame
```

### Usage

1. **Data Collection**
   ```bash
   python training_game.py
   ```
   - Play the game manually
   - Data will be automatically saved to data.csv

2. **Model Training**
   - Open `poly_regression.ipynb` in Jupyter Notebook
   - Run all cells to train the model
   - The model will be saved as `model.pkl`

3. **Testing**
   ```bash
   python Test_model.py
   ```
   - Test the trained model's predictions


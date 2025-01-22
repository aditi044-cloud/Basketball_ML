# Basketball Shooting Simulation with Polynomial Regression

This project simulates a basketball shooting game where you can manually play the game, collect data, train a polynomial regression model, and test the trained model to automate the shooting process.

## Table of Contents
1. [Overview](#overview)
2. [Files](#files)
3. [Setup](#setup)
4. [How to Use](#how-to-use)
   - [Manual Gameplay](#manual-gameplay)
   - [Training the Model](#training-the-model)
   - [Testing the Model](#testing-the-model)
5. [Dependencies](#dependencies)
6. [License](#license)

---

## Overview

The project consists of three main components:
1. **Manual Gameplay**: Play the basketball game manually, and collect data (speed, angle, and rim position) for training.
2. **Model Training**: Use the collected data to train a polynomial regression model using scikit-learn.
3. **Model Testing**: Test the trained model in an automated basketball shooting simulation.

---

## Files

1. **`training_game.py`**:
   - A Python script where you can manually play the basketball game.
   - After each game, the data (speed, angle, and rim position) is appended to `data.csv`.

2. **`poly_regression.ipynb`**:
   - A Jupyter Notebook for training a polynomial regression model using the data from `data.csv`.
   - The trained model is exported as a pickle file (`modell.pkl`).

3. **`test_model.py`**:
   - A Python script to test the trained model in an automated basketball shooting simulation.

4. **`data.csv`**:
   - A CSV file where the game data (speed, angle, and rim position) is stored.

5. **`modell.pkl`**:
   - A pickle file containing the trained polynomial regression model.

---

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/basketball-shooting-simulation.git
   cd basketball-shooting-simulation

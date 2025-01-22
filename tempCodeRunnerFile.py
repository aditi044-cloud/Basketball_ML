    # Load left model and extract player name from file name
        left_model_file = 'model_l.pkl'  # Replace with your actual file name
        with open(left_model_file, 'rb') as f:
            model_data = pickle.load(f)
            self.model_l = model_data['model']
            self.poly_l = model_data['poly']
        # Extract just the name part before .pkl
        self.player_left_name = left_model_file.split('.')[0]

        # Load right model and extract player name from file name
        right_model_file = 'model_r.pkl'  # Replace with your actual file name
        with open(right_model_file, 'rb') as f:
            model_data = pickle.load(f)
            self.model_r = model_data['model']
            self.poly_r = model_data['poly']
        # Extract just the name part before .pkl
        self.player_right_name = right_model_file.split('.')[0]
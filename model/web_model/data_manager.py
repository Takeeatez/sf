import json
import os
import datetime
import numpy as np

class DataManager:
    def __init__(self, base_path='exercise_data'):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def save_exercise_data(self, exercise_type, sets_data, total_duration):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{exercise_type}_{timestamp}.json"
        filepath = os.path.join(self.base_path, filename)

        # 정확도 계산
        overall_accuracy = self.calculate_overall_accuracy(sets_data)

        data = {
            "exercise_type": exercise_type,
            "date": datetime.datetime.now().isoformat(),
            "total_duration": total_duration,
            "sets": sets_data,
            "overall_accuracy": overall_accuracy
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

        return filepath

    def load_exercise_data(self, filepath):
        with open(filepath, 'r') as f:
            return json.load(f)

    def get_exercise_history(self, exercise_type=None):
        history = []
        for filename in os.listdir(self.base_path):
            if filename.endswith('.json'):
                if exercise_type is None or filename.startswith(exercise_type):
                    filepath = os.path.join(self.base_path, filename)
                    data = self.load_exercise_data(filepath)
                    history.append(data)
        return history

    def calculate_overall_accuracy(self, sets_data):
        all_accuracies = []
        for set_data in sets_data:
            if 'accuracies' in set_data:
                all_accuracies.extend(set_data['accuracies'])
        
        if all_accuracies:
            return np.mean(all_accuracies)
        else:
            return None

    def analyze_exercise_progress(self, exercise_type):
        history = self.get_exercise_history(exercise_type)
        if not history:
            return None

        analysis = {
            "exercise_type": exercise_type,
            "total_sessions": len(history),
            "average_duration": np.mean([session['total_duration'] for session in history]),
            "average_accuracy": np.mean([session['overall_accuracy'] for session in history if 'overall_accuracy' in session]),
            "trend": self.calculate_trend([session['overall_accuracy'] for session in history if 'overall_accuracy' in session])
        }

        return analysis

    def calculate_trend(self, accuracies):
        if len(accuracies) < 2:
            return "Not enough data"
        
        slope = np.polyfit(range(len(accuracies)), accuracies, 1)[0]
        if slope > 0.01:
            return "Improving"
        elif slope < -0.01:
            return "Declining"
        else:
            return "Stable"
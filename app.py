from flask import Flask, jsonify, request

app = Flask(__name__)

PROGRAMS = {
    "Fat Loss (FL)": {"factor": 22, "workout": "Squat, Cardio, Bench", "diet": "Egg Whites, Chicken"},
    "Muscle Gain (MG)": {"factor": 35, "workout": "Squat, Bench, Deadlift", "diet": "Eggs, Biryani"},
    "Beginner (BG)": {"factor": 26, "workout": "Air Squats, Push-ups", "diet": "Balanced meals"},
}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "app": "ACEest Fitness"})

@app.route('/programs', methods=['GET'])
def get_programs():
    return jsonify(list(PROGRAMS.keys()))

@app.route('/calories', methods=['POST'])
def calculate_calories():
    data = request.json
    program = data.get('program')
    weight = data.get('weight', 0)
    if program not in PROGRAMS:
        return jsonify({'error': 'Invalid program'}), 400
    calories = int(weight * PROGRAMS[program]['factor'])
    return jsonify({'calories': calories, 'program': program})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
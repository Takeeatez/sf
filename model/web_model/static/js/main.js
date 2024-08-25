document.addEventListener('DOMContentLoaded', function() {
    const exerciseForm = document.getElementById('exercise-form');
    if (exerciseForm) {
        exerciseForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(exerciseForm);
            const data = Object.fromEntries(formData);
            
            fetch('/set_exercise', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.href = '/exercise';
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    }

    const stopExerciseButton = document.getElementById('stop-exercise');
    if (stopExerciseButton) {
        stopExerciseButton.addEventListener('click', function() {
            window.location.href = '/';
        });
    }
});
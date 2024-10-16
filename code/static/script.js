document.getElementById('project-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const userName = document.getElementById('userName').value;
    const projectName = document.getElementById('projectName').value;
    const siteLocation = document.getElementById('siteLocation').value;
    const buildingType = document.getElementById('buildingType').value;
    const budget = document.getElementById('budget').value;
    const formData = {
        userName,
        projectName,
        siteLocation,
        buildingType,
        budget
    };
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').innerText = data.message;
        document.getElementById('project-form').reset();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
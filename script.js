function startSimulation() {
  // Use JavaScript to send a request to the Python backend
  // You can use AJAX, Fetch API, or any other method to make a request

  // Example using Fetch API:
  fetch('/run_simulation')
    .then(response => response.blob())
    .then(data => {
      // Handle the response from the Python backend
      // Convert the image blob to URL and create an <img> element
      const imageUrl = URL.createObjectURL(data);
      const imgElement = document.createElement('img');
      imgElement.src = imageUrl;

      // Clear the simulation container and append the image element
      const simulationContainer = document.getElementById('simulation-container');
      simulationContainer.innerHTML = '';
      simulationContainer.appendChild(imgElement);
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

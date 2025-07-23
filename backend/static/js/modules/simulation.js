export function initSimulationControls() {
    const speedButtons = document.querySelectorAll('.speed-btn');
    const timeDisplay = document.getElementById('simulation-time');
    if (!speedButtons.length || !timeDisplay) return;

    let currentSpeed = 0;
    let simulationTime = 0;
    let simulationInterval;

    function startSimulation() {
        stopSimulation();
        simulationInterval = setInterval(() => {
            simulationTime += currentSpeed;
            updateSimulationTime();
        }, 1000);
    }

    function stopSimulation() {
        clearInterval(simulationInterval);
    }

    function updateSimulationTime() {
        const hours = Math.floor(simulationTime / 3600);
        const minutes = Math.floor((simulationTime % 3600) / 60);
        const seconds = simulationTime % 60;

        timeDisplay.textContent =
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    speedButtons.forEach(button => {
        button.addEventListener('click', () => {
            speedButtons.forEach(btn => btn.classList.remove('active-speed'));
            button.classList.add('active-speed');
            currentSpeed = parseInt(button.getAttribute('data-speed'));

            if (currentSpeed > 0) {
                startSimulation();
            } else {
                stopSimulation();
            }
        });
    });

    // Ativa o botão de velocidade 0 inicialmente
    document.querySelector('.speed-btn[data-speed="0"]')?.classList.add('active-speed');
}

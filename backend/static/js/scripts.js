// Copy host IP to clipboard
function copyHostIP() {
    const ipField = document.getElementById('host-ip');
    ipField.select();
    document.execCommand('copy');
    alert('IP copiado para a área de transferência!');
}

// Toggle sidebar
const sidebar = document.getElementById('sidebar');
const toggleSidebar = document.getElementById('toggle-sidebar');
const logoText = document.getElementById('logo-text');

toggleSidebar.addEventListener('click', () => {
    sidebar.classList.toggle('md:w-20');
    sidebar.classList.toggle('w-64');

    // Alterna visibilidade de todos os labels da sidebar
    document.querySelectorAll('.nav-label').forEach(label => {
        label.classList.toggle('md:hidden');
    });

    // Alterna visibilidade do texto do logo
    logoText.classList.toggle('md:hidden');
});

// Speed controls
const speedButtons = document.querySelectorAll('.speed-btn');
let currentSpeed = 0;
let simulationTime = 0;
let simulationInterval;

speedButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all speed buttons
        speedButtons.forEach(btn => {
            btn.classList.remove('active-speed');
        });

        // Add active class to clicked button
        button.classList.add('active-speed');

        // Set current speed
        currentSpeed = parseInt(button.getAttribute('data-speed'));

        // Start/stop simulation based on speed
        if (currentSpeed > 0) {
            startSimulation();
        } else {
            stopSimulation();
        }
    });
});

function startSimulation() {
    stopSimulation(); // Clear any existing interval

    // Update simulation time every second
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

    document.getElementById('simulation-time').textContent =
        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

document.querySelector('.speed-btn[data-speed="0"]').classList.add('active-speed');


// Timeout para esconder toasts
setTimeout(() => {
    document.querySelectorAll(".toast, .alert, .toast-auto").forEach(el => {
        el.style.opacity = 0;
        setTimeout(() => el.remove(), 300);
    });
}, 3000); // 3000ms = 3s
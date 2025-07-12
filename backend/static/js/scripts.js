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
const navTexts = ['nav-text-1', 'nav-text-2', 'nav-text-3', 'nav-text-4', 'nav-text-5', 'nav-text-6', 'nav-text-7', 'nav-text-8'];
const logoText = document.getElementById('logo-text');

toggleSidebar.addEventListener('click', () => {
    sidebar.classList.toggle('md:w-20');
    sidebar.classList.toggle('w-64');

    // Toggle nav text visibility
    navTexts.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.toggle('md:hidden');
        }
    });

    // Toggle logo text
    logoText.classList.toggle('md:hidden');
});

// Navigation between sections
const navLinks = document.querySelectorAll('nav a');
const sections = document.querySelectorAll('.section-content');

navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();

        // Remove active class from all nav items
        navLinks.forEach(navLink => {
            navLink.classList.remove('active-nav-item');
        });

        // Add active class to clicked nav item
        link.classList.add('active-nav-item');

        // Hide all sections
        sections.forEach(section => {
            section.classList.add('hidden');
        });

        // Show the selected section
        const sectionId = link.getAttribute('data-section');
        document.getElementById(sectionId).classList.remove('hidden');

        // Update header title
        const headerTitle = document.querySelector('header h1');
        if (sectionId === 'variable-income') headerTitle.textContent = 'Renda Variável';
        else if (sectionId === 'fixed-income') headerTitle.textContent = 'Renda Fixa';
        else if (sectionId === 'portfolio') headerTitle.textContent = 'Carteira';
        else if (sectionId === 'import-assets') headerTitle.textContent = 'Importar Ativos';
        else if (sectionId === 'stock-detail') headerTitle.textContent = 'Detalhe do Ativo';
        else if (sectionId === 'fixed-income-detail') headerTitle.textContent = 'Detalhe Renda Fixa';
        else if (sectionId === 'strategies') headerTitle.textContent = 'Estratégias';
        else if (sectionId === 'stats') headerTitle.textContent = 'Estatísticas Multiplayer';
        else if (sectionId === 'lobby') headerTitle.textContent = 'Sala Multiplayer';
        else if (sectionId === 'settings') headerTitle.textContent = 'Configurações';
    });
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

// Initialize with variable income section visible
document.querySelector('nav a[data-section="variable-income"]').classList.add('active-nav-item');
document.querySelector('.speed-btn[data-speed="0"]').classList.add('active-speed');

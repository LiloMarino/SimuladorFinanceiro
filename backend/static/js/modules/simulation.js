export function initSimulationControls() {
    const speedButtons = document.querySelectorAll('.speed-btn');
    const timeDisplay = document.getElementById('simulation-time');
    if (!speedButtons.length || !timeDisplay) return;

    async function updateSpeed(speed) {
        const res = await fetch("/simulation/speed", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ speed }),
        });
        const state = await res.json();
        console.log("Velocidade alterada:", state);
    }

    async function fetchState() {
        const res = await fetch("/simulation/state");
        const state = await res.json();
        timeDisplay.textContent = state.current_date;
        return state;
    }

    speedButtons.forEach(button => {
        button.addEventListener('click', () => {
            speedButtons.forEach(btn => btn.classList.remove('active-speed'));
            button.classList.add('active-speed');

            const newSpeed = parseInt(button.getAttribute('data-speed'));
            updateSpeed(newSpeed);
        });
    });

    // Atualiza o tempo periodicamente (polling simples)
    setInterval(fetchState, 2000);

    // Inicializa estado
    fetchState();
}

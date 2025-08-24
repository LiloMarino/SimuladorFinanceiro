export function initSimulationControls() {
    const speedButtons = document.querySelectorAll('.speed-btn');
    const timeDisplay = document.getElementById('simulation-time');
    if (!speedButtons.length || !timeDisplay) return;

    // Socket global definido em socket.js
    const socket = window.socket;

    socket.on("connect", () => console.log("Conectado ao WebSocket", socket.id));
    socket.on("disconnect", () => console.log("Desconectado"));

    // Atualiza apenas a data
    socket.on("simulation_update", (state) => {
        console.log("simulation_update", state);
        timeDisplay.textContent = state.current_date;
    });
    
    // Atualiza apenas a velocidade
    socket.on("speed_update", (state) => {
        console.log("speed_update", state);
        speedButtons.forEach(btn => {
            btn.classList.toggle("active-speed", parseInt(btn.dataset.speed) === state.speed);
        });
    });

    // Ao clicar, envia via REST
    speedButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const newSpeed = parseInt(button.dataset.speed);
            await fetch("/api/set_speed", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ speed: newSpeed })
            });
        });
    });
}
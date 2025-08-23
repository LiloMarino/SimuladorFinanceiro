import { io } from "https://cdn.socket.io/4.7.1/socket.io.esm.min.js";

export function initSimulationControls() {
    const speedButtons = document.querySelectorAll('.speed-btn');
    const timeDisplay = document.getElementById('simulation-time');
    if (!speedButtons.length || !timeDisplay) return;

    const socket = io(); // conecta no backend

    // 🔹 Recebe atualizações do backend
    socket.on("simulation_update", (state) => {
        timeDisplay.textContent = state.current_date;
        speedButtons.forEach(btn => {
            btn.classList.toggle("active-speed", parseInt(btn.dataset.speed) === state.speed);
        });
    });

    // 🔹 Ao clicar, envia via REST (não WebSocket)
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

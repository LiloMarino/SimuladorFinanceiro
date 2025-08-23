import { initSidebarToggle } from "./modules/sidebar.js";
import { initSimulationControls } from "./modules/simulation.js";
import { initAutoToast } from "./modules/toast.js";

document.addEventListener("DOMContentLoaded", () => {
    initSidebarToggle();
    initSimulationControls();
    initAutoToast();
});

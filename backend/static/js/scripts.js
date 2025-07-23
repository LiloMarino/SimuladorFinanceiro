import { initSidebarToggle } from "./modules/sidebar.js";
import { initImporter } from "./modules/import.js";
import { initSimulationControls } from "./modules/simulation.js";
import { initCopyHostIP } from "./modules/copy.js";
import { initAutoToast } from "./modules/toast.js";

document.addEventListener("DOMContentLoaded", () => {
    initSidebarToggle();
    initImporter();
    initSimulationControls();
    initCopyHostIP();
    initAutoToast();
});

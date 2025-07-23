import { initSidebarToggle } from "./modules/sidebar.js";
import { initDragAndDrop } from "./modules/dragndrop.js";
import { initSimulationControls } from "./modules/simulation.js";
import { initCopyHostIP } from "./modules/copy.js";
import { initAutoToast } from "./modules/toast.js";

document.addEventListener("DOMContentLoaded", () => {
    initSidebarToggle();
    initDragAndDrop();
    initSimulationControls();
    initCopyHostIP();
    initAutoToast();
});

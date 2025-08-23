export function initImporter() {
    // Drag-n-Drop
    const input = document.getElementById("csv-upload");
    const fileNameDisplay = document.getElementById("file-name");
    const dropArea = document.getElementById("drop-area");

    if (dropArea && input && fileNameDisplay) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.add('border-blue-500', 'bg-blue-50');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.remove('border-blue-500', 'bg-blue-50');
            });
        });

        dropArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                fileNameDisplay.textContent = `Arquivo selecionado: ${files[0].name}`;
            }
        });

        input.addEventListener("change", function () {
            const file = input.files[0];
            if (file) {
                fileNameDisplay.textContent = `Arquivo selecionado: ${file.name}`;
            } else {
                fileNameDisplay.textContent = "";
            }
        });

        // --- Modal de confirmação ---
        const modal = document.getElementById('confirm-modal');
        const confirmBtn = document.getElementById('confirm-btn');
        const cancelBtn = document.getElementById('cancel-btn');

        let currentForm = null;
        let currentAction = null;

        // Captura qualquer botão com data-open-modal
        document.querySelectorAll("[data-open-modal]").forEach(btn => {
            btn.addEventListener("click", () => {
                const formId = btn.getAttribute("data-form");
                const action = btn.getAttribute("data-action");

                currentForm = document.getElementById(formId);
                currentAction = action;

                modal.classList.remove("hidden");
            });
        });

        cancelBtn?.addEventListener("click", () => {
            modal.classList.add("hidden");
            currentForm = null;
            currentAction = null;
        });

        confirmBtn?.addEventListener("click", () => {
            if (currentForm && currentAction) {
                // injeta hidden action
                const actionInput = document.createElement("input");
                actionInput.type = "hidden";
                actionInput.name = "action";
                actionInput.value = currentAction;
                currentForm.appendChild(actionInput);

                currentForm.submit();
            }

            modal.classList.add("hidden");
            currentForm = null;
            currentAction = null;
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initImporter();
});

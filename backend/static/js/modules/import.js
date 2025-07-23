export function initImporter() {
    // Drag-n-Drop
    const input = document.getElementById("csv-upload");
    const fileNameDisplay = document.getElementById("file-name");
    const dropArea = document.getElementById("drop-area");

    if (!dropArea || !input || !fileNameDisplay) return;

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

    // Modal de confirmação para importação
    const modal = document.getElementById('confirm-modal');
    const openModalBtn = document.getElementById('open-modal-btn');
    const confirmBtn = document.getElementById('confirm-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const csvForm = document.getElementById('csv-form');

    if (openModalBtn && modal && confirmBtn && cancelBtn && csvForm) {
        openModalBtn.addEventListener('click', () => {
            modal.classList.remove('hidden');
        });

        cancelBtn.addEventListener('click', () => {
            modal.classList.add('hidden');
        });

        confirmBtn.addEventListener('click', () => {
            modal.classList.add('hidden');
            csvForm.submit();
        });
    }
}

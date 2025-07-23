export function initAutoToast() {
    setTimeout(() => {
        document.querySelectorAll(".toast, .alert, .toast-auto").forEach(el => {
            el.style.opacity = 0;
            setTimeout(() => el.remove(), 300);
        });
    }, 4000);
}

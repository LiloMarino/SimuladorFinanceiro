export function initSidebarToggle() {
    const sidebar = document.getElementById('sidebar');
    const toggleSidebar = document.getElementById('toggle-sidebar');
    const logoText = document.getElementById('logo-text');

    if (!sidebar || !toggleSidebar || !logoText) return;

    toggleSidebar.addEventListener('click', () => {
        sidebar.classList.toggle('md:w-20');
        sidebar.classList.toggle('w-64');

        document.querySelectorAll('.nav-label').forEach(label => {
            label.classList.toggle('md:hidden');
        });

        logoText.classList.toggle('md:hidden');
    });
}

export function initCopyHostIP() {
    const ipField = document.getElementById('host-ip');
    if (!ipField) return;

    document.getElementById('copy-ip-btn')?.addEventListener('click', () => {
        ipField.select();
        document.execCommand('copy');
        alert('IP copiado para a área de transferência!');
    });
}

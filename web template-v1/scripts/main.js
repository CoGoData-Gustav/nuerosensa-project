function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.style.display = sidebar.style.display === 'block' ? 'none' : 'block';
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.style.display = 'none';
}

window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        document.getElementById('sidebar').style.display = 'none';
    }
});
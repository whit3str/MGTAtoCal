async function triggerAction(action) {
    const notification = document.getElementById('notification');
    
    // Reset classes
    notification.className = 'notification';
    notification.textContent = 'Lancement en cours...';
    
    try {
        const response = await fetch(`/api/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        notification.textContent = data.message;
        
        // Hide notification & gently reload after a delay to reflect DB state changes
        setTimeout(() => {
            notification.classList.add('hidden');
            setTimeout(() => {
                window.location.reload();
            }, 600);
        }, 3000);
        
    } catch (error) {
        notification.textContent = `Erreur de connexion: ${error.message}`;
        notification.style.background = 'rgba(239, 68, 68, 0.15)';
        notification.style.color = '#ef4444';
        notification.style.borderColor = 'rgba(239, 68, 68, 0.3)';
    }
}

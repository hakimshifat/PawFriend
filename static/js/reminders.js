document.addEventListener('DOMContentLoaded', function() {
    // Initialize date picker with current date
    initializeDatePicker();
    
    // Set up event listeners for reminder completion buttons
    setupReminderCompletion();
    
    // Set up event listeners for tabs
    setupTabListeners();
    
    // Visualize the queue structure
    visualizeQueue();
});

function initializeDatePicker() {
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const now = new Date();
        const formattedDate = formatDate(now);
        dateInput.value = formattedDate;
    }
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function setupPetSelection() {
    const petSelect = document.getElementById('pet_id');
    if (!petSelect) return;
    
    petSelect.addEventListener('change', function() {
        // In a real app, this could trigger fetching the pet's medication history
        console.log('Selected pet:', this.value);
    });
}

function setupReminderCompletion() {
    // Find all forms for marking reminders as complete
    document.querySelectorAll('form[action*="mark_reminder_complete"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            // Normally we would let the form submit to the server
            // But for demo purposes, we can add animations
            const reminderCard = this.closest('.card');
            if (reminderCard) {
                reminderCard.style.transition = 'all 0.3s ease';
                reminderCard.style.opacity = '0.5';
                reminderCard.style.transform = 'translateX(100%)';
                
                // Let the animation complete before actual submission
                setTimeout(() => {
                    // This would normally remove the form submit event prevention
                    // and let the form submit
                    // e.preventDefault();
                }, 300);
            }
        });
    });
}

function setupTabListeners() {
    const tabLinks = document.querySelectorAll('#reminderTabs button');
    if (!tabLinks.length) return;
    
    tabLinks.forEach(tab => {
        tab.addEventListener('click', function() {
            // When tab is clicked, update the visualization if needed
            const tabId = this.getAttribute('id');
            
            if (tabId === 'upcoming-tab') {
                // Re-visualize the queue when on the upcoming tab
                setTimeout(visualizeQueue, 300);
            }
        });
    });
}

function visualizeQueue() {
    const queueVisualization = document.getElementById('queue-visualization');
    if (!queueVisualization) return;
    
    // For a real application, we would animate the queue to demonstrate FIFO
    // Here, we'll just add a simple animation for demo purposes
    animateQueue();
}

function animateQueue() {
    const queueItems = document.querySelectorAll('.queue-item');
    if (!queueItems.length) return;
    
    // Reset any previous animations
    queueItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
    });
    
    // Animate items one by one with a delay
    queueItems.forEach((item, index) => {
        setTimeout(() => {
            item.style.transition = 'all 0.5s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

function validateReminderForm() {
    const form = document.getElementById('reminderForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const petId = document.getElementById('pet_id').value;
        const date = document.getElementById('date').value;
        const medication = document.getElementById('medication').value;
        
        if (!petId || !date || !medication) {
            e.preventDefault();
            alert('Please fill out all required fields.');
        }
    });
}

function setupRecurrenceOptions() {
    // This would be used for setting up recurring reminders
    // Not implemented in the current version
}

function setupFilterOptions() {
    // This would be used for filtering reminders by type, pet, etc.
    // Not implemented in the current version
}

function setupSortOptions() {
    // This would be used for sorting reminders by date, priority, etc.
    // Not implemented in the current version
}

function setupBulkActions() {
    // This would be used for bulk actions like marking multiple reminders complete
    // Not implemented in the current version
}

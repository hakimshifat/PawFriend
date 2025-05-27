document.addEventListener('DOMContentLoaded', function() {
    // Initialize date picker with current date
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const now = new Date();
        const month = (now.getMonth() + 1).toString().padStart(2, '0');
        const day = now.getDate().toString().padStart(2, '0');
        dateInput.value = `${now.getFullYear()}-${month}-${day}`;
    }
    
    // Initialize view buttons for appointment details
    initializeViewButtons();
    
    // Visualize the min heap structure
    visualizeHeap();
    
    // Initialize the urgent photo upload section
    toggleUrgentPhotoUpload();
});

function initializeViewButtons() {
    const viewButtons = document.querySelectorAll('.view-appointment');
    const appointmentModal = new bootstrap.Modal(document.getElementById('appointmentModal'));
    
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const appointmentId = this.getAttribute('data-id');
            showAppointmentDetails(appointmentId);
            appointmentModal.show();
        });
    });
}

function showAppointmentDetails(appointmentId) {
    // In a real application, this would fetch the details from the server
    // For now, we'll find the appointment in the table
    const modalBody = document.getElementById('appointmentModalBody');
    const table = document.querySelector('table');
    
    if (!table) {
        modalBody.innerHTML = '<p class="text-center text-muted">Appointment details not available.</p>';
        return;
    }
    
    const rows = table.querySelectorAll('tbody tr');
    let foundAppointment = null;
    
    rows.forEach(row => {
        const viewButton = row.querySelector('.view-appointment');
        if (viewButton && viewButton.getAttribute('data-id') === appointmentId) {
            const petName = row.cells[0].textContent;
            const date = row.cells[1].textContent;
            const time = row.cells[2].textContent;
            const reason = row.cells[3].textContent;
            const priorityElement = row.cells[4].querySelector('.badge');
            const priority = priorityElement ? priorityElement.textContent : 'Unknown';
            
            foundAppointment = { petName, date, time, reason, priority };
        }
    });
    
    if (foundAppointment) {
        let priorityClass = 'bg-info';
        switch (foundAppointment.priority.trim()) {
            case 'Emergency': priorityClass = 'bg-danger'; break;
            case 'Urgent': priorityClass = 'bg-warning text-dark'; break;
            case 'Regular': priorityClass = 'bg-info'; break;
            case 'Vaccination': priorityClass = 'bg-success'; break;
            case 'Grooming': priorityClass = 'bg-secondary'; break;
        }
        
        modalBody.innerHTML = `
            <div class="text-center mb-3">
                <div class="display-1 text-primary">
                    <i class="fas fa-calendar-check"></i>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-4 text-muted">Pet:</div>
                <div class="col-8 fw-bold">${foundAppointment.petName}</div>
            </div>
            <div class="row mb-3">
                <div class="col-4 text-muted">Date:</div>
                <div class="col-8">${foundAppointment.date}</div>
            </div>
            <div class="row mb-3">
                <div class="col-4 text-muted">Time:</div>
                <div class="col-8">${foundAppointment.time}</div>
            </div>
            <div class="row mb-3">
                <div class="col-4 text-muted">Reason:</div>
                <div class="col-8">${foundAppointment.reason}</div>
            </div>
            <div class="row mb-3">
                <div class="col-4 text-muted">Priority:</div>
                <div class="col-8">
                    <span class="badge ${priorityClass}">${foundAppointment.priority}</span>
                </div>
            </div>
        `;
    } else {
        modalBody.innerHTML = '<p class="text-center text-muted">Appointment details not available.</p>';
    }
}

function visualizeHeap() {
    const heapContainer = document.getElementById('heap-visualization');
    if (!heapContainer) return;
    
    // Get appointments from the table
    const table = document.querySelector('table');
    if (!table) {
        heapContainer.innerHTML = '<p class="text-center text-muted py-5">No appointments to visualize.</p>';
        return;
    }
    
    const rows = table.querySelectorAll('tbody tr');
    const appointments = [];
    
    rows.forEach(row => {
        const petName = row.cells[0].textContent;
        const reason = row.cells[3].textContent;
        const priorityElement = row.cells[4].querySelector('.badge');
        const priority = priorityElement ? priorityElement.textContent : 'Unknown';
        
        appointments.push({ petName, reason, priority });
    });
    
    if (appointments.length === 0) {
        heapContainer.innerHTML = '<p class="text-center text-muted py-5">No appointments to visualize.</p>';
        return;
    }
    
    // Clear the container
    heapContainer.innerHTML = '';
    
    // Create a heap visualization (simplified for display purposes)
    // In a real min-heap, the elements would be arranged by priority value
    const maxNodes = Math.min(appointments.length, 7); // Limit to 7 nodes for space
    
    for (let i = 0; i < maxNodes; i++) {
        const appointment = appointments[i];
        heapContainer.appendChild(createHeapNode(appointment, i));
    }
}

function createHeapNode(appointment, index) {
    const node = document.createElement('div');
    node.className = 'heap-node';
    
    // Position calculation for a binary tree layout
    // Level 0: 1 node, Level 1: 2 nodes, Level 2: 4 nodes
    let level = 0;
    let position = index;
    
    if (index === 0) {
        level = 0;
        position = 0;
    } else if (index <= 2) {
        level = 1;
        position = index - 1;
    } else {
        level = 2;
        position = index - 3;
    }
    
    // Set position based on level and position within level
    const topOffset = level * 90;
    let leftOffset;
    
    if (level === 0) {
        leftOffset = '50%';
    } else if (level === 1) {
        leftOffset = position === 0 ? '25%' : '75%';
    } else {
        const positions = ['12.5%', '37.5%', '62.5%', '87.5%'];
        leftOffset = positions[position];
    }
    
    node.style.top = `${topOffset}px`;
    node.style.left = leftOffset;
    node.style.transform = 'translate(-50%, 0)';
    
    // Set background color based on priority
    let bgColor = 'var(--bs-info)';
    switch (appointment.priority.trim()) {
        case 'Emergency': bgColor = 'var(--bs-danger)'; break;
        case 'Urgent': bgColor = 'var(--bs-warning)'; break;
        case 'Regular': bgColor = 'var(--bs-info)'; break;
        case 'Vaccination': bgColor = 'var(--bs-success)'; break;
        case 'Grooming': bgColor = 'var(--bs-secondary)'; break;
    }
    
    node.style.backgroundColor = bgColor;
    
    // Set content
    node.innerHTML = `
        <div>
            <div class="small fw-bold">${appointment.petName}</div>
            <div class="small">${appointment.priority}</div>
        </div>
    `;
    
    // Add connecting lines to parent nodes (for nodes that aren't the root)
    if (index > 0) {
        const line = document.createElement('div');
        line.style.position = 'absolute';
        line.style.width = '2px';
        line.style.backgroundColor = 'var(--bs-secondary)';
        line.style.zIndex = '-1';
        
        // Connect to parent node
        if (level === 1) {
            // Connect to the root
            line.style.height = '40px';
            line.style.top = '-40px';
            line.style.left = '50%';
        } else if (level === 2) {
            // Connect to level 1 nodes
            line.style.height = '40px';
            line.style.top = '-40px';
            line.style.left = '50%';
        }
        
        node.appendChild(line);
    }
    
    return node;
}

function toggleUrgentPhotoUpload() {
    const prioritySelect = document.getElementById('priority');
    const urgentPhotoSection = document.getElementById('urgentPhotoSection');
    
    if (prioritySelect && urgentPhotoSection) {
        const priority = parseInt(prioritySelect.value);
        
        // Show photo upload for Emergency (1) or Urgent (2) cases
        if (priority === 1 || priority === 2) {
            urgentPhotoSection.style.display = 'block';
        } else {
            urgentPhotoSection.style.display = 'none';
        }
    }
}

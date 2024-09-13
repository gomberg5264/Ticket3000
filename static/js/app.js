document.addEventListener('DOMContentLoaded', () => {
    loadTickets();

    document.getElementById('new-ticket-form').addEventListener('submit', createTicket);
    document.getElementById('purge-completed').addEventListener('click', purgeCompletedTickets);
});

async function loadTickets() {
    const response = await fetch('/api/tickets');
    const tickets = await response.json();
    const ticketList = document.getElementById('ticket-list');
    ticketList.innerHTML = '';
    tickets.forEach(ticket => {
        const li = document.createElement('li');
        li.className = 'ticket';
        li.innerHTML = `
            <span>${ticket.title}</span>
            <span>(${ticket.status})</span>
            <span>Category: ${ticket.category}</span>
            <span>Priority: ${ticket.priority}</span>
            <button onclick="updateTicketStatus(${ticket.id}, '${ticket.status === 'pending' ? 'completed' : 'pending'}')">${ticket.status === 'pending' ? 'Complete' : 'Reopen'}</button>
            <button onclick="deleteTicket(${ticket.id})">Delete</button>
        `;
        ticketList.appendChild(li);
    });
}

async function createTicket(event) {
    event.preventDefault();
    const title = document.getElementById('new-ticket-title').value;
    const category = document.getElementById('new-ticket-category').value;
    const priority = document.getElementById('new-ticket-priority').value;
    const response = await fetch('/api/tickets', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, category, priority }),
    });
    if (response.ok) {
        document.getElementById('new-ticket-title').value = '';
        document.getElementById('new-ticket-category').selectedIndex = 0;
        document.getElementById('new-ticket-priority').selectedIndex = 0;
        loadTickets();
    }
}

async function updateTicketStatus(id, newStatus) {
    const response = await fetch(`/api/tickets/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
    });
    if (response.ok) {
        loadTickets();
    }
}

async function deleteTicket(id) {
    const response = await fetch(`/api/tickets/${id}`, {
        method: 'DELETE',
    });
    if (response.ok) {
        loadTickets();
    }
}

async function purgeCompletedTickets() {
    const response = await fetch('/api/tickets/purge', {
        method: 'POST',
    });
    if (response.ok) {
        loadTickets();
    }
}

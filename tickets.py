from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
import json
import os
import logging

tickets_bp = Blueprint('tickets', __name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CATEGORIES = ['Bug', 'Feature Request', 'Support']
PRIORITY_LEVELS = ['Low', 'Medium', 'High', 'Critical']

@tickets_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', categories=CATEGORIES, priority_levels=PRIORITY_LEVELS)

@tickets_bp.route('/api/tickets', methods=['GET', 'POST'])
@login_required
def api_tickets():
    if request.method == 'GET':
        logger.debug(f"User {current_user.username} requested all tickets")
        tickets = load_tickets()
        return jsonify(tickets)
    elif request.method == 'POST':
        logger.debug(f"User {current_user.username} is creating a new ticket")
        new_ticket = request.json
        tickets = load_tickets()
        new_ticket['id'] = len(tickets) + 1
        new_ticket['status'] = 'pending'
        new_ticket['category'] = new_ticket.get('category', 'Bug')
        new_ticket['priority'] = new_ticket.get('priority', 'Medium')
        new_ticket['created_by'] = current_user.username
        tickets.append(new_ticket)
        save_tickets(tickets)
        logger.debug(f"New ticket created: {new_ticket}")
        return jsonify(new_ticket), 201

@tickets_bp.route('/api/tickets/<int:ticket_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_ticket(ticket_id):
    tickets = load_tickets()
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    if not ticket:
        logger.warning(f"Ticket with id {ticket_id} not found")
        return jsonify({'error': 'Ticket not found'}), 404

    if request.method == 'GET':
        logger.debug(f"User {current_user.username} requested ticket {ticket_id}")
        return jsonify(ticket)
    elif request.method == 'PUT':
        logger.debug(f"User {current_user.username} is updating ticket {ticket_id}")
        update_data = request.json
        ticket.update(update_data)
        save_tickets(tickets)
        logger.debug(f"Ticket {ticket_id} updated: {ticket}")
        return jsonify(ticket)
    elif request.method == 'DELETE':
        logger.debug(f"User {current_user.username} is deleting ticket {ticket_id}")
        if not current_user.is_admin and ticket['created_by'] != current_user.username:
            logger.warning(f"User {current_user.username} attempted to delete ticket {ticket_id} without permission")
            return jsonify({'error': 'You do not have permission to delete this ticket'}), 403
        tickets = [t for t in tickets if t['id'] != ticket_id]
        save_tickets(tickets)
        logger.debug(f"Ticket {ticket_id} deleted")
        return '', 204

@tickets_bp.route('/api/tickets/purge', methods=['POST'])
@login_required
def purge_completed_tickets():
    if not current_user.is_admin:
        logger.warning(f"Non-admin user {current_user.username} attempted to purge completed tickets")
        return jsonify({'error': 'Only admins can purge completed tickets'}), 403
    logger.debug(f"Admin user {current_user.username} is purging completed tickets")
    tickets = load_tickets()
    tickets = [t for t in tickets if t['status'] != 'completed']
    save_tickets(tickets)
    logger.debug("Completed tickets purged")
    return jsonify({'message': 'Completed tickets purged'}), 200

def load_tickets():
    if not os.path.exists('tickets.txt'):
        return []
    with open('tickets.txt', 'r') as f:
        return json.load(f)

def save_tickets(tickets):
    with open('tickets.txt', 'w') as f:
        json.dump(tickets, f)

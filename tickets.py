from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
import json
import os

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@tickets_bp.route('/api/tickets', methods=['GET', 'POST'])
@login_required
def api_tickets():
    if request.method == 'GET':
        tickets = load_tickets()
        return jsonify(tickets)
    elif request.method == 'POST':
        new_ticket = request.json
        tickets = load_tickets()
        new_ticket['id'] = len(tickets) + 1
        new_ticket['status'] = 'pending'
        tickets.append(new_ticket)
        save_tickets(tickets)
        return jsonify(new_ticket), 201

@tickets_bp.route('/api/tickets/<int:ticket_id>', methods=['PUT', 'DELETE'])
@login_required
def api_ticket(ticket_id):
    tickets = load_tickets()
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    if request.method == 'PUT':
        ticket['status'] = request.json['status']
        save_tickets(tickets)
        return jsonify(ticket)
    elif request.method == 'DELETE':
        tickets = [t for t in tickets if t['id'] != ticket_id]
        save_tickets(tickets)
        return '', 204

@tickets_bp.route('/api/tickets/purge', methods=['POST'])
@login_required
def purge_completed_tickets():
    tickets = load_tickets()
    tickets = [t for t in tickets if t['status'] != 'completed']
    save_tickets(tickets)
    return jsonify({'message': 'Completed tickets purged'}), 200

def load_tickets():
    if not os.path.exists('tickets.txt'):
        return []
    with open('tickets.txt', 'r') as f:
        return json.load(f)

def save_tickets(tickets):
    with open('tickets.txt', 'w') as f:
        json.dump(tickets, f)

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

peer_sid_map = {}

@socketio.on('join')
def on_join(data):
    room = data['room']
    peer_id = data['peer_id']
    sid = request.sid
    peer_sid_map[peer_id] = sid
    join_room(room)
    print(f"Peer {peer_id} joined room {room}")
    emit('peer_joined', {'peer_id': peer_id}, room=room, include_self=False)

@socketio.on('signal')
def on_signal(data):
    to_peer = data.get('to')
    from_peer = data.get('from')
    signal_data = data.get('signal')
    room = data.get('room')

    print(f"Signal from {from_peer} to {to_peer} in room {room}")

    target_sid = peer_sid_map.get(to_peer)
    if target_sid:
        emit('signal', {'from': from_peer, 'signal': signal_data}, to=target_sid)
    else:
        print(f"Warning: target peer {to_peer} not found")

@socketio.on('leave')
def on_leave(data):
    room = data.get('room')
    peer_id = data.get('peer_id')
    sid = request.sid
    peer_sid_map.pop(peer_id, None)
    leave_room(room)
    print(f"Peer {peer_id} left room {room}")
    emit('peer_left', {'peer_id': peer_id}, room=room)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    for pid, psid in list(peer_sid_map.items()):
        if psid == sid:
            peer_sid_map.pop(pid)
            print(f"Peer {pid} disconnected")
            break

def start_server(port, shutdown_event):
    print(f"Launching SocketIO server on port {port}")

    def run_socketio():
        socketio.run(app, host='0.0.0.0', port=port)

    server_thread = threading.Thread(target=run_socketio)
    server_thread.start()

    while not shutdown_event.is_set():
        time.sleep(0.5) 

    print("Server shutdown signal received")

def end_server(port):
    print(f"Stopping SocketIO server on port {port}")
    socketio.stop(app, host='0.0.0.0', port=port)
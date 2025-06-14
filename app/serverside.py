from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('join')
def on_join(data):
    room = data['room']
    peer_id = data['peer_id']
    join_room(room)
    print(f"Peer {peer_id} joined room {room}")
    emit('peer_joined', {'peer_id': peer_id}, room=room, include_self=False)

@socketio.on('signal')
def on_signal(data):
    room = data['room']
    to_peer = data['to']
    signal_data = data['signal']
    print(f"Signal from {data['from']} to {to_peer} in room {room}")
    emit('signal', {'from': data['from'], 'signal': signal_data}, room=room, include_self=False)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    peer_id = data['peer_id']
    leave_room(room)
    print(f"Peer {peer_id} left room {room}")
    emit('peer_left', {'peer_id': peer_id}, room=room)

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
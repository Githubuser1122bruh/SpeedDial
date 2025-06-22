import asyncio
import threading
import numpy as np

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, Qt

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRecorder

import socketio

class VideoLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setFixedSize(640, 480)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Waiting for video")

    def update_image(self, image):
        self.setPixmap(QPixmap.fromImage(image).scaled(self.size(), Qt.KeepAspectRatio))

class VideoStreamReceiver(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, video_label):
        super().__init__()
        self.track = track
        self.video_label = video_label

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)

        def update():
            self.video_label.update_image(qt_image)

        QTimer.singleShot(0, update)
        return frame

class WebRTCClient:
    def __init__(self, video_label, server_url, peer_id, room):
        self.server_url = server_url
        self.peer_id = peer_id
        self.room = room
        self.sio = socketio.Client()
        self.video_label = video_label

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        self.player = MediaPlayer(None, format="avfoundation", options={"framerate": "30", "video_size": "640x480"})
        self.recorder = MediaRecorder('default')

        # map peer_id -> RTCPeerConnection instance
        self.peer_connections = {}

        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('signal', self.on_signal)
        self.sio.on('peer_joined', self.on_peer_joined)
        self.sio.on('peer_left', self.on_peer_left)

    def start(self):
        self.sio.connect(self.server_url)
        self.sio.emit('join', {'peer_id': self.peer_id, 'room': self.room})

    def on_connect(self):
        print("[SocketIO] Connected")

    def on_disconnect(self):
        print("[SocketIO] Disconnected")

    def on_peer_joined(self, data):
        new_peer_id = data['peer_id']
        print(f"Peer joined: {new_peer_id}")
        if new_peer_id == self.peer_id:
            return  # ignore self

        # create new RTCPeerConnection for this peer
        pc = RTCPeerConnection()
        self.peer_connections[new_peer_id] = pc

        # add local tracks to pc
        if self.player.video:
            pc.addTrack(self.player.video)
        if self.player.audio:
            pc.addTrack(self.player.audio)

        # handle incoming tracks from this peer
        @pc.on("track")
        async def on_track(track):
            print(f"Track received from {new_peer_id}: {track.kind}")
            if track.kind == "video":
                receiver = VideoStreamReceiver(track, self.video_label)
                pc.addTrack(receiver)
            elif track.kind == "audio":
                await self.recorder.addTrack(track)
                await self.recorder.start()

        # create and send offer to new peer
        asyncio.run_coroutine_threadsafe(self._send_offer(new_peer_id, pc), self.loop)

    def on_peer_left(self, data):
        leaving_peer = data['peer_id']
        print(f"Peer left: {leaving_peer}")
        pc = self.peer_connections.pop(leaving_peer, None)
        if pc:
            asyncio.run_coroutine_threadsafe(pc.close(), self.loop)

    def on_signal(self, data):
        from_peer = data['from']
        signal = data['signal']

        # ignore signals from self or unknown peer connections
        if from_peer == self.peer_id:
            return

        pc = self.peer_connections.get(from_peer)
        if not pc:
            print(f"Received signal from unknown peer {from_peer}, creating pc...")
            pc = RTCPeerConnection()
            self.peer_connections[from_peer] = pc

            # add local tracks and track handlers (same as on_peer_joined)
            if self.player.video:
                pc.addTrack(self.player.video)
            if self.player.audio:
                pc.addTrack(self.player.audio)

            @pc.on("track")
            async def on_track(track):
                print(f"Track received from {from_peer}: {track.kind}")
                if track.kind == "video":
                    receiver = VideoStreamReceiver(track, self.video_label)
                    pc.addTrack(receiver)
                elif track.kind == "audio":
                    await self.recorder.addTrack(track)
                    await self.recorder.start()

        asyncio.run_coroutine_threadsafe(self._handle_signal(pc, signal, from_peer), self.loop)

    async def _handle_signal(self, pc, signal, from_peer):
        if signal['type'] == 'offer':
            await pc.setRemoteDescription(RTCSessionDescription(signal['sdp'], signal['type']))
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            self.sio.emit('signal', {
                'room': self.room,
                'from': self.peer_id,
                'to': from_peer,
                'signal': {'type': 'answer', 'sdp': pc.localDescription.sdp}
            })
        elif signal['type'] == 'answer':
            await pc.setRemoteDescription(RTCSessionDescription(signal['sdp'], signal['type']))
        elif signal['type'] == 'candidate':
            candidate = signal['candidate']
            await pc.addIceCandidate(candidate)

    async def _send_offer(self, to_peer, pc):
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        self.sio.emit('signal', {
            'room': self.room,
            'from': self.peer_id,
            'to': to_peer,
            'signal': {'type': 'offer', 'sdp': pc.localDescription.sdp}
        })
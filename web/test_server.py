#!/usr/bin/env python3
import sys
import os
import signal

# Ignore SIGHUP
signal.signal(signal.SIGHUP, signal.SIG_IGN)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'OK from test server'

@app.route('/test')
def test():
    return 'TEST WORKS'

if __name__ == '__main__':
    import sys
    if '--unix' in sys.argv:
        # Use Unix socket
        import werkzeug.serving
        sock_path = '/tmp/flask_test.sock'
        if os.path.exists(sock_path):
            os.unlink(sock_path)
        print(f"Starting on Unix socket {sock_path}...", flush=True)
        srv = werkzeug.serving.make_server('localhost', 0, app, threaded=True)
        import socket
        srv.socket.close()
        srv.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.socket.bind(sock_path)
        srv.socket.listen(128)
        os.chmod(sock_path, 0o777)
        print(f"Listening on {sock_path}", flush=True)
        srv.serve_forever()
    else:
        print("Starting test server on 0.0.0.0:7220...", flush=True)
        app.run(host='0.0.0.0', port=7220, debug=False, use_reloader=False, threaded=True)

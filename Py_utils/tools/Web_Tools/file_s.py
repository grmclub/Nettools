import http.server
import socketserver
import os

# CONFIGURATION
PORT = 8000
# Leave empty "" for the current folder, or provide an absolute path like "C:/SharedFiles"
DIRECTORY = "" 

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the root directory for the file server
        if DIRECTORY:
            super().__init__(*args, directory=DIRECTORY, **kwargs)
        else:
            super().__init__(*args, **kwargs)

def start_server():
    # Allow restarting the server immediately without "address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        current_dir = DIRECTORY if DIRECTORY else os.getcwd()
        print(f"==================================================")
        print(f" Serving files from: {current_dir}")
        print(f" Local URL:          http://localhost:{PORT}")
        print(f" Press CTRL+C to stop the server safely.")
        print(f"==================================================")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n Shutting down the server safely...")
            httpd.shutdown()

if __name__ == "__main__":
    start_server()

import os
from bottle import route, run, request, template

# Define the folder where files will be saved
UPLOAD_DIR = "./uploads"

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@route('/upload', method='GET')
def upload_form():
    """Serves a simple HTML form to the user."""
    return '''
        <!DOCTYPE html>
        <html>
        <head><title>File Upload</title></head>
        <body>
            <h2>Upload a File</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <label for="file_upload">Select file:</label>
                <input type="file" id="file_upload" name="upload" required />
                <br><br>
                <input type="submit" value="Start Upload" />
            </form>
        </body>
        </html>
    '''

@route('/upload', method='POST')
def do_upload():
    """Handles the file upload logic."""
    # Retrieve the file from the form data using the input name attribute ('upload')
    upload_file = request.files.get('upload')
    
    if not upload_file:
        return "No file was selected for upload."

    # The .filename property automatically sanitizes the client-side filename
    filename = upload_file.filename
    
    # Save the file securely using Bottle's built-in save method
    # Setting overwrite=True replaces an existing file with the same name
    upload_file.save(UPLOAD_DIR, overwrite=True)
    
    return f"Success! File '{filename}' was uploaded to '{UPLOAD_DIR}'."

if __name__ == '__main__':
    # Start the local development server
    run(host='localhost', port=8080, debug=True, reloader=True)
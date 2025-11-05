from app import app

# Gunicorn will look for the 'app' object in this file (or directly in app.py)
# This file simply imports the Flask app instance from your main app.py file.

if __name__ == "__main__":
    # This part is typically not run by Gunicorn but can be useful
    # for certain local testing scenarios or alternative WSGI servers.
    # For standard Gunicorn/Render usage, it often does nothing.
    # You might even see just the 'from app import app' line in many wsgi.py files.
    pass
    # If you wanted to run using Python directly (like `python wsgi.py`)
    # you might put app.run() here, but that's not the Render/Gunicorn way.
    # app.run() # Generally not needed here for Gunicorn deployment
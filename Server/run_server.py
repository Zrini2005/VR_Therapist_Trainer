import sys
import os

# Change to the Server directory
server_dir = r"c:\Users\srini\Downloads\VR-Therapist-Virtual-Mental-Health-Experience\Server"
os.chdir(server_dir)
sys.path.insert(0, server_dir)

# Now run the app
exec(open('app.py').read())

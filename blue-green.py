from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess
import re
import signal
import time

# blue = 4001
# green = 4002

def check_nginx_port_in_config():
    nginx_conf_path = '/etc/nginx/nginx.conf'
    
    try:
        # Open and read the nginx.conf file
        with open(nginx_conf_path, 'r') as file:
            config_data = file.read()
        
        # Check if the string "40012" exists in the file
        if '4001' in config_data:
            return "green"
            #print("The string '4001' is found in the nginx.conf.")
            #return True
        else:
            return "blue"
            #print("The string '4001' is not found in the nginx.conf.")
            #return False
    except FileNotFoundError:
        print(f"Error: The file {nginx_conf_path} does not exist.")
        return "green"
    except PermissionError:
        print(f"Error: Permission denied when trying to open {nginx_conf_path}.")
        return "green"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "green"

def update_nginx_and_run_deno():
    try:
        next_deployment = check_nginx_port_in_config()
        next_port = 4002 if next_deployment == "green" else 4001
        print(f"next_deployment {next_deployment}")

        nginx_conf = '/etc/nginx/nginx.conf'
        if not os.path.exists(nginx_conf):
            print(f"Nginx configuration file {nginx_conf} not found.")
            return

        # Step 1: Find the PID of the "deno" process
        pid = None
        result = subprocess.run(['pgrep', 'deno'], capture_output=True, text=True)
        if result.returncode == 0:
            pid = result.stdout.strip()
            print(f"Found Deno process with PID: {pid}")
        else:
            pid = None
            print("No Deno process found.")

        # Step 2: Run the deno command in the "green" subdirectory
        #deployment_dir = 'green'
        if not os.path.isdir(next_deployment):
            print(f"The subdirectory {next_deployment} does not exist.")
            return

        os.chdir(next_deployment)

        print(os.getcwd())

        print("Running Deno build command...")
        #subprocess.run(['deno', 'task', 'build'])
        subprocess.Popen(['deno', 'run', '-A', 'main.ts', 'build'], env=dict(os.environ, **{"PORT":f"{next_port}"}))

        time.sleep(3)
        # Step 3: Modify nginx.conf to replace port 4001 with 4002
        with open(nginx_conf, 'r') as file:
            config_data = file.read()

        # Replace port 4001 with 4002 in nginx.conf
        # updated_config = re.sub(r'8000', '4002', config_data)
        if next_deployment == "green":
            updated_config = re.sub(r'4001', '4002', config_data)
            print("Updated nginx.conf to replace port 4001 with 4002.")
        else:
            updated_config = re.sub(r'4002', '4001', config_data)
            print("Updated nginx.conf to replace port 4002 with 4001.")

        try:
            with open(nginx_conf, 'w') as file:
                file.write(updated_config)
        except PermissionError:
            print("Permission error")

        os.chdir("..")

        # Step 4: Reload the Nginx configuration
        subprocess.run(['nginx', '-s', 'reload'], check=True)
        print("Nginx configuration reloaded.")

        # Step 5: Kill the Deno process using the PID
        if pid:
            os.kill(int(pid), signal.SIGTERM)
            print(f"Terminated Deno process with PID: {pid}")

    except subprocess.CalledProcessError as e:
        print(f"Error during subprocess execution: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Check if the requested path is '/'
        if self.path == '/':
            # Send a 200 OK response
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            # Send the response text "blue-green"

            self.wfile.write(b"blue-green")
        else:
            # For other paths, return a 404 Not Found response
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=RequestHandler, port=4003):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    update_nginx_and_run_deno()
    #run()
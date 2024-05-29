import os
import subprocess
import json
import mysql.connector


def get_terraform_output():
    try:
        # Get the current directory of the script
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Navigate up to the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_directory)))

        # Construct the path to the terraform directory
        
        terraform_dir = os.path.join(project_root, 'terraform')

        os.chdir(terraform_dir)
        # Run terraform output command and capture the result
        result = subprocess.run(["terraform", "output", "-json"], capture_output=True, text=True, check=True)

        # Parse the JSON output
        output_json = json.loads(result.stdout)

        # Return the parsed output
        return output_json

    except subprocess.CalledProcessError as e:
        print("Error executing Terraform command:", e)
        return None
def get_jwt_details():
    output = get_terraform_output()
    if output:
        jwt_details = output.get("access_token_details", {}).get("value", {})
        if jwt_details:
            return jwt_details
        else:
            print("Failed to retrieve details.")
    else:
        print("Failed to retrieve Terraform output.")

def get_data_features(feature):
    output = get_terraform_output()
    if output:
        features = output.get(feature, {}).get("value", {})
        if features:
            return features
        else:
            print("Failed to retrieve details.")
    else:
        print("Failed to retrieve Terraform output.")



def create_mysql_connection():
    output = get_terraform_output()
    if output:
        mysql_connection_details = output.get("mysql_connection_details", {}).get("value", {})
        if mysql_connection_details:
            try:
        # Create MySQL connection
                conn = mysql.connector.connect(
                    host=mysql_connection_details.get("host"),
                    port=mysql_connection_details.get("port"),
                    user=mysql_connection_details.get("username"),
                    password=mysql_connection_details.get("password"),
                    database=mysql_connection_details.get("database")
                )
                
                return conn

            except Exception as e:
                print("Error connecting to MySQL:", e)
                return None
            
            
    else:
        print("Failed to retrieve Terraform output.")

    



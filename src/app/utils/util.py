import os
import subprocess
import json
import mysql.connector


def get_terraform_output():
    try:
        terraform_dir="/home/wangui/Documents/projects/AI-Navigator/terraform"

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

    



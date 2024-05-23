# AI-Navigator
DataBot is an innovative chatbot designed to assist users with data analysis tasks. Leveraging natural language processing (NLP) and machine learning technologies, DataBot provides an intuitive interface for users to interact with their data, perform analyses, and gain insights effortlessly.

# Installation
To set up and install this project, proceed with the following steps::
* Clone the project
* Navigate to the installation directory
## Terraform Setup
Terraform is a tool for building, changing, and versioning infrastructure safely and efficiently. In this project, Terraform is used to manage the infrastructure needed for deployment, such as provisioning cloud resources.

To set up Terraform for this project, follow these steps:
### Navigate to the terraform folder
```
cd terraform
```
### Create varibales.tf and secrets.tfvars files in the terraform directory
```
touch variables.tf
touch secrets.tfvars
```
These files will contain the necessary variables used by Terraform to provision resources.

Populate the variables.tf file with the appropriate variables and values. These variables define the configuration for the infrastructure resources that Terraform will provision.

Populate the secrets.tfvars file with sensitive information such as access keys or passwords. Ensure that this file is not shared or committed to version control.

### Initialize terraform 
```
terraform init
```
### Apply Terraform configurations using the secrets.tfvars file
```
terraform apply -var-file="secrets.tfvars"
```
This command will execute the Terraform configuration and provision the specified infrastructure resources based on the variables and settings provided.

## Running Locally 
If running locally, follow these steps:
* Install the dependencies listed in the requirements.txt
``` 
pip install -r requirements.txt
```
* Run the main script
``` 
python main.py
```
## If running docker container
* Build Docker image
``` 
docker build -t databot .
```

* Run Docker container
``` 
docker run -p 8000:8000 databot
```
## Authentication

Authentication is a crucial aspect of the DataBot project, ensuring that only authorized users can access certain functionalities and data. The project utilizes OAuth2 for user authentication, which provides a secure and standardized way for clients to obtain access to protected resources on the server.

### OAuth2 Scheme

The project defines an OAuth2 password bearer scheme using FastAPI's `OAuth2PasswordBearer` class. This scheme allows clients to obtain access tokens by providing their username and password via a POST request to the `/token` endpoint.

### Password Hashing

To ensure the security of user credentials, passwords are hashed using the bcrypt hashing algorithm before being stored in the database. Password hashing prevents plaintext passwords from being exposed in the event of a data breach, enhancing the overall security of the system.

### Authentication Workflow

The authentication workflow in the DataBot project can be summarized as follows:

1. **Login Endpoint (`/token`):** Clients send a POST request to the `/token` endpoint with their username and password credentials encoded in the request body. The server verifies the credentials, generates an access token using JWT (JSON Web Tokens), and returns it to the client.

2. **Access Token:** The access token is a JSON Web Token that contains information about the user and an expiration time. Clients include the access token in the `Authorization` header of subsequent requests to protected endpoints.

3. **Token Verification:** When a client sends a request to a protected endpoint, the server verifies the access token to ensure its authenticity and validity. If the token is valid and not expired, the server grants access to the requested resource. Otherwise, it returns an authentication error.

### Token Expiry and Renewal

Access tokens issued by the server have a limited lifespan to mitigate the risk of unauthorized access. Tokens expire after a specified period (e.g., 15 minutes), after which clients must obtain a new token by re-authenticating with their credentials.

### Secure Communication

All communication between clients and the server is secured using HTTPS (HTTP over SSL/TLS) to encrypt data transmission and protect against eavesdropping and man-in-the-middle attacks.

By implementing OAuth2-based authentication and password hashing, the DataBot project ensures the confidentiality, integrity, and authenticity of user authentication, safeguarding sensitive data and resources from unauthorized access.

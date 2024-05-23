
terraform {
  required_providers {
    mysql = {
      source  = "terraform-providers/mysql"
      # Optionally specify the version if needed
      # version = "x.x.x"
    }
  }
}

provider "mysql" {
  endpoint = "${var.mysql_host}:${var.mysql_port}"
  username = var.mysql_username
  password = var.mysql_password
}

output "mysql_connection_details" {
  value = {
    host     = var.mysql_host
    port     = var.mysql_port
    username = var.mysql_username
    password = var.mysql_password
    database = var.mysql_database_name
  }
}

output "access_token_details" {
  value = {
    secret_key="Trinidad96"
    algorithm= "HS256"
    access_token_expire_minutes = 5
  }

}



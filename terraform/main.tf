
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
    secret_key=var.access_token_key
    algorithm= var.access_token_algorithm
    access_token_expire_minutes = var.access_token_expire_minutes
  }
}

output "categorical_features" {
  value = var.categorical_features
}

output "time_features" {
  value = var.time_features
}

output "numerical_features" {
  value = var.numerical_features
}



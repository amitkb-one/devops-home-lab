output "container_id" {
  description = "ID of the created Docker container"
  value       = docker_container.nginx.id
}

output "container_name" {
  description = "Name of the created Docker container"
  value       = docker_container.nginx.name
}

output "application_url" {
  description = "Local URL of the Nginx service"
  value       = "http://localhost:${var.external_port}"
}

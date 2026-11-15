
variable "container_name" {
  description = "Name of the Nginx container"
  type        = string
}

variable "image_name" {
  description = "Docker image to deploy"
  type        = string
  default     = "nginx:alpine"
}

variable "external_port" {
  description = "Host port for Nginx"
  type        = number

  validation {
    condition     = var.external_port >= 1024 && var.external_port <= 65535
    error_message = "Port must be between 1024 and 65535."
  }
}

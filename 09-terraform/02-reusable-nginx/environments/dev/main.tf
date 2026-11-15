terraform {
  required_version = ">= 1.5.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

module "nginx" {
  source = "../../modules/nginx"

  container_name = "terraform-nginx-dev"
  image_name     = "nginx:alpine"
  external_port  = 8085
}

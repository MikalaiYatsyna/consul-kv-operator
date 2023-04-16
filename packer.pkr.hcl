packer {
  required_plugins {
    docker = {
      version = ">= 0.0.7"
      source  = "github.com/hashicorp/docker"
    }
  }
}

source "docker" "python" {
  image       = var.python_image
  run_command = ["-d", "-i", "-t", "--entrypoint=/bin/bash", "{{ .Image }}"]
  commit      = true
  changes     = [
    "ENTRYPOINT . /opt/venv/bin/activate && kopf run main.py"
  ]
}

build {
  sources = ["source.docker.python"]

  provisioner "file" {
    source      = "src/requirements.txt"
    destination = "requirements.txt"
  }

  provisioner "file" {
    source      = "src/main.py"
    destination = "main.py"
  }

  provisioner "shell" {
    inline = ["python3 -m venv /opt/venv && . /opt/venv/bin/activate && pip3 install -r requirements.txt --upgrade pip"]
  }

  post-processors {
    post-processor "docker-tag" {
      repository = var.ecr_url
      tag        = [var.image_tag]
    }

    post-processor "docker-push" {
      ecr_login = true
      login_server = "https://${var.ecr_url}"
    }
  }
}



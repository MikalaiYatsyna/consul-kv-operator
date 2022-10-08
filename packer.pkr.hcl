packer {
  required_plugins {
    docker = {
      version = ">= 0.0.7"
      source  = "github.com/hashicorp/docker"
    }
  }
}

source "docker" "python" {
  image = "${var.python_image}"
  commit = true
    changes = [
        "ENTRYPOINT kopf run /operator.py"
    ]
}

build {
  sources = ["source.docker.python"]

  provisioner "file" {
    source      = "operator.py"
    destination = "/"
  }
  provisioner "shell" {
    inline = [
      "pip install --upgrade pip && pip install --no-cache-dir kopf kubernetes consulate ruamel.yaml"
    ]
  }

  post-processors {
    post-processor "docker-tag" {
      repository = "${var.image_name}"
      tag        = ["${var.image_tag}"]
    }
  }
}



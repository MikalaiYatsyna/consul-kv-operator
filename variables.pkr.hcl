variable "python_image" {
  type    = string
  default = "python:slim"
}

variable "image_name" {
  type    = string
  default = "consul-kv-operator"
}

variable "image_tag" {
  type = string
}

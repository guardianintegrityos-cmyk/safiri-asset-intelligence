provider "aws" {
  region = "us-east-1"
}

resource "aws_db_instance" "safiri_kenya_primary" {
  allocated_storage    = 50
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.m6g.large"
  name                 = "safiri_kenya"
  username             = "safiri"
  password             = var.db_password
  multi_az             = true
  storage_type         = "gp3"
  backup_retention_period = 7
}

resource "aws_db_instance" "safiri_kenya_replica" {
  replicate_source_db  = aws_db_instance.safiri_kenya_primary.id
  instance_class       = "db.m6g.large"
  multi_az             = true
}

resource "aws_elasticsearch_domain" "safiri_es" {
  domain_name           = "safiri-assets"
  elasticsearch_version = "8.13"

  cluster_config {
    instance_type  = "r6g.large.elasticsearch"
    instance_count = 3
    zone_awareness_enabled = true
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 50
    volume_type = "gp3"
  }

  node_to_node_encryption {
    enabled = true
  }

  encrypt_at_rest {
    enabled = true
  }
}

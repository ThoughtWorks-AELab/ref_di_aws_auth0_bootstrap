terraform {
  required_version = ">= 0.9.1"

  backend "s3" {}
}

provider "aws" {
  region = "${var.aws_region}"
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "instance-assume-role-policy" {
  statement {
    actions = ["sts:AssumeRoleWithSAML"]

    principals {
      type        = "Federated"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:saml-provider/auth0-preproduction"]
    }

    condition {
      test     = "ForAnyValue:StringLike"
      variable = "SAML:aud"
      values   = ["https://signin.aws.amazon.com/saml", "urn:dps-reference-implementation.auth0.com"]
    }
  }
}

resource "aws_iam_policy" "power_user_policy" {
  name = "power_user"
  policy = "${file("${path.module}/policies/poweruser.json")}"
}

resource "aws_iam_policy" "readonly_policy" {
  name = "readonly"
  policy = "${file("${path.module}/policies/readonly.json")}"
}

resource "aws_iam_role" "dev_admin" {
  name               = "dev_admin"
  assume_role_policy = "${data.aws_iam_policy_document.instance-assume-role-policy.json}"
}

resource "aws_iam_role" "infra_reader" {
  name               = "infra_reader"
  assume_role_policy = "${data.aws_iam_policy_document.instance-assume-role-policy.json}"
}

# Assign policies to roles per environment

resource "aws_iam_policy_attachment" "power_user_attachments" {
  name      = "poweruser"
  roles      = ["${var.power_user_roles}"]
  policy_arn = "${aws_iam_policy.power_user_policy.arn}"
}

resource "aws_iam_policy_attachment" "read_only_attachments" {
  name      = "readonly"
  roles      = ["${var.readonly_roles}"]
  policy_arn = "${aws_iam_policy.readonly_policy.arn}"
}


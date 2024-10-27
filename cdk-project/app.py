#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_project.cdk_project_stack import CdkProjectStack


app = cdk.App()
CdkProjectStack(app, "aws-hello-api", stack_name="hello-api")

app.synth()

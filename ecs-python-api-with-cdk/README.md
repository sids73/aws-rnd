# ECS Python API with CDK

This project demonstrates how to deploy a Python API using AWS ECS and AWS CDK.

## Project Structure

- **cdk-project/**: Contains AWS CDK infrastructure code.
- **hello-api/**: Contains the Python API source code.
- **hello-api/Dockerfile**: Defines the Docker image for the Python API.
- **README.md**: Project documentation.

## Prerequisites

- AWS CLI
- AWS CDK
- Docker
- Python 3.8+

## Setup

1. **Install dependencies**:
   Do this with both the requirements.txt files, one in hello-api/ and one in cdk-project
   Tip: Instantiate a Python virtual environment first before installing any requirements.txt
        to prevent polluting your global python environment
    ```bash
    pip install -r requirements.txt
    ```
2. **Test hello-api python code**
    Try running the server.py file in your IDE or Terminal locally to make sure that the api 
    actually works. Test the healthcheck URL http://localhost:8000/hello/health as well as the
    hello url http:localhost:8000/hello/coder, returns JSON string Hello Coder! through
    a browser, CURL, http-pie or postman. Fix any issues until the code runs fine
3. **Build Docker image**:
    Build Docker image locally to ensure that Dockerfile Docker script in the hello-api folder is okay
    ```bash
    docker build -t ecs-python-api .
    ```
    This will create a Docker image. Run the image as a container on your local Docker, expose port 8000
    and test as explained in step #2. Tweak Dockerfile until the container tests okay.
3. **Deploy infrastructure**:
    To make sure that your cdk code is correct first
    ```bash
    cdk synth
    ```
    Make sure that there are not CloudFormation template creation errors or deprecated code warnings.
    If any errors or warnings, fix and synth again until no warnings or errors.
    Deploy to AWS. Ensure that the AWS CLI can connect to AWS with your account/IAM user first!
    ```bash
    cdk deploy --all --require-approval never
    ```
    --all:

    This flag tells the CDK to deploy all stacks defined in your CDK application. Without this flag, you would need to specify the stack names individually.
    
    --require-approval never:

    This flag disables the approval prompt that usually appears when deploying stacks that might make security-sensitive changes (like creating IAM roles or policies). 
    By setting it to never, you are instructing CDK to proceed without asking for any manual approvals. This is useful in CI/CD pipelines where manual prompting
    and waiting for human intervention is not desired



## Usage

- Access the API endpoint provided after deployment.
- Monitor the ECS service via the AWS Management Console.

## Cleanup

- Destroy the CDK stack to prevent unnecessary AWS charges:
    ```bash
    cdk destroy --all
    ```

## License

This project is licensed under the MIT License.
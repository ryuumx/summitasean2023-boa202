
# Accelerate modern application development with Serverless
 
This is a project built to demonstrate how you can accelerate your modern application development with AWS Serverless tools and services


## 1. Requirements

  * [Python >= 3.9](https://www.python.org/downloads/)
  * [AWS CDK 2.67.0](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)
  * Setup your AWS credentials
  * If you haven't, run CDK bootstrap of your AWS account:

  ```
  $ cdk bootstrap
  ```


## 2. Architecture

### 2.1. Basic flow (*main* branch)
![Basic flow architecture](/docs/main.png "Basic flow architecture")

### 2.2. Advanced flow (*advanced* branch)
![Advanced flow architecture](/docs/advanced.png "Advanced flow architecture")


## 3. Development from scratch

Initialize the CDK project
```
$ cdk init app --language python
```


## 4. Deployment

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

Deploy to your account

```
$ cdk deploy
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation


## 5. 

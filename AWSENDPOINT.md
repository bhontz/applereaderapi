## Hosting the Icebreaker API with Amazon's AWS Lambda Service 

In the README of this repo I mention how to test this API illustration using
localhost and how to temporarily expose it to the internet (and so Thunkable
can connect to it) using NGROK.  There are several "permanent" cloud solutions
for hosting API's like Google Cloud Run, Heroku, Microsoft's Azure Cloud, and
as we will illustrate here, Amazon AWS's Lambda service.   We can use one of
these services to create a permanent API endpoint that can be referenced by
anyone using a Thunkable WebAPI block.

### Create an AWS Account

You'll need to create a AWS account in order to proceed.   As of this writing
(and for several years before) AWS has provided a FREE TIER which will work just
fine, although do note that you'll have to provide a payment method even when
signing up for the free tier.  

From personal experience, I am currently paying less than $1 a month to host a
few gigs of storage for old company records I wish to keep around.  In other
words, don't be too concerned with providing your payment method as you only
pay for what you use, and if you are following along here for the purposes of
creating an API for a seasonal app challenge, you will likely pay either
nothing (under Amazon's free 12-month trial), or next to nothing based on
likely usage for this Thunkable app challenge example.  

There are plenty of resources to follow for creating an AWS account, [here's
an example](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/).   

Ultimately, you will be creating AWS credentials
consisting of an AWS_ACCESS_KEY_ID and an AWS_SECRET_ACCESS_KEY.  I am using a
Mac OSx system and these two keys are stored within the file ~/.aws/credentials.  A similar
and separate file ~/.aws/config, contains two keys, output and region; for
example:

    [default]
    output = json
    region = us-east-2

On a Windows machine, these two credential files should be stored within an
aws folder beneath your home (see your %UserProfile% environment variable)
folder.

### Changes required to the Icebreaker Python project

Within this repo's module app.py, change the last line from:

    app.run(debug=True, host='127.0.0.1', port=8080)

… to:

    app.run()

We will use the [python module zappa](https://github.com/Miserlou/Zappa) to
simplify the creation of an AWS lambda API endpoint.  The zappa process will
create a "package" of all the modules within our machine's python environment,
so it's essential that you create a virtual environment specific to this
project in order to limit the modules packaged to the python modules associated with this
project.

### Create a virtual environment for this project

Fortunately, it's very easy to create a virtual environment for each one of
your python projects, and it's additionally a "best practice" to follow.

From your terminal (or command prompt), change into your projects folder and execute
the following:

    $ python3 -m venv env

This will create the folder env beneath your project folder.  Next, start the
virtual environment using the command:

    $ source env/bin/activate

You will note your terminal (command prompt) prompt will change as an
indication that you are now working within the virtual environment.

If you "cloned" this project from github, you'll note the use of
requirements.txt file which contains the python modules this project requires.
To install the requirements within your new virtual environment, use pip as
shown here:

    (env) $ pip install -r requirements.txt

You'll also need to install the zappa module, which you can do as follows:

    (env) $ pip install zappa

Now you can run zappa from your terminal (command prompt) and follow along
with the prompted questions, **confirming each of the default selections as
you are prompted.**

    (env) user:icebreaker$ zappa init

You'll note towards the end of the output of this step:


    Done! Now you can deploy your Zappa application by executing:
        $ zappa deploy dev

You note here I'd used the default "dev" project as part of the
"zappa init" step.  Now we just need to:

    (env) $ zappa deploy dev

… which will deploy the app on AWS and return the equivalent of:

    Deploying API Gateway..
    Deployment complete: https://fdalfkjda.execute-us-east-2.amazon.aws.com/dev

Your URL endpoint will of course be different than the example above, but I'll
continue to use this fictional URL throughout the remainder of this document.

Just as within this repo's README, we can obtain the count of the name X 
icebreaker combinations from Thunkable by pointing our WebAPI block to:

    https://fdalfkjda.execute-us-east-2.amazon.aws.com/dev/count

… which will determine the range of our random item selection when we call the question endpoint as follows:

    https://fdalfkjda.execute-us-east-2.amazon.aws.com/dev/question?item=1

The item parameter's value of "1" is an illustration; your Thunkable app will substitute the
value of 1 with a random value between 0 and the count we obtained by visiting
the "count" endpoint.

Good luck with your own implementation!




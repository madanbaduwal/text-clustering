Data Download from AWS
======================
We have provide data into aws instance we need to download data

1. Amazon console

Console login link: https://851797349069.signin.aws.amazon.com/console

User Name : madan@fusemachines.com

Password : Tesla@123

2. Ip of EC2 Instance in which data is contain

`34.235.222.35`

3. Connect this ip from local

I personally like to connect with the help of ssh , you need to install ssh in your local machine.

`ssh -i .\dev_us_east_1.pem ubuntu@ec2-34-235-222-35.compute-1.amazonaws.com`

4. To download and upload data into EC2 

To download and upload data into EC2 we need scp 

`scp -i dev_us_east_1.pem -r ubuntu@ec2-34-235-222-35.compute-1.amazonaws.com:/home/ubuntu/Training_Ursula_Overall/ .`

* r is for download folder
* TO upload we need to swap the location of folder in command 
# cse546-project3

## Cloud Computing Project 3

### Group: CCP

#### Team Members

| Name  | ASU ID  |
|---|---|
| Gaurav Kulkarni  |  1225477253 |
| Parth Shah | 1225457038 |
| Shreyas Kirtane | 1225453736 |

-----

> [Project Report](https://drive.google.com/file/d/1R3JobhemUxeN-MtCeG033-SPEk1DUwf4/view?usp=sharing)

-----

#### AWS Credentials

* Account ID: 583586231865
* user: demo

-----

#### S3

* input bucket: cse546proj3-input
* resuls bucket: cse546proj3-output

------
#### EventBridge

* event - s3event

------

## Installing and Deploying the hybrid cloud Infrastructure
1.	Clone the devstack project
git clone https://opendev.org/openstack/devstack
2.	Copy the sample configuration file from samples directory to current directory and change the passwords
```
cp samples.conf/local.conf .
```
3.	Make the stack script executable and run it - ```./stack.sh```

4.	Configure the network to connect to the public internet
```
openstack subnet set --dhcp external-subnet
openstack subnet set --dhcp test-subnet
openstack subnet set --dns-nameserver 8.8.8.8 external-subnet
openstack subnet set --dns-nameserver 8.8.8.8 test-subnet
openstack network set --share external
openstack network set --share test
```
5.	Add iptables rules for routing and enable IP forwarding on host OS
```
sudo iptables -t nat -A POSTROUTING -s 10.20.20.1/24 ! -d 10.20.20.1/24  MASQUERADE
sudo sysctl net.ipv4.ip_forward=1
```
6.	Using the Horizon Dashboard, upload a server image of Ubuntu 22.04
7.	Set up a public/private Keypair for additional security via Horizon
8.	Launch a new VM instance using Nova and boot it with the disk image
9.	SSH into the newly create instance using the Key Pair 
10.	Set up a Security Group for the VM instance to allow ingress for SSH (TCP port 22) as well as HTTP port 12500 (our server is running on this port)
11.	Clone the project repository onto the VM
git clone https://github.com/skirtan1/cse546-proj3 (This is a private repository)
12.	Deploy the Golang server using the main.go file (Make sure golang is installed) (The server will run on port 12500 by default)
```
go run main.go
```
13.	Expose the local server running on Openstack via ngrok
```
ngrok http 12500
```
14.	Log into the aws console using the credentials provided in the Readme file of the git repositoty and access the dashboard for AWS Eventbridge 
15.	Copy the ngrok URL and paste it into the following path -  
AWS Eventbridge -> Rules -> select s3event -> Targets -> API destinations
16.	We can then run the workload file with cse546proj3-input and cse546proj3-output as the input and output S3 buckets respectively


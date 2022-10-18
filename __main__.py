from pulumi import export
import pulumi_aws as aws

vpc = aws.ec2.Vpc(
	"ec2-vpc",
	cidr_block="10.0.0.0/16"
)

public_subnet = aws.ec2.Subnet(
	"ec2-public-subnet",
	cidr_block="10.0.101.0/24",
	tags={
		"Name": "ec2-public"
	},
	vpc_id=vpc.id
)

igw = aws.ec2.InternetGateway(
	"ec2-igw",
	vpc_id=vpc.id,
)

route_table = aws.ec2.RouteTable(
	"ec2-route-table",
	vpc_id=vpc.id,
	routes=[
		{
			"cidr_block": "0.0.0.0/0",
			"gateway_id": igw.id
		}
	]
)

rt_assoc = aws.ec2.RouteTableAssociation(
	"ec2-rta",
	route_table_id=route_table.id,
	subnet_id=public_subnet.id
)

sg = aws.ec2.SecurityGroup(
	"ec2-http-sg",
	description="Allow HTTP traffic to EC2 instance",
	ingress=[{
		"protocol": "tcp",
		"from_port": 80,
		"to_port": 80,
		"cidr_blocks": ["0.0.0.0/0"],
	}],
    vpc_id=vpc.id,
)

ami = aws.ec2.get_ami(
	most_recent="true",
	owners=["amazon"],
	filters=[{"name": "name", "values": ["amzn-ami-hvm-*"]}]
)


user_data = """
#!/bin/bash
echo "Hello, world!" > index.html
nohup python -m SimpleHTTPServer 80 &
"""

ec2_instance = aws.ec2.Instance(
	"ec2-tutorial",
	instance_type="t2.micro",
	vpc_security_group_ids=[sg.id],
	ami=ami.id,
	user_data=user_data,
    subnet_id=public_subnet.id,
    associate_public_ip_address=True,
)

export("ec2-public-ip", ec2_instance.public_ip)

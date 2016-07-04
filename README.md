python script for lambda to backup all instances tagged with "autobackup" tag. It will also clean old images and keep a number of copies equal to "autobackup" value

just upload the function to lambda, set a daily event source and set lambda_function.lambda_handler as handler. Also make sure the role has ec2 permissions to read ebs disks, make and delete snapshots

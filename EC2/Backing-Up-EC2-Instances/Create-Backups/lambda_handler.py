import boto3
from datetime import datetime

def create_snapshots(region):
    ec2 = boto3.resource('ec2', region_name=region)

    instances = ec2.instances.filter(
        Filters=[
            {'Name': 'tag:backup', 'Values': ['true']}
        ]
    )

    timestamp = datetime.utcnow().replace(microsecond=0).isoformat()
    snapshots_created = []

    for instance in instances.all():
        for volume in instance.volumes.all():
            description = f'Backup of {instance.id}, volume {volume.id}, created {timestamp}'
            print(description)

            snapshot = volume.create_snapshot(Description=description)
            snapshots_created.append(snapshot.id)

    return snapshots_created

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    all_snapshots_created = []

    for region in regions:
        print(f'Instances in EC2 Region {region}:')
        snapshots_created = create_snapshots(region)
        all_snapshots_created.extend(snapshots_created)

    print('All snapshots created:', all_snapshots_created)

if __name__ == "__main__":
    lambda_handler(None, None)  # For local testing if needed

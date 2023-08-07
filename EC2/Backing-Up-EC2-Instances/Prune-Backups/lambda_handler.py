import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_old_snapshots(ec2_client, account_id):
    response = ec2_client.describe_snapshots(OwnerIds=[account_id])
    snapshots = response["Snapshots"]
    snapshots.sort(key=lambda x: x["StartTime"])
    return snapshots[:-5]  # Keep a minimum of 5 snapshots

def delete_snapshots(ec2_client, snapshots):
    for snapshot in snapshots:
        snapshot_id = snapshot['SnapshotId']
        try:
            logger.info("Deleting snapshot: %s", snapshot_id)
            ec2_client.delete_snapshot(SnapshotId=snapshot_id)
        except Exception as e:
            logger.warning("Snapshot %s in use, skipping.", snapshot_id)

def lambda_handler(event, context):
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    ec2_client = boto3.client('ec2')

    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    for region in regions:
        logger.info("Processing region: %s", region)
        ec2_client_region = boto3.client('ec2', region_name=region)
        old_snapshots = get_old_snapshots(ec2_client_region, account_id)
        
        if old_snapshots:
            delete_snapshots(ec2_client_region, old_snapshots)
        else:
            logger.info("No old snapshots to delete in region: %s", region)

if __name__ == "__main__":
    lambda_handler(None, None)

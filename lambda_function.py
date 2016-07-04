import boto3
import time
import datetime
from operator import itemgetter, attrgetter, methodcaller


instance_filters = [
    {'Name': 'tag-key', 'Values':['autobackup']},
    {'Name': 'instance-state-name', 'Values':['running']}
]

class BasicObj(object):
    pass

ec = boto3.client('ec2')

def autobackup_manager(instanceid, instancename, numimages, instanceObject, owner):
    print "autobackup_manager su: "+instancename+" che deve avere "+numimages+" backups totali ("+instanceid+")"
#elenco i dischi ebs
    for dev in instanceObject['BlockDeviceMappings']:
        if (dev.has_key('Ebs')):
#per ciascun disco creo uno snapshopt con nome nomeistanza_idistanza_iddisco
            currentvolume=dev['Ebs']['VolumeId'];
            currentdescription='Automated backup '+instancename+"_"+instanceid+"_"+currentvolume
            ec.create_snapshot(VolumeId=currentvolume, Description=currentdescription)
            print "created snapshot :"+currentdescription
#elenco tutti gli snapshop basati sullo stesso volume
            simpleList = []
            dateList = []
            out2 = []
            snapshot_response = ec.describe_snapshots(OwnerIds=[owner], Filters=[{'Name': 'volume-id', 'Values': [currentvolume]}], MaxResults=100)
#ordino gli snapshop dello stesso disco per timestamp di creazione decrescente
            snapshots = sorted(snapshot_response['Snapshots'], key=itemgetter('StartTime'), reverse=True)
            toberemoved=snapshots[int(numimages):]
            for s in toberemoved:
#cancello quelli in eccesso
                try:
                    if (s['State']=="completed"):
                        ec.delete_snapshot(SnapshotId=s['SnapshotId'])                
                        print "rimosso: "+s['SnapshotId']
                except Exception as e:
                    print "rimozione di "+s['SnapshotId']+" generated Exception"
                    print e
#fine


def lambda_handler(event, context):
#elenco tutte le istanze attive
    reservations = ec.describe_instances(Filters=instance_filters);
    for reservation in reservations['Reservations']:
        for inst in reservation['Instances']:
            dobackup=0
            numbackups=False
            namebackup=""
            for t in inst['Tags']:
                if (t['Key']=="autobackup"):
                    dobackups=True
                    numbackups=t['Value']
                else:
                    if(t['Key']=='Name'):
                        namebackup=t['Value']
            if (dobackups):
#per ciascuna istanza che necessita backup eseguo la procedura che elenca i disci, ne fa immagine, e mantiene n immagini come descritto dal tag autobackup
                autobackup_manager(inst['InstanceId'], namebackup, numbackups, inst, reservation['OwnerId'])
#fine

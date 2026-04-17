import prometheus_client
from prometheus_client import generate_latest, Gauge

from . import metrics_blueprint
from ..models import Settings
from ..toncenterapi import Toncenterapi


prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)


def get_all_metrics():
    toncenterapi = Toncenterapi()

    try:
        response = {}
        last_fullnode_block_number = toncenterapi.get_masterchain_head()
        response['last_fullnode_block_number'] = last_fullnode_block_number
        response['last_fullnode_block_timestamp'] = toncenterapi.get_block_timestamp(last_fullnode_block_number)
    
        pd = Settings.query.filter_by(name = 'last_block').first()
        last_checked_block_number = int(pd.value)
        response['ton_wallet_last_block'] = last_checked_block_number
        timestamp = toncenterapi.get_block_timestamp(last_checked_block_number)
        response['ton_wallet_last_block_timestamp'] = timestamp
        response['ton_fullnode_status'] = 1
        return response
    except:
        response['ton_fullnode_status'] = 0
        return response


ton_fullnode_status = Gauge('ton_fullnode_status', 'Connection status to ton fullnode')
ton_fullnode_last_block = Gauge('ton_fullnode_last_block', 'Last block loaded to the fullnode', )
ton_wallet_last_block = Gauge('ton_wallet_last_block', 'Last checked block ') 
ton_fullnode_last_block_timestamp = Gauge('ton_fullnode_last_block_timestamp', 'Last block timestamp loaded to the fullnode', )
ton_wallet_last_block_timestamp = Gauge('ton_wallet_last_block_timestamp', 'Last checked block timestamp')

@metrics_blueprint.get("/metrics")
def get_metrics():
    response = get_all_metrics()
    if response['ton_fullnode_status'] == 1:
        ton_fullnode_last_block.set(response['last_fullnode_block_number'])
        ton_fullnode_last_block_timestamp.set(response['last_fullnode_block_timestamp'])
        ton_wallet_last_block.set(response['ton_wallet_last_block'])
        ton_wallet_last_block_timestamp.set(response['ton_wallet_last_block_timestamp'])
        ton_fullnode_status.set(response['ton_fullnode_status'])
    else:
        ton_fullnode_status.set(response['ton_fullnode_status'])

    return generate_latest().decode()
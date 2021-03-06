"""
    test_02_asset_identity


    As a developer working with Ocean,
    I need a stable identifier (Asset ID) for an arbitrary asset in the Ocean ecosystem

"""

import secrets
from starfish.asset import DataAsset
from starfish.agent import RemoteAgent


def test_02_asset_register(remote_agent_surfer, resources):
    testData = secrets.token_bytes(1024)
    asset1 = DataAsset.create('TestAsset1', testData)
    asset2 = DataAsset.create('TestAsset2', testData)
    asset = remote_agent_surfer.register_asset(asset2)
    assert(asset.data == asset2.data)


def test_02_asset_upload(remote_agent_surfer, resources):
    testData = secrets.token_bytes(1024)
    asset_data = DataAsset.create('TestAsset', testData)
    asset = remote_agent_surfer.register_asset(asset_data)
    remote_agent_surfer.upload_asset(asset)

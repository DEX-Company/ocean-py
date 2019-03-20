"""
    SurferModel - Model to access the Surfer Services
"""
import json
import requests
from web3 import Web3

from squid_py.did_resolver.did_resolver import DIDResolver
from squid_py.ddo.ddo import DDO

from starfish import logger

# default base URI for this version surfer
SURFER_BASE_URI = '/api/v1'

class SurferModel():
    _http_client = requests

    def __init__(self, ocean, did=None, ddo=None, options=None):
        """init a standard ocan connection, with a given DID"""
        self._ocean = ocean
        self._did = did
        self._ddo = ddo
        if not options:
            options = {}

        self._headers = {'content-type': 'application/json'}
        authorization = options.get('authorization')
        if authorization:
            self._headers['Authorization'] = f'Basic {authorization}'

    def register_asset(self, metadata, endpoint):
        """
        Register an asset with the agent storage server
        :param metadata: metadata to write to the storage server

        :return: A dict of the following items
        [0] asset_id.
        [1] did of the asset.
        [2] metadata in text format, that was saved.

        :type: dict
        """
        result = None
        metadata_text = json.dumps(metadata)
        asset_id = SurferModel.get_asset_id_from_metadata(metadata_text)
        saved_asset_id = self.save_metadata(asset_id, metadata_text, endpoint)
        if asset_id == saved_asset_id:
            result = {
                'asset_id': asset_id,
                'metadata_text': metadata_text,
            }
        return result

    def save_metadata(self, asset_id, metadata_text, endpoint):
        """save metadata to the agent server, using the asset_id and metadata"""
        url = endpoint + '/' + asset_id
        logger.debug(f'metadata save url {url}')
        response = SurferModel._http_client.put(url, data=metadata_text, headers=self._headers)
        if response and response.status_code == requests.codes.ok:
            if response.content == asset_id:
                return asset_id
            logger.warning(f'on asset save ( {asset_id} ) surfer returned an invalid asset id ({response.content})')
            return None
        logger.warning(f'metadata asset save {asset_id} response returned {response}')
        return None

    def read_asset(self, asset_id, endpoint):
        """read the metadata from a service agent using the asset_id"""

        result = None
        if endpoint:
            url = endpoint + '/' + asset_id
            logger.debug(f'metadata read url {url}')
            response = SurferModel._http_client.get(url, headers=self._headers)
            if response and response.status_code == requests.codes.ok:
                result = {
                    'asset_id': asset_id,
                    'metadata_text': response.content
                }
                # convert to str if bytes
                if isinstance(result['metadata_text'], bytes):
                    result['metadat_text'] = response.content.encode('utf-8')
            else:
                logger.warning(f'metadata asset read {asset_id} response returned {response}')
        return result

    def get_endpoint(self, name, service_type):
        """return the endpoint based on the name of the service, service service_type"""
        base_uri = None
        if name == 'metadata':
            base_uri = SURFER_BASE_URI + '/meta/data'
        # else: codacy complaint ..
        #    logger:warning(f'unknown service endpoint name {name}')

        if self._ddo and base_uri:
            service = self._ddo.get_service(service_type)
            if service:
                endpoints = service.endpoints
                return endpoints[0] + base_uri
        return None

    @property
    def ddo(self):
        """return the DDO stored for this agent"""
        return self._ddo

    @property
    def did(self):
        """return the DID used for this agent"""
        return self._did

    @property
    def register_name(self):
        return self._register_name


    @staticmethod
    def is_metadata_valid(asset_id, metadata_text):
        """
        validate metadata, by calcualating the hash (asset_id) and compare this to the
        given asset_id, if both are equal then the metadata is valid
        :param asset_id: asset id to compare with
        :param metadata: dict of metadata to calculate the hash ( asset_id)
        :return bool True if metadata is valid for the asset_id provided
        """
        if metadata_text:
            # the calc asset_id from the metadata should be same as this asset_id
            metadata_id = SurferModel.get_asset_id_from_metadata(metadata_text)
            if metadata_id != asset_id:
                logger.debug(f'metdata does not match {metadata_id} != {asset_id}')
            return metadata_id == asset_id
        return False


    @staticmethod
    def get_asset_id_from_metadata(metadata_text):
        """
        return the asset_id calculated from the metadata
        :param metadata: dict of metadata to hash
        a 64 char hex string, which is the asset id
        :return 64 char hex string, with no leading '0x'
        """
        return Web3.toHex(Web3.sha3(metadata_text.encode()))[2:]

    @staticmethod
    def set_http_client(http_client):
        """Set the http client to something other than the default `requests`"""
        SurferModel._http_client = http_client

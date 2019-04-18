"""

Memory Agent class to provide basic functionality for Ocean Agents

"""

import secrets
import re
import json

from squid_py.did import id_to_did

from starfish.account import Account
from starfish.agent import AgentBase
from starfish.listing import Listing
from starfish.asset import Asset
from starfish.purchase import Purchase
from starfish.utils.did import did_parse


class MemoryAgent(AgentBase):
    """

    Memory Agent class allows to register, list, purchase and consume assets.

    :param ocean: Ocean object that is being used.
    :type ocean: :class:`.Ocean`

    """

    def __init__(self, ocean, *args, **kwargs):
        """init a standard ocean object"""
        AgentBase.__init__(self, ocean)

        if args and isinstance(args[0], dict):
            kwargs = args[0]

        self._memory = {
            'listingdata': {},
            'asset': {},
            'purchase': {}
        }

    def register_asset(self, asset, account = None):
        """

        Register a memory asset with the ocean network.

        :param dict metadata: metadata dictionary to store for this asset.
        :param account: Optional, since an account is not assigned to an registered memory asset.
        :type account: :class:`.Account` object to use for registration.

        :return: A new :class:`.Listing` object that has been registered, if failure then return None.
        :type: :class:`.Listing` class

        For example::

            metadata = json.loads('my_metadata')
            # get your publisher account
            agent = MemoryAgent(ocean)
            listing = agent.register_asset(metadata)

            if listing:
                print(f'registered my listing asset for sale with the did {listing.did}')

        """

        did = id_to_did(secrets.token_hex(64))
        asset_did = did
        listingdata = {
            'did': did,
            'asset_did': asset_did
        }
        self._memory['listingdata'][did] = listingdata
        self._memory['asset'][asset_did] = asset

        listing = None
        if listingdata:
            asset.set_did(asset_did)
            listing = Listing(self, did, asset, listingdata)

        return listing

    def validate_asset(self, asset):
        """

        Validate an asset

        :param asset: Asset to validate.
        :return: True if the asset is valid
        """
        return not asset is None


    def get_listing(self, did):
        """

        Return an listing on the listing's DID.

        :param str did: DID of the listing.

        :return: a registered asset given a DID of the asset
        :type: :class:`.Asset` class

        """
        listing = None
        if MemoryAgent.is_did_valid(did):
            if did in self._memory['listingdata']:
                listingdata = self._memory['listingdata'][did]
                if listingdata:
                    asset_did = listingdata['asset_did']
                    asset = self._memory['asset'][asset_did]
                    listing = Listing(self, did, asset, listingdata)
        else:
            raise ValueError(f'Invalid did "{did}" for an asset')

        return listing


    def search_listings(self, text, sort=None, offset=100, page=0):
        """

        Search for listings with the givien 'text'

        :param str text: Text to search all listing data for.
        :param sort: sort the results ( defaults: None, no sort).
        :type sort: str or None
        :param int offset: Return the result from with the maximum record count ( defaults: 100 ).
        :param int page: Returns the page number based on the offset.

        :return: a list of listing objects found using the search.
        :type: :class:`.Listing` objects

        For example::

            # return the 300 -> 399 records in the search for the text 'weather' in the metadata.
            my_result = agent.search_registered_assets('weather', None, 100, 3)

        """
        listing_items = None
        for asset_did, asset in self._memory['asset'].items():
            if re.search(text, json.dumps(asset.metadata)):
                for did, listing in self._memory['listingdata'].items():
                    if listing['asset_did'] == asset_did:
                        if listing_items is None:
                            listing_items = {}
                        listing_items[did] = listing

        return listing_items

    def purchase_asset(self, listing, account):
        """

        Purchase an asset using it's listing and an account.

        :param listing: Listing to use for the purchase.
        :type listing: :class:`.Listing`
        :param account: Ocean account to purchase the asset.
        :type account: :class:`.Account` object to use for registration.

        """
        purchase = None

        purchase_id = secrets.token_hex(64)
        if purchase_id:
            purchase = Purchase(self, listing, purchase_id)
            self._memory['purchase'][purchase_id] = (purchase, account.address)

        return purchase

    def purchase_wait_for_completion(self, purchase_id, timeoutSeconds):
        """

            Wait for completion of the purchase

            TODO: issues here...
            + No method as yet to pass back paramaters and values during the purchase process
            + We assume that the following templates below will always be used.

        """
        return

    def is_access_granted_for_asset(self, asset, purchase_id, account):
        """

        Check to see if the account and purchase_id have access to the assed data.


        :param asset: Asset to check for access.
        :type asset: :class:`.Asset` object
        :param str purchase_id: purchase id that was used to purchase the asset.
        :param account: Ocean account to purchase the asset.
        :type account: :class:`.Account` object to use for registration.

        :return: True if the asset can be accessed and consumed.
        :type: boolean
        """

        if purchase_id in self._memory['purchase']:
            purchase, account_address = self._memory['purchase'][purchase_id]
            return purchase and account.is_address_equal(account_address)

        return False

    def consume_asset(self, listing, purchase_id, account, download_path):
        """
        Consume the asset and download the data. The actual payment to the asset
        provider will be made at this point.

        :param listing: Listing that was used to make the purchase.
        :type listing: :class:`.Listing`
        :param str purchase_id: purchase id that was used to purchase the asset.
        :param account: Ocean account that was used to purchase the asset.
        :type account: :class:`.Account` object to use for registration.
        :param str download_path: path to store the asset data.

        :return: True if the asset has been consumed and downloaded
        :type: boolean

        """
        return purchase_id in self._memory['purchase']

    @staticmethod
    def is_did_valid(did):
        """
        Checks to see if the DID string is a valid DID for this type of Asset.
        This method only checks the syntax of the DID, it does not resolve the DID
        to see if it is assigned to a valid Asset.

        :param str did: DID string to check to see if it is in a valid format.

        :return: True if the DID is in the format 'did:op:xxxxx'
        :type: boolean
        """
        data = did_parse(did)
        return not data['path']

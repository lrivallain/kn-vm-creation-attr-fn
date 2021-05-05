import os
import atexit
import ssl
import logging
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Session:
    """Setter is a client to set custom attributes to newly created VM.
    """

    def __init__(self):
        """Setter is a client to set custom attributes to newly created VM.
        """
        load_dotenv() # take environment variables from .env.
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        if os.environ.get('VC_SSLVERIFY', True) == 'False':
            self.ssl_context.verify_mode = ssl.CERT_NONE
        try:
            self.host = os.environ['VC_SERVER']
            self.user = os.environ['VC_USER']
            self.pwd  = os.environ['VC_PASSWORD']
            self.attr_owner = os.environ['VC_ATTR_OWNER']
            self.attr_creation_date = os.environ['VC_ATTR_CREATION_DATE']
            self.attr_last_poweredon = os.environ['VC_ATTR_LAST_POWEREDON']
        except KeyError as err:
            raise Exception(f'Missing mandatory configuration key: {err}')

        logger.debug(f'Initializing vCenter connection...')
        try:
            self.service_instance = SmartConnect(
                host = self.host,
                user = self.user,
                pwd  = self.pwd,
                port = 443,
                sslContext = self.ssl_context
            )
            atexit.register(Disconnect, self.service_instance)
            self.content = self.service_instance.RetrieveContent()
        except IOError as err:
            raise Exception(f'Error connecting to vCenter: {err}')
        except Exception as err:
            raise Exception(f'Unknown error when creating vsphere session: {err}')
        logger.info(f"Connected to vCenter {self.host}")


    def close(self):
        """Disconnect the current session from vCenter.
        """
        Disconnect(self.service_instance)


    def get_vm_attributes(self):
        """Get VM attributes reference.

        Returns:
            tuple: 3 VM attributes
        """
        attr_owner, attr_creation_date, attr_last_poweredon = None, None, None
        cfmgr = self.content.customFieldsManager
        for field in cfmgr.field:
            if field.name == self.attr_owner:
                attr_owner = field
            if field.name == self.attr_creation_date:
                attr_creation_date = field
            if field.name == self.attr_last_poweredon:
                attr_last_poweredon = field
        if not (attr_owner and attr_creation_date and attr_last_poweredon):
            raise Exception(f'Missing attribute for owner or creation_date')
        return attr_owner, attr_creation_date, attr_last_poweredon


    def get_vm(self, moref: str):
        """Get a VM object based on its MoRef identifier

        Args:
            moref (str): Identifier of the VM to return
        """
        # List and iter on VMs objects
        objView = self.content.viewManager.CreateContainerView(
            self.content.rootFolder,
            [vim.VirtualMachine],
            True
        )
        vmList = objView.view
        objView.Destroy()
        for vm in vmList:
            if vm._moId == moref:
                return vm
        return None


    def set_custom_attr(self, entity, key, value):
        """Set a custom attribute to entity

        Args:
            entity (obj): The entity object to set attribute on
            key (str): Key of the custom attribute
            value (str): Value of the custom attribute
        """
        cfmgr = self.content.customFieldsManager
        cfmgr.SetField(
            entity=entity,
            key=key,
            value=value
        )
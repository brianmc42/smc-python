'''
Exceptions Module
'''
import json
import smc.api.web

class SMCException(Exception):
    """ Base class for exceptions """
    pass

class ConfigLoadError(SMCException):
    """
    Thrown when there was a problem reading credential information from 
    file. Typically caused by missing settings.
    """
    pass

class SMCConnectionError(SMCException):
    """
    Thrown when there are connection related issues with the SMC.
    This could be that the underlying http requests library could not connect
    due to wrong IP address, wrong port, or time out
    """
    pass
        
class SMCOperationFailure(SMCException):
    """ Exception class for storing results from calls to the SMC
    This is thrown for HTTP methods that do not return the expected HTTP
    status code. See each http_* method in :py:mod:`smc.api.web` for 
    expected success status
    
    :param response: response object returned from HTTP method
    :param msg: optional msg to insert
    
    Instance attributes:
    
    :ivar response: http request response object
    :ivar code: http status code
    :ivar status: status from SMC API
    :ivar message: message attribute from SMC API
    :ivar details: details list from SMC API (may not always exist)
    :ivar smcresult: :py:class:`smc.api.web.SMCResult` object for consistent returns
    """
    def __init__(self, response=None):
        self.response = response
        self.code = None
        self.smcresult = smc.api.web.SMCResult()
        if response is not None:
            self.format_ex()
    
    def format_ex(self):
        details = None
        self.code = self.response.status_code
        if self.response.headers.get('content-type') == 'application/json':
            data = json.loads(self.response.text)
            #status = data.get('status', None)
            message = data.get('message', None)
            details = data.get('details', None)
        else: #it's not json
            if self.response.text:
                message = self.response.text
            else:
                message = "HTTP error code: %s, no message" % self.code

        self.smcresult.code = self.code
        
        if details:
            details = ' '.join(details).encode('utf-8') \
                if isinstance(details, list) else details.encode('utf-8')
        if message:
            message = message.encode('utf-8')
    
        if message and details:
            self.smcresult.msg = '{} {}'.format(message, details)
        elif details:
            self.smcresult.msg = details
        else:
            self.smcresult.msg = message

    def __repr__(self):
        return 'SMCOperationFailure(response=%s)' % (self.response)

class CertificateError(SMCException):
    """
    Related to certificate based operations like requests, signing, or
    creation. For example, engines that are not initialized can not respond
    to certificate creation requests and SMC API will return an error.
    """
    pass

class CreateEngineFailed(SMCException):
    """ 
    Thrown when a POST operation returns with a failed response.
    API based response will be returned as the exception message
    """
    pass

class LoadEngineFailed(SMCException):
    """ Thrown when attempting to load an engine that does not
    exist
    """
    pass

class CreatePolicyFailed(SMCException):
    """
    Thrown when failures occur when creating specific
    poliies like Firewall Policy, IPS, VPN, etc.
    """
    pass

class LoadPolicyFailed(SMCException):
    """
    Failure when trying to load a specific policy type
    """
    pass

class LoadElementFailed(SMCException):
    """
    Failure when attempting to obtain the settings for a specific
    element. This is more generic for a broad class of elements.
    """
    pass

class CreateElementFailed(SMCException):
    """
    Generic exception when there was a failure calling a 
    create method
    """
    pass

class ElementNotFound(SMCException):
    """
    Generic exception when an attempt is made to load an element 
    that is not found. This is only relavant for elements that 
    require the .load() method
    """
    pass

class MissingRequiredInput(SMCException):
    """
    Some functinos will flat out fail if certain fields are not provided.
    This is to ensure that some functions have some protection in case the
    user doesn't read the doc's.
    """
    pass
    
class UnsupportedEntryPoint(SMCException):
    """
    An entry point was specified that was not found in this API
    version. This is likely due to using an older version of the 
    SMC API that does not support that feature. The exception is 
    thrown specifying the entry point specified.
    """
    pass

class UnsupportedEngineFeature(SMCException):
    """
    If an operation is performed on an engine that does not support
    the functionality, this is thrown. For example, only Master Engine
    has virtual resources. IPS and Layer 2 Firewall do not have internal
    gateways (used for VPN).
    """
    pass

class UnsupportedInterfaceType(SMCException):
    """
    Some interface types are not supported on certain engines. For example,
    Virtual Engines only have Virtual Physical Interfaces. Layer 3 Firewalls
    do not support Capture or Inline Interfaces. This exception will be thrown
    when an attempt is made to enumerate interfaces for an engine type missing
    a reference to an unsupported interface type
    """
    pass

class TaskRunFailed(SMCException):
    """
    When running tasks such as policy upload, refresh policy, etc, if the result
    from SMC is a failure, possibly due to an incorrect input (i.e. missing policy),
    then this exception will be thrown
    """
    pass

class LicenseError(SMCException):
    """
    Thrown when operations to perform Node specific license related operations such as 
    bind license, fetch license or cancel license fail.
    For node licensing specific actions, see:
    :py:class: `smc.core.node.Node`
    """
    pass

class NodeCommandFailed(SMCException):
    """
    Each engine node will have multiple commands that can be executed such as go online,
    go offline, go standby, locking, etc. When these commands fail, this exception will
    be thrown and wrap the SMC API response.
    For all node specific command actions, see:
    :py:class: `smc.core.node.Node`
    """
    pass

class EngineCommandFailed(SMCException):
    """
    Engines will have some commands that are specifically executed such as adding 
    blacklist entries, flushing blacklist or adding routes. This exception will be
    thrown if the SMC API responds with any sort of error and wrap the response
    """
    pass

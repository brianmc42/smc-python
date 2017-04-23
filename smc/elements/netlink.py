"""
NetLink elements are used to represent alternative routes that lead to the
same destination IP addresses.

NetLinks usually represent Internet connections, but can be used for other
communications links as well.

You can use a single Router if a single route is enough for routing traffic
to a network through an interface or an aggregated link. If you want to create
separate routes for traffic to a network through two or more interfaces, you
must use NetLinks.

Tunnel interfaces for a Route-Based VPN do not use Router or NetLink elements.
Instead, networks that are reachable through the VPN tunnel are added directly
to the tunnel interface as if they were directly connected networks.

To use traffic handlers, you must first create the netlink type required, then
add this to the engine routing node.

Creating a static netlink element::

    StaticNetlink.create(
        name='netlink',
        gateway=Router('routerfoo'),
        network=[Network('mynetwork')],
        domain_server_address=['8.8.8.8', '8.8.4.4'],
        probe_address=['1.1.1.254'],
        comment='foobar')

Add the netlink to the desired routing interface::

    engine = Engine('vm')
    rnode = engine.routing.get(0) #interface 0
    rnode.add_traffic_handler(
        netlink=StaticNetlink('mynetlink'),
        netlink_gw=Router('myrtr'))

.. seealso:: :class:`smc.core.route.Routing.add_traffic_handler`

"""
from smc.base.model import Element, ElementCreator
from smc.base.util import element_resolver


class StaticNetlink(Element):
    """
    A Static Netlink is applied to an interface to provide an alternate
    route to a destination. It is typically used when you have fixed IP
    interfaces versus using DHCP (use a Dynamic NetLink).
    """
    typeof = 'netlink'

    def __init__(self, name, **meta):
        super(StaticNetlink, self).__init__(name, **meta)

    @classmethod
    def create(cls, name, gateway, network, input_speed=None,
               output_speed=None, domain_server_address=None,
               provider_name=None, probe_address=None,
               standby_mode_period=3600, standby_mode_timeout=30,
               active_mode_period=5, active_mode_timeout=1, comment=None):
        """
        Create a new netlink. Name, gateway and network values are all
        required fields.

        :param str name: name of netlink Element
        :param gateway: gateway (engine node) to map this netlink
            to. This can be an element or str href.
        :type gateway: Router,Engine
        :param list network: network/s associated with this netlink.
        :type network: list(str,Element)
        :param int input_speed: input speed in Kbps, used for ratio-based
            load-balancing
        :param int output_speed: output speed in Kbps,  used for ratio-based
            load-balancing
        :param list domain_server_address: dns addresse for netlink. Engine
            DNS can override this field
        :type dns_addresses: list(str,Element)
        :param str provider_name: optional name to identify provider for this
            netlink
        :param list probe_address: list of IP addresses to use as probing
            addresses to validate connectivity
        :type probe_ip_address: list(str)
        :param int standby_mode_period: Specifies the probe period when
            standby mode is used (in seconds)
        :param int standby_mode_timeout: probe timeout in seconds
        :param int active_mode_period: Specifies the probe period when active
            mode is used (in seconds)
        :param int active_mode_timeout: probe timeout in seconds
        :raises ElementNotFound: if using type Element parameters that are
            not found.
        :raises CreateElementFailed: failure to create netlink with reason
        :return: href of new netlink element

        .. note:: To monitor the status of the network links, you must define
                  at least one probe IP address.
        """
        comment = comment if comment else ''
        json = {'name': name,
                'gateway_ref': element_resolver(gateway),
                'ref': element_resolver(network),
                'input_speed': input_speed,
                'output_speed': output_speed,
                'probe_address': probe_address,
                'nsp_name': provider_name,
                'comment': comment,
                'standby_mode_period': standby_mode_period,
                'standby_mode_timeout': standby_mode_timeout,
                'active_mode_period': active_mode_period,
                'active_mode_timeout': active_mode_timeout}

        if domain_server_address:
            dns = element_resolver(domain_server_address)

            domain_server_address = [{'rank': num, 'value': server}
                                     if not server.startswith('http')
                                     else
                                     {'rank': num, 'ne_ref': server}
                                     for num, server in enumerate(dns)]

            json.update(domain_server_address=domain_server_address)

        return ElementCreator(cls, json)

    @property
    def domain_server_address(self):
        """
        Configured DNS servers for this netlink

        :return: list of DNS servers; if elements are specifed, they will
            be returned as type Element
        :rtype: list(str,Element)
        """
        return [address['value']
                if 'value' in address
                else
                Element.from_href(address['ne_ref'])
                for address in self.data.get('domain_server_address', [])]

    @property
    def gateway(self):
        """
        The gateway (engine) that this netlink is used on.

        :return: Element type for engine
        :rtype: Element
        """
        return Element.from_href(self.data.get('gateway_ref'))

    @property
    def networks(self):
        """
        List of networks this static netlink uses.

        :return: networks associated with this netlink, as Element
        :rtype: Element
        """
        return [Element.from_href(element)
                for element in self.data.get('ref')]

    @property
    def input_speed(self):
        """
        Used for ratio-based load-balancing method. Value is based on the
        real-life bandwidth the network connection provides. The values are
        used to calculate how much traffic each link receives in relation to
        the other links.

        :return: input speed in Kbps
        :rtype: int
        """
        return self.data.get('input_speed')

    @property
    def output_speed(self):
        """
        Used for ratio-based load-balancing method. Value is based on the
        real-life bandwidth the network connection provides. The values are
        used to calculate how much traffic each link receives in relation to
        the other links.

        :return: output speed in Kbps
        :rtype: int
        """
        return self.data.get('output_speed')

    @property
    def standby_mode_period(self):
        """
        Specifies the probe period when Standby Mode is used.

        :return: probe period in seconds
        :rtype: int
        """
        return self.data.get('standby_mode_period')

    @property
    def standby_mode_timeout(self):
        """
        Specifies the probe timeout when Standby Mode is used.

        :return: probe timeout in seconds
        :rtype: int
        """
        return self.data.get('standby_mode_timeout')

    @property
    def active_mode_period(self):
        """
        Specifies the probe period when Active Mode is used.

        :return: probe period in seconds
        :rtype: int
        """
        return self.data.get('active_mode_period')

    @property
    def active_mode_timeout(self):
        """
        Specifies the probe timeout when Active Mode is used.

        :return: probe timeout in seconds
        :rtype: int
        """
        return self.data.get('active_mode_timeout')

    @property
    def probe_address(self):
        """
        IP addresses that are probed with ICMP echo requests (ping) to
        determine if the link is up. It is recommended to add more than
        one.

        :return: list of probe addresses
        :rtype: list(str)
        """
        return self.data.get('probe_address')

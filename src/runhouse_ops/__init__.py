# def get_instance(provider=None, instance_type=None, ips=None, ssh_creds=None, name=None, **kwargs):
#     """ Returns an instance of compute matching the given parameters
#
#     Usage Note:
#         - If the args `ips` and `ssh_creds` ARE provided, the instance will be assumed to be BYOServer
#         - If the args `ips`, and `ssh_creds` ARE NOT provided, the instance will be assumed to be via a cloud provider
#
#     Args:
#         provider (str, optional): The provider to use for the instance. Defaults to None.
#         instance_type (str, optional): The instance type to use for the instance. Defaults to None.
#         ips (list, optional): A list of ips to use for the instance. Defaults to None.
#         ssh_creds (dict, optional): A dict of ssh credentials to use for the instance. Defaults to None.
#         name (str, optional): The name of the instance. Defaults to None.
#         **kwargs: Additional kwargs to pass to the instance
#
#     Returns:
#         rh.Cluster or rh.OnDemandCluster: The resulting cluster.
#     """
#
#     gpu = rh.cluster(provider=provider, instance_type=instance_type, ips=ips, ssh_creds=ssh_creds, name=name, **kwargs)
#     return gpu
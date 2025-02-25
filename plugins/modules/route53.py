#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r'''
---
module: route53
version_added: 1.0.0
requirements: [ "boto3", "botocore" ]
short_description: add or delete entries in Amazons Route 53 DNS service
description:
     - Creates and deletes DNS records in Amazons Route 53 service.
options:
  state:
    description:
      - Specifies the state of the resource record. As of Ansible 2.4, the I(command) option has been changed
        to I(state) as default and the choices C(present) and C(absent) have been added, but I(command) still works as well.
    required: true
    aliases: [ 'command' ]
    choices: [ 'present', 'absent', 'get', 'create', 'delete' ]
    type: str
  zone:
    description:
      - The DNS zone to modify.
      - This is a required parameter, if parameter I(hosted_zone_id) is not supplied.
    type: str
  hosted_zone_id:
    description:
      - The Hosted Zone ID of the DNS zone to modify.
      - This is a required parameter, if parameter I(zone) is not supplied.
    type: str
  record:
    description:
      - The full DNS record to create or delete.
    required: true
    type: str
  ttl:
    description:
      - The TTL, in second, to give the new record.
      - Mutually exclusive with I(alias).
    default: 3600
    type: int
  type:
    description:
      - The type of DNS record to create.
    required: true
    choices: [ 'A', 'CNAME', 'MX', 'AAAA', 'TXT', 'PTR', 'SRV', 'SPF', 'CAA', 'NS', 'SOA' ]
    type: str
  alias:
    description:
      - Indicates if this is an alias record.
      - Mutually exclusive with I(ttl).
      - Defaults to C(false).
    type: bool
  alias_hosted_zone_id:
    description:
      - The hosted zone identifier.
    type: str
  alias_evaluate_target_health:
    description:
      - Whether or not to evaluate an alias target health. Useful for aliases to Elastic Load Balancers.
    type: bool
    default: false
  value:
    description:
      - The new value when creating a DNS record.  YAML lists or multiple comma-spaced values are allowed for non-alias records.
      - When deleting a record all values for the record must be specified or Route 53 will not delete it.
    type: list
    elements: str
  overwrite:
    description:
      - Whether an existing record should be overwritten on create if values do not match.
    type: bool
  retry_interval:
    description:
      - In the case that Route 53 is still servicing a prior request, this module will wait and try again after this many seconds.
        If you have many domain names, the default of C(500) seconds may be too long.
    default: 500
    type: int
  private_zone:
    description:
      - If set to C(true), the private zone matching the requested name within the domain will be used if there are both public and private zones.
      - The default is to use the public zone.
    type: bool
    default: false
  identifier:
    description:
      - Have to be specified for Weighted, latency-based and failover resource record sets only.
        An identifier that differentiates among multiple resource record sets that have the same combination of DNS name and type.
    type: str
  weight:
    description:
      - Weighted resource record sets only. Among resource record sets that
        have the same combination of DNS name and type, a value that
        determines what portion of traffic for the current resource record set
        is routed to the associated location.
      - Mutually exclusive with I(region) and I(failover).
    type: int
  region:
    description:
      - Latency-based resource record sets only Among resource record sets
        that have the same combination of DNS name and type, a value that
        determines which region this should be associated with for the
        latency-based routing
      - Mutually exclusive with I(weight) and I(failover).
    type: str
  health_check:
    description:
      - Health check to associate with this record
    type: str
  failover:
    description:
      - Failover resource record sets only. Whether this is the primary or
        secondary resource record set. Allowed values are PRIMARY and SECONDARY
      - Mutually exclusive with I(weight) and I(region).
    type: str
    choices: ['SECONDARY', 'PRIMARY']
  vpc_id:
    description:
      - "When used in conjunction with private_zone: true, this will only modify records in the private hosted zone attached to this VPC."
      - This allows you to have multiple private hosted zones, all with the same name, attached to different VPCs.
    type: str
  wait:
    description:
      - Wait until the changes have been replicated to all Amazon Route 53 DNS servers.
    type: bool
    default: false
  wait_timeout:
    description:
      - How long to wait for the changes to be replicated, in seconds.
    default: 300
    type: int
author:
- Bruce Pennypacker (@bpennypacker)
- Mike Buzzetti (@jimbydamonk)
extends_documentation_fragment:
- amazon.aws.aws
'''

RETURN = r'''
nameservers:
  description: Nameservers associated with the zone.
  returned: when state is 'get'
  type: list
  sample:
  - ns-1036.awsdns-00.org.
  - ns-516.awsdns-00.net.
  - ns-1504.awsdns-00.co.uk.
  - ns-1.awsdns-00.com.
set:
  description: Info specific to the resource record.
  returned: when state is 'get'
  type: complex
  contains:
    alias:
      description: Whether this is an alias.
      returned: always
      type: bool
      sample: false
    failover:
      description: Whether this is the primary or secondary resource record set.
      returned: always
      type: str
      sample: PRIMARY
    health_check:
      description: health_check associated with this record.
      returned: always
      type: str
    identifier:
      description: An identifier that differentiates among multiple resource record sets that have the same combination of DNS name and type.
      returned: always
      type: str
    record:
      description: Domain name for the record set.
      returned: always
      type: str
      sample: new.foo.com.
    region:
      description: Which region this should be associated with for latency-based routing.
      returned: always
      type: str
      sample: us-west-2
    ttl:
      description: Resource record cache TTL.
      returned: always
      type: str
      sample: '3600'
    type:
      description: Resource record set type.
      returned: always
      type: str
      sample: A
    value:
      description: Record value.
      returned: always
      type: str
      sample: 52.43.18.27
    values:
      description: Record Values.
      returned: always
      type: list
      sample:
      - 52.43.18.27
    weight:
      description: Weight of the record.
      returned: always
      type: str
      sample: '3'
    zone:
      description: Zone this record set belongs to.
      returned: always
      type: str
      sample: foo.bar.com.
'''

EXAMPLES = r'''
- name: Add new.foo.com as an A record with 3 IPs and wait until the changes have been replicated
  community.aws.route53:
    state: present
    zone: foo.com
    record: new.foo.com
    type: A
    ttl: 7200
    value: 1.1.1.1,2.2.2.2,3.3.3.3
    wait: yes
- name: Update new.foo.com as an A record with a list of 3 IPs and wait until the changes have been replicated
  community.aws.route53:
    state: present
    zone: foo.com
    record: new.foo.com
    type: A
    ttl: 7200
    value:
      - 1.1.1.1
      - 2.2.2.2
      - 3.3.3.3
    wait: yes
- name: Retrieve the details for new.foo.com
  community.aws.route53:
    state: get
    zone: foo.com
    record: new.foo.com
    type: A
  register: rec
- name: Delete new.foo.com A record using the results from the get command
  community.aws.route53:
    state: absent
    zone: foo.com
    record: "{{ rec.set.record }}"
    ttl: "{{ rec.set.ttl }}"
    type: "{{ rec.set.type }}"
    value: "{{ rec.set.value }}"
# Add an AAAA record.  Note that because there are colons in the value
# that the IPv6 address must be quoted. Also shows using the old form command=create.
- name: Add an AAAA record
  community.aws.route53:
    command: create
    zone: foo.com
    record: localhost.foo.com
    type: AAAA
    ttl: 7200
    value: "::1"
# For more information on SRV records see:
# https://en.wikipedia.org/wiki/SRV_record
- name: Add a SRV record with multiple fields for a service on port 22222
  community.aws.route53:
    state: present
    zone: foo.com
    record: "_example-service._tcp.foo.com"
    type: SRV
    value: "0 0 22222 host1.foo.com,0 0 22222 host2.foo.com"
# Note that TXT and SPF records must be surrounded
# by quotes when sent to Route 53:
- name: Add a TXT record.
  community.aws.route53:
    state: present
    zone: foo.com
    record: localhost.foo.com
    type: TXT
    ttl: 7200
    value: '"bar"'
- name: Add an alias record that points to an Amazon ELB
  community.aws.route53:
    state: present
    zone: foo.com
    record: elb.foo.com
    type: A
    value: "{{ elb_dns_name }}"
    alias: True
    alias_hosted_zone_id: "{{ elb_zone_id }}"
- name: Retrieve the details for elb.foo.com
  community.aws.route53:
    state: get
    zone: foo.com
    record: elb.foo.com
    type: A
  register: rec
- name: Delete an alias record using the results from the get command
  community.aws.route53:
    state: absent
    zone: foo.com
    record: "{{ rec.set.record }}"
    ttl: "{{ rec.set.ttl }}"
    type: "{{ rec.set.type }}"
    value: "{{ rec.set.value }}"
    alias: True
    alias_hosted_zone_id: "{{ rec.set.alias_hosted_zone_id }}"
- name: Add an alias record that points to an Amazon ELB and evaluates it health
  community.aws.route53:
    state: present
    zone: foo.com
    record: elb.foo.com
    type: A
    value: "{{ elb_dns_name }}"
    alias: True
    alias_hosted_zone_id: "{{ elb_zone_id }}"
    alias_evaluate_target_health: True
- name: Add an AAAA record with Hosted Zone ID
  community.aws.route53:
    state: present
    zone: foo.com
    hosted_zone_id: Z2AABBCCDDEEFF
    record: localhost.foo.com
    type: AAAA
    ttl: 7200
    value: "::1"
- name: Use a routing policy to distribute traffic
  community.aws.route53:
    state: present
    zone: foo.com
    record: www.foo.com
    type: CNAME
    value: host1.foo.com
    ttl: 30
    # Routing policy
    identifier: "host1@www"
    weight: 100
    health_check: "d994b780-3150-49fd-9205-356abdd42e75"
- name: Add a CAA record (RFC 6844)
  community.aws.route53:
    state: present
    zone: example.com
    record: example.com
    type: CAA
    value:
      - 0 issue "ca.example.net"
      - 0 issuewild ";"
      - 0 iodef "mailto:security@example.com"
'''

from operator import itemgetter

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible.module_utils._text import to_native

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_message
from ansible_collections.amazon.aws.plugins.module_utils.core import scrub_none_parameters
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry

MAX_AWS_RETRIES = 10  # How many retries to perform when an API call is failing
WAIT_RETRY = 5  # how many seconds to wait between propagation status polls


@AWSRetry.jittered_backoff(retries=MAX_AWS_RETRIES)
def _list_record_sets(route53, **kwargs):
    paginator = route53.get_paginator('list_resource_record_sets')
    return paginator.paginate(**kwargs).build_full_result()['ResourceRecordSets']


@AWSRetry.jittered_backoff(retries=MAX_AWS_RETRIES)
def _list_hosted_zones(route53, **kwargs):
    paginator = route53.get_paginator('list_hosted_zones')
    return paginator.paginate(**kwargs).build_full_result()['HostedZones']


def get_record(route53, zone_id, record_name, record_type, record_identifier):
    record_sets_results = _list_record_sets(route53, HostedZoneId=zone_id)

    for record_set in record_sets_results:
        # If the record name and type is not equal, move to the next record
        if (record_name, record_type) != (record_set['Name'], record_set['Type']):
            continue

        if record_identifier and record_identifier != record_set.get("SetIdentifier"):
            continue

        return record_set

    return None


def get_zone_id_by_name(route53, module, zone_name, want_private, want_vpc_id):
    """Finds a zone by name or zone_id"""
    hosted_zones_results = _list_hosted_zones(route53)

    for zone in hosted_zones_results:
        # only save this zone id if the private status of the zone matches
        # the private_zone_in boolean specified in the params
        private_zone = module.boolean(zone['Config'].get('PrivateZone', False))
        zone_id = zone['Id'].replace("/hostedzone/", "")

        if private_zone == want_private and zone['Name'] == zone_name:
            if want_vpc_id:
                # NOTE: These details aren't available in other boto methods, hence the necessary
                # extra API call
                hosted_zone = route53.get_hosted_zone(aws_retry=True, Id=zone_id)
                if want_vpc_id in [v['VPCId'] for v in hosted_zone['VPCs']]:
                    return zone_id
            else:
                return zone_id
    return None


def get_hosted_zone_nameservers(route53, zone_id):
    hosted_zone_name = route53.get_hosted_zone(aws_retry=True, Id=zone_id)['HostedZone']['Name']
    resource_records_sets = _list_record_sets(route53, HostedZoneId=zone_id)

    nameservers_records = list(
        filter(lambda record: record['Name'] == hosted_zone_name and record['Type'] == 'NS', resource_records_sets)
    )[0]['ResourceRecords']

    return [ns_record['Value'] for ns_record in nameservers_records]


def main():
    argument_spec = dict(
        state=dict(type='str', required=True, choices=['absent', 'create', 'delete', 'get', 'present'], aliases=['command']),
        zone=dict(type='str'),
        hosted_zone_id=dict(type='str'),
        record=dict(type='str', required=True),
        ttl=dict(type='int', default=3600),
        type=dict(type='str', required=True, choices=['A', 'AAAA', 'CAA', 'CNAME', 'MX', 'NS', 'PTR', 'SOA', 'SPF', 'SRV', 'TXT']),
        alias=dict(type='bool'),
        alias_hosted_zone_id=dict(type='str'),
        alias_evaluate_target_health=dict(type='bool', default=False),
        value=dict(type='list', elements='str'),
        overwrite=dict(type='bool'),
        retry_interval=dict(type='int', default=500),
        private_zone=dict(type='bool', default=False),
        identifier=dict(type='str'),
        weight=dict(type='int'),
        region=dict(type='str'),
        health_check=dict(type='str'),
        failover=dict(type='str', choices=['PRIMARY', 'SECONDARY']),
        vpc_id=dict(type='str'),
        wait=dict(type='bool', default=False),
        wait_timeout=dict(type='int', default=300),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[['zone', 'hosted_zone_id']],
        # If alias is True then you must specify alias_hosted_zone as well
        required_together=[['alias', 'alias_hosted_zone_id']],
        # state=present, absent, create, delete THEN value is required
        required_if=(
            ('state', 'present', ['value']),
            ('state', 'create', ['value']),
            ('state', 'absent', ['value']),
            ('state', 'delete', ['value']),
        ),
        # failover, region and weight are mutually exclusive
        mutually_exclusive=[
            ('failover', 'region', 'weight'),
            ('alias', 'ttl'),
        ],
        # failover, region and weight require identifier
        required_by=dict(
            failover=('identifier',),
            region=('identifier',),
            weight=('identifier',),
        ),
    )

    if module.params['state'] in ('present', 'create'):
        command_in = 'create'
    elif module.params['state'] in ('absent', 'delete'):
        command_in = 'delete'
    elif module.params['state'] == 'get':
        command_in = 'get'

    zone_in = (module.params.get('zone') or '').lower()
    hosted_zone_id_in = module.params.get('hosted_zone_id')
    ttl_in = module.params.get('ttl')
    record_in = module.params.get('record').lower()
    type_in = module.params.get('type')
    value_in = module.params.get('value') or []
    alias_in = module.params.get('alias')
    alias_hosted_zone_id_in = module.params.get('alias_hosted_zone_id')
    alias_evaluate_target_health_in = module.params.get('alias_evaluate_target_health')
    retry_interval_in = module.params.get('retry_interval')

    if module.params['vpc_id'] is not None:
        private_zone_in = True
    else:
        private_zone_in = module.params.get('private_zone')

    identifier_in = module.params.get('identifier')
    weight_in = module.params.get('weight')
    region_in = module.params.get('region')
    health_check_in = module.params.get('health_check')
    failover_in = module.params.get('failover')
    vpc_id_in = module.params.get('vpc_id')
    wait_in = module.params.get('wait')
    wait_timeout_in = module.params.get('wait_timeout')

    if zone_in[-1:] != '.':
        zone_in += "."

    if record_in[-1:] != '.':
        record_in += "."

    if command_in == 'create' or command_in == 'delete':
        if alias_in and len(value_in) != 1:
            module.fail_json(msg="parameter 'value' must contain a single dns name for alias records")
        if (weight_in is None and region_in is None and failover_in is None) and identifier_in is not None:
            module.fail_json(msg="You have specified identifier which makes sense only if you specify one of: weight, region or failover.")

    # connect to the route53 endpoint
    try:
        route53 = module.client(
            'route53',
            retry_decorator=AWSRetry.jittered_backoff(retries=MAX_AWS_RETRIES, delay=retry_interval_in)
        )
    except botocore.exceptions.HTTPClientError as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS')

    # Find the named zone ID
    zone_id = hosted_zone_id_in or get_zone_id_by_name(route53, module, zone_in, private_zone_in, vpc_id_in)

    # Verify that the requested zone is already defined in Route53
    if zone_id is None:
        errmsg = "Zone %s does not exist in Route53" % (zone_in or hosted_zone_id_in)
        module.fail_json(msg=errmsg)

    aws_record = get_record(route53, zone_id, record_in, type_in, identifier_in)

    resource_record_set = scrub_none_parameters({
        'Name': record_in,
        'Type': type_in,
        'Weight': weight_in,
        'Region': region_in,
        'Failover': failover_in,
        'TTL': ttl_in,
        'ResourceRecords': [dict(Value=value) for value in value_in],
        'HealthCheckId': health_check_in,
    })

    if alias_in:
        resource_record_set['AliasTarget'] = dict(
            HostedZoneId=alias_hosted_zone_id_in,
            DNSName=value_in[0],
            EvaluateTargetHealth=alias_evaluate_target_health_in
        )
        if 'ResourceRecords' in resource_record_set:
            del resource_record_set['ResourceRecords']
        if 'TTL' in resource_record_set:
            del resource_record_set['TTL']

    # On CAA records order doesn't matter
    if type_in == 'CAA':
        resource_record_set['ResourceRecords'] = sorted(resource_record_set['ResourceRecords'], key=itemgetter('Value'))

    if command_in == 'create' and aws_record == resource_record_set:
        module.exit_json(changed=False)

    if command_in == 'get':
        if type_in == 'NS':
            ns = aws_record.get('values', [])
        else:
            # Retrieve name servers associated to the zone.
            ns = get_hosted_zone_nameservers(route53, zone_id)

        module.exit_json(changed=False, set=aws_record, nameservers=ns)

    if command_in == 'delete' and not aws_record:
        module.exit_json(changed=False)

    if command_in == 'create' or command_in == 'delete':
        if command_in == 'create' and aws_record:
            if not module.params['overwrite']:
                module.fail_json(msg="Record already exists with different value. Set 'overwrite' to replace it")
            command = 'UPSERT'
        else:
            command = command_in.upper()

    if not module.check_mode:
        try:
            change_resource_record_sets = route53.change_resource_record_sets(
                aws_retry=True,
                HostedZoneId=zone_id,
                ChangeBatch=dict(
                    Changes=[
                        dict(
                            Action=command,
                            ResourceRecordSet=resource_record_set
                        )
                    ]
                )
            )

            if wait_in:
                waiter = route53.get_waiter('resource_record_sets_changed')
                waiter.wait(
                    Id=change_resource_record_sets['ChangeInfo']['Id'],
                    WaiterConfig=dict(
                        Delay=WAIT_RETRY,
                        MaxAttemps=wait_timeout_in // WAIT_RETRY,
                    )
                )
        except is_boto3_error_message('but it already exists'):
            module.exit_json(changed=False)
        except botocore.exceptions.WaiterError as e:
            module.fail_json_aws(e, msg='Timeout waiting for resource records changes to be applied')
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:  # pylint: disable=duplicate-except
            module.fail_json_aws(e, msg='Failed to update records')
        except Exception as e:
            module.fail_json(msg='Unhandled exception. (%s)' % to_native(e))

    module.exit_json(
        changed=True,
        diff=dict(
            before=aws_record,
            after=resource_record_set if command != 'delete' else {},
        ),
    )


if __name__ == '__main__':
    main()

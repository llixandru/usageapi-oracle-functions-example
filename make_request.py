# coding: utf-8
# Copyright (c) 2016, 2020, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl
# or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

import requests
from oci.config import from_file
from oci.signer import Signer

config = from_file()
auth = Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file'],
    pass_phrase=config['pass_phrase']
)

endpoint = 'https://usageapi.eu-frankfurt-1.oci.oraclecloud.com/20200107/usage'

body = {
    'tenantId': config['tenancy'],
    'granularity': 'MONTHLY',
    'timeUsageStarted': '2020-10-10T00:00:00.000Z',
    'timeUsageEnded': '2021-10-10T00:00:00.000Z'
}

response = requests.post(endpoint, json=body, auth=auth)
response.raise_for_status()

print(response.json())

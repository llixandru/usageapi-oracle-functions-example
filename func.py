# coding: utf-8
# Copyright (c) 2016, 2020, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl
# or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

import io
import json
import oci
import requests
from fdk import response


def handler(ctx, data: io.BytesIO = None):
    try:
        body = json.loads(data.getvalue())
    except Exception:
        raise Exception()
    resp = get_usage(body)
    return response.Response(
        ctx,
        response_data=json.dumps(resp.json()),
        headers={"Content-Type": "application/json"}
    )


def get_usage(body):
    signer = oci.auth.signers.get_resource_principals_signer()
    try:
        endpoint = 'https://usageapi.eu-frankfurt-1.oci.oraclecloud.com/20200107/usage'
        output = requests.post(endpoint, json=body, auth=signer)
    except Exception as e:
        output = "Failed: " + str(e.message)
    return output

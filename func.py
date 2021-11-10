# coding: utf-8
# Copyright (c) 2016, 2020, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl
# or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

import io
import json
import oci
from fdk import response
from datetime import datetime


def handler(ctx, data: io.BytesIO = None):
    try:
        body = json.loads(data.getvalue())
    except Exception:
        raise Exception()
    resp = get_usage(body)
    return response.Response(
        ctx,
        response_data=resp,
        headers={"Content-Type": "application/json"}
    )


def get_usage(body):
    signer = oci.auth.signers.get_resource_principals_signer()
    usage_api_client = oci.usage_api.UsageapiClient(config={}, signer=signer)
    output = ""
    try:
        request_summarized_usages_response = usage_api_client.request_summarized_usages(request_summarized_usages_details=oci.usage_api.models.RequestSummarizedUsagesDetails(
            tenant_id=body["tenantId"],
            time_usage_started=datetime.strptime(
                body["timeUsageStarted"],
                "%Y-%m-%dT%H:%M:%S.%fZ"),
            time_usage_ended=datetime.strptime(
                body["timeUsageEnded"],
                "%Y-%m-%dT%H:%M:%S.%fZ"),
            granularity=body["granularity"],
            query_type=body["queryType"]))
        output = request_summarized_usages_response.data
    except Exception as e:
        output = "Failed: " + str(e.message)
    return output

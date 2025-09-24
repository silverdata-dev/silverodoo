import requests
url = "https://api.zeptomail.com/v1.1/email/template/batch"

payload = '''
{\n\"mail_template_key\":\"2d6f.6ea5ff3994a2d856.k1.1c0b4101-834f-11f0-9f35-fae9afc80e45.198ebda890f\",
\n\"from\": { \"address\": \"noreply@silver-data.net\", \"name\": \"noreply\"},
\n\"to\": [{\"email_address\": {\"address\": \"lmoraperez@gmail.com\",\"name\": \"Luis Mora\"},
\"merge_info\": {"name":"name_valueluis","team":"team_valueluis","product_name":"Luis producto"}},
{\"email_address\": {\"address\": \"scitelhta@gmail.com.com\",\"name\": \"Sergio\"},
\"merge_info\": {"name":"name_valuesss","team":"team_valuesss","product_name":"product_name_valuessss"}}]
}'''

headers = {
'accept': "application/json",
'content-type': "application/json",
'authorization': "Zoho-enczapikey wSsVR61/+BL4Dq8vmDyrdOc7nA9dBlv1HUh+2Qbw4yWoTarDpsc/kxWfAwHyGPRKFjRqEDVE8e4rnEpUhDQIh9h8nFgECyiF9mqRe1U4J3x17qnvhDzPVm5VmxaMKIILzg9vnGFpEcsi+g==",
}

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)

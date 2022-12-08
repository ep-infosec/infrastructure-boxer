#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import plugins.basetypes
import plugins.session
import aiohttp

""" GitHub org invite endpoint for Boxer"""


async def process(
        server: plugins.basetypes.Server, session: plugins.session.SessionObject, indata: dict
) -> dict:
    if indata.get('unlink') and session.credentials:
        for person in server.data.people:
            if person.asf_id == session.credentials.uid:
                print(f"Unlinking GitHub login from user {person.asf_id}")
                person.github_login = ""
                person.save(server.database.client)
                return {
                    "okay": True,
                    "reauth": True,
                    "message": "unlinked from GitHub",
                }
        return {
            "okay": False,
            "message": "Could not unlink - account not found in database!",
        }
    if not session.credentials.github_id:
        if session.credentials.github_login:
            for person in server.data.people:
                if person.github_login == session.credentials.github_login:
                    print(f"Removing stale GitHub login from user {person.asf_id}")
                    person.github_login = ""
                    person.save(server.database.client)
                    break
        return {
            "okay": False,
            "reauth": True,
            "message": "Could not invite to Org - missing numerical GitHub ID.",
        }
    if session.credentials and session.credentials.github_login:
        invite_url = f"https://api.github.com/orgs/{server.config.github.org}/invitations"
        async with aiohttp.ClientSession() as httpsession:
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': f"token {server.config.github.token}",
            }
            async with httpsession.post(invite_url, headers=headers, json={
                "invitee_id": session.credentials.github_id,
                "role": "direct_member",
            }) as rv:
                response = await rv.json()
                if rv.status == 201:
                    return {
                        "okay": True,
                        "message": "Invitation sent!",
                    }
                else:
                    return {
                        "okay": False,
                        "message": "Could not invite to Org - already invited??",
                    }
    else:
        return {
            "okay": False,
            "message": "You need to be authed via GitHub before we can send an invite link to you.",
        }


def register(server: plugins.basetypes.Server):
    return plugins.basetypes.Endpoint(process)

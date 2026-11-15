#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import plistlib
import copy


def parse_com_apple_messages_urlballoonprovider_objects_parse_xml(
    dict_data: dict, list_objects: list
):
    keys = dict_data.keys()
    for key in keys:
        if isinstance(dict_data[key], dict):
            if "CF$UID" in dict_data[key].keys():
                dict_data[key] = copy.deepcopy(list_objects[dict_data[key]["CF$UID"]])
    for key in keys:
        if isinstance(dict_data[key], dict):
            parse_com_apple_messages_urlballoonprovider_objects_parse_xml(
                dict_data[key], list_objects
            )


def parse_com_apple_messages_urlballoonprovider(data: str):
    debug = False
    dict_data = plistlib.loads(data)
    if debug:
        list_keys = dict_data.keys()
        print(list_keys)
        for key in list_keys:
            print("key {}: {}".format(key, dict_data[key]))
    list_objects = dict_data["$objects"]
    if debug:
        print("Iter objs")
        i = 0
        for obj in list_objects:
            print("{}:{}".format(i, obj))
            i += 1

    dict_objects = copy.deepcopy(list_objects[dict_data["$top"]["root"]["CF$UID"]])
    parse_com_apple_messages_urlballoonprovider_objects_parse_xml(
        dict_objects, list_objects
    )

    if debug:
        print(dict_objects)

    dict_temp = dict()
    dict_temp["Body"] = (
        dict_objects["richLinkMetadata"]["title"]
        + "\n"
        + dict_objects["richLinkMetadata"]["summary"]
        + "\n"
        + dict_objects["richLinkMetadata"]["URL"]["NS.relative"]
    )
    dict_temp["Attachments"] = list()
    dict_image = dict()
    dict_image["name"] = dict_objects["richLinkMetadata"]["image"]["$class"][
        "$classname"
    ]
    dict_image["mime_type"] = dict_objects["richLinkMetadata"]["image"]["MIMEType"]
    dict_image["data"] = dict_objects["richLinkMetadata"]["image"]["data"]["NS.data"]
    dict_temp["Attachments"].append(dict_image)

    return dict_temp


def parse_com_apple_messages_msmessageextensionballoonplugin_objects_parse_bin(
    dict_data: dict, list_objects: list
):
    keys = dict_data.keys()
    for key in keys:
        if isinstance(dict_data[key], plistlib.UID):
            dict_data[key] = copy.deepcopy(list_objects[dict_data[key]])
        elif isinstance(dict_data[key], list):
            list_new = list()
            for item in dict_data[key]:
                if isinstance(item, plistlib.UID):
                    list_new.append(copy.deepcopy(list_objects[item]))
                else:
                    list_new.append(item)
            dict_data[key] = list_new

    for key in keys:
        if isinstance(dict_data[key], dict):
            parse_com_apple_messages_msmessageextensionballoonplugin_objects_parse_bin(
                dict_data[key], list_objects
            )
        elif isinstance(dict_data[key], list):
            for i, item in enumerate(dict_data[key]):
                if isinstance(dict_data[key][i], dict):
                    parse_com_apple_messages_msmessageextensionballoonplugin_objects_parse_bin(
                        dict_data[key][i], list_objects
                    )
                elif isinstance(dict_data[key][i], list):
                    parse_com_apple_messages_msmessageextensionballoonplugin_objects_parse_bin(
                        dict_data[key][i], list_objects
                    )


def parse_com_apple_messages_msmessageextensionballoonplugin_get_text(
    dict_objects: dict,
) -> str:
    str_temp = str()
    keys = dict_objects.keys()
    for key in keys:
        if "NS.objects" == key and isinstance(dict_objects[key], list):
            for item in dict_objects[key]:
                if isinstance(item, int):
                    str_temp += "{}".format(item) + "\n"
                elif isinstance(item, str):
                    if 0 < len(item):
                        str_temp += item + "\n"
                elif isinstance(item, dict):
                    str_temp += (
                        parse_com_apple_messages_msmessageextensionballoonplugin_get_text(
                            item
                        )
                        + "\n"
                    )

    return str_temp


def parse_com_apple_messages_msmessageextensionballoonplugin(data) -> dict:
    debug = False
    dict_data = plistlib.loads(data)
    if debug:
        list_keys = dict_data.keys()
        print(list_keys)
        for key in list_keys:
            print("key {}: {}".format(key, dict_data[key]))
    list_objects = dict_data["$objects"]
    if debug:
        print("Iter objs")
        i = 0
        for obj in list_objects:
            print("{}:{}".format(i, obj))
            i += 1

    dict_objects = copy.deepcopy(list_objects[dict_data["$top"]["root"]])
    parse_com_apple_messages_msmessageextensionballoonplugin_objects_parse_bin(
        dict_objects, list_objects
    )

    if debug:
        print(dict_objects)

    dict_temp = dict()
    dict_temp["Body"] = (
        parse_com_apple_messages_msmessageextensionballoonplugin_get_text(dict_objects)
    )

    return dict_temp

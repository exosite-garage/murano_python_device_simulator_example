#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Murano Python Simple Device Simulator
# Copyright 2016 Exosite
# Version 1.0
#
# This python script simulates a Smart Light bulb by generating simlulated
# sensor data and taking action on a remote state variable to control on/off.
# It is written to work with the Murano example Smart Light Bulb Consumer example
# application.
#
# For more information see: http://beta-docs.exosite.com/murano/get-started
#
# Requires:
# - Tested with: Python 2.6 or Python 2.7
# - A basic knowledge of running Python scripts
#
# To run:
# Option 1: From computer with Python installed, run command:  python murano_device_simulator.py
# Option 2: Any machine with Python isntalled, double-click on murano_device_simulator.py to launch
# the Python IDE, which you can then run this script in.
#

import os
import time
import datetime
import random

import requests


try:
    input = raw_input
except ImportError:
    pass

# -----------------------------------------------------------------
# EXOSITE PRODUCT ID / SERIAL NUMBER IDENTIFIER / CONFIGURATION
# -----------------------------------------------------------------
UNSET_PRODUCT_ID = 'YOUR_PRODUCT_ID_HERE'
productid = os.getenv('SIMULATOR_PRODUCT_ID', UNSET_PRODUCT_ID)
identifier = os.getenv('SIMULATOR_DEVICE_ID', '000001')  # default identifier

SHOW_RAW_HTTP = str(os.getenv('SHOW_RAW_HTTP')).lower() == "true"
PROMPT_FOR_PRODUCTID_AND_SN = os.getenv('SIMULATOR_SHOULD_PROMPT', '1') == '1'
LONG_POLL_REQUEST_TIMEOUT = 2 * 1000  # in milliseconds

# -----------------------------------------------------------------
# ---- SHOULD NOT NEED TO CHANGE ANYTHING BELOW THIS LINE ------
# -----------------------------------------------------------------

host_address_base = os.getenv('SIMULATOR_HOST', 'm2.exosite.com')
host_address_base = os.getenv('SIMULATOR_HOST', 'm2.exosite.com')
host_address = None  # set this later when we know the product ID
https_port = 443

# LOCAL DATA VARIABLES
FLAG_CHECK_ACTIVATION = False

state = ''
temperature = 70
humidity = 50
uptime = 0
connected = True
last_modified = {}


#
# HELPER FUNCTIONS
#

def pretty_print_request(req):
    print('{}\n{}\n{}\n\n{}\n{}'.format(
        '-----------RAW REQUEST------------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body if req.body != None else '',
        '----------------------------------',
    ))

def pretty_print_respone(rsp):
    print('{}\n{}\n{}\n\n{}\n{}'.format(
        '-----------RAW RESPONSE-----------',
        'HTTP/1.1 ' + str(rsp.status_code) + ' ' + rsp.reason,
        '\n'.join('{}: {}'.format(k, v) for k, v in rsp.headers.items()),
        rsp.text if rsp.text != None else '',
        '----------------------------------',
    ))


#
# DEVICE MURANO RELATED FUNCTIONS
#

def ACTIVATE():
    try:
        request = requests.Request(
            'POST',
            "https://" + host_address + "/provision/activate",
            headers = {
                "X-Exosite-CIK": cik,
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
            },
            data = {
                'vendor': productid,
                'model': productid,
                'sn': identifier,
            }
        ).prepare()

        if SHOW_RAW_HTTP:
            pretty_print_request(request)

        # send with global session
        response = s.send(request)

        if SHOW_RAW_HTTP:
            pretty_print_respone(response)

        # HANDLE POSSIBLE RESPONSES
        if response.status == 200:
            new_cik = response.text
            print("Activation Response: New CIK: {}..............................".format(new_cik[0:10]))
            return new_cik
        elif response.status == 409:
            print("Activation Response: Device Aleady Activated, there is no new CIK")
        elif response.status == 404:
            print("Activation Response: Device Identity ({}) activation not available or check Product Id ({})".format(
                identifier,
                productid
                ))
        else:
            print("Activation Response: failed request: {} {}".format(str(response.status), response.reason))
            return None

    except Exception as e:
        # pass
        print("Exception: {}".format(e))
    return None


def GET_STORED_CIK():
    print("get stored CIK from non-volatile memory")
    try:
        f = open(productid + "_" + identifier + "_cik", "r+")  # opens file to store CIK
        local_cik = f.read()
        f.close()
        print("Stored cik: {}..............................".format(local_cik[0:10]))
        return local_cik
    except Exception as e:
        print("Unable to read a stored CIK: {}".format(e))
        return None


def STORE_CIK(cik_to_store):
    print("storing new CIK to non-volatile memory")
    f = open(productid + "_" + identifier + "_cik", "w")  # opens file that stores CIK
    f.write(cik_to_store)
    f.close()
    return True


def WRITE(WRITE_PARAMS):
    request = requests.Request(
        'POST',
        "https://" + host_address + "/onep:v1/stack/alias",
        headers = {
            "X-Exosite-CIK": cik,
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
    ).prepare()

    if SHOW_RAW_HTTP:
        pretty_print_request(request)

    # send with global session
    response = s.send(request)

    if SHOW_RAW_HTTP:
        pretty_print_respone(response)

    # HANDLE POSSIBLE RESPONSES
    if response.status_code == 204:
        # print "write success"
        return True, 204
    elif response.status_code == 401:
        print("401: Bad Auth, CIK may be bad")
        return False, 401
    elif response.status_code == 400:
        print("400: Bad Request: check syntax")
        return False, 400
    elif response.status_code == 405:
        print("405: Bad Method")
        return False, 405
    else:
        print(str(response.status), response.reason, 'failed:')
        return False, response.status

    # This code is unreachable and should be removed
    #       except Exception as err:
    # pass
    # print("exception: {}".format(str(err)))


    # return None


def READ(READ_PARAMS):
    try:
        request = requests.Request(
            'GET',
            "https://" + host_address + "/onep:v1/stack/alias?" + READ_PARAMS,
            headers = {
                "X-Exosite-CIK": cik,
                "Accept": "application/x-www-form-urlencoded; charset=utf-8"
            }
        ).prepare()

        if SHOW_RAW_HTTP:
            pretty_print_request(request)

        # send with global session
        response = s.send(request)

        if SHOW_RAW_HTTP:
            pretty_print_respone(response)

        # HANDLE POSSIBLE RESPONSES
        if response.status_code == 200:
            # print "read success"
            return True, response.text
        elif response.status_code == 401:
            print("401: Bad Auth, CIK may be bad")
            return False, 401
        elif response.status_code == 400:
            print("400: Bad Request: check syntax")
            return False, 400
        elif response.status_code == 405:
            print("405: Bad Method")
            return False, 405
        else:
            print(str(response.status_code), response.text, 'failed:')
            return False, response.status_code

    except Exception as e:
        # pass
        print("Exception: {}".format(e))
    return False, 'function exception'


def LONG_POLL_WAIT(READ_PARAMS):
    try:
        headers = {
            "X-Exosite-CIK": cik,
            "Accept": "application/x-www-form-urlencoded; charset=utf-8",
            'Request-Timeout': str(LONG_POLL_REQUEST_TIMEOUT),
        }

        if last_modified.get(READ_PARAMS) != None:
            headers['If-Modified-Since'] = last_modified.get(READ_PARAMS)

        request = requests.Request(
            'GET',
            "https://" + host_address + "/onep:v1/stack/alias?" + READ_PARAMS,
            headers = headers
        ).prepare()

        if SHOW_RAW_HTTP:
            pretty_print_request(request)

        # send with global session
        response = s.send(request)

        if SHOW_RAW_HTTP:
            pretty_print_respone(response)

        # HANDLE POSSIBLE RESPONSES
        if response.status_code == 200:
            # print "read success"
            if response.headers.get("last-modified") != None:
                # Save Last-Modified Header (Plus 1s)
                lm = response.headers.get("last-modified")
                next_lm = (datetime.datetime.strptime(lm, "%a, %d %b %Y %H:%M:%S GMT") + datetime.timedelta(seconds=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
                last_modified[READ_PARAMS] = next_lm
            return True, response.text
        elif response.status_code == 304:
            # print "304: No Change"
            return False, 304
        elif response.status_code == 401:
            print("401: Bad Auth, CIK may be bad")
            return False, 401
        elif response.status_code == 400:
            print("400: Bad Request: check syntax")
            return False, 400
        elif response.status_code == 405:
            print("405: Bad Method")
            return False, 405
        else:
            print(str(response.status), response.reason)
            return False, response.status

    except Exception as e:
        pass
        print("Exception: {}".format(e))
    return False, 'function exception'


# --------------------------
# APPLICATION STARTS RUNNING HERE
# --------------------------


# --------------------------
# BOOT
# --------------------------

# Check if CIK locally stored already
if PROMPT_FOR_PRODUCTID_AND_SN is True or productid == UNSET_PRODUCT_ID:
    print("Check for Device Parameters Enabled (hit return after each question)")
    productid = input("Enter the Murano Product ID: ")
    host_address = productid + '.' + host_address_base

    print("The Host Address is: {}".format(host_address))
    # hostok = input("If OK, hit return, if you prefer a different host address, type it here: ")
    # if hostok != "":
    #   host_address = hostok

    print("The default Device Identity is: {}".format(identifier))
    identityok = input("If OK, hit return, if you prefer a different Identity, type it here: ")
    if identityok != "":
        identifier = identityok
else:
    host_address = productid + '.' + host_address_base

start_time = int(time.time())
print("\r\n-----")
print("Murano Example Smart Lightbulb Device Simulator booting...")
print("Product Id: {}".format(productid))
print("Device Identity: {}".format(identifier))
print("Product Unique Host: {}".format(host_address))
print("-----")
cik = GET_STORED_CIK()
if cik is None:
    print("try to activate")
    act_response = ACTIVATE()
    if act_response is not None:
        cik = act_response
        STORE_CIK(cik)
        FLAG_CHECK_ACTIVATION = False
    else:
        FLAG_CHECK_ACTIVATION = True



# global requests network session
s = requests.Session()
s.cert = ('./certs/clcert.pem', './certs/clpkey.pem')

# --------------------------
# MAIN LOOP
# --------------------------
print("starting main loop")

counter = 100  # for debug purposes so you don't have issues killing this process
LOOP = True
lightbulb_state = 0
init = 1

# Check current system expected state
status, resp = READ('state')
if not status and resp == 401:
    FLAG_CHECK_ACTIVATION = True
if not status and resp == 304:
    # print("No New State Value")
    pass
if status:
    new_value = resp.split('=')
    lightbulb_state = int(new_value[1])
    if lightbulb_state == 1:
        print("Light Bulb is On")
    else:
        print("Light Bulb is Off")

try:
    while LOOP:
        uptime = int(time.time()) - start_time
        last_request = time.time()

        connection = 'Connected'
        if FLAG_CHECK_ACTIVATION:
            connection = "Not Connected"

        output_string = (
            "Connection: {0:s}, Run Time: {1:5d}, Temperature: {2:3.1f} F, Humidity: {3:3.1f} %, Light State: {4:1d}").format(connection, uptime, temperature, humidity, lightbulb_state)
        print("{}".format(output_string))

        if cik is not None and not FLAG_CHECK_ACTIVATION:
            # GENERATE RANDOM TEMPERATURE VALUE

            temperature = round(random.uniform(temperature - 0.2, temperature + 0.2), 1)
            if temperature > 120:
                temperature = 120
            if temperature < 1:
                temperature = 1
            # GENERATE RANDOM HUMIDITY VALUE
            humidity = round(random.uniform(humidity - 0.2, humidity + 0.2), 1)
            if humidity > 100:
                humidity = 100
            if humidity < 1:
                humidity = 1

            status, resp = WRITE('temperature=' + str(temperature) + '&humidity=' + str(humidity) + '&uptime=' + str(uptime))
            if not status and resp == 401:
                FLAG_CHECK_ACTIVATION = True

            # print("Look for on/off state change")
            status, resp = LONG_POLL_WAIT('state')
            if not status and resp == 401:
                FLAG_CHECK_ACTIVATION = True
            if not status and resp == 304:
                # print("No New State Value")
                pass
            if status:
                # print("New State Value: {}".format(str(resp)))
                new_value = resp.split('=')

                if lightbulb_state != int(new_value[1]):
                    lightbulb_state = int(new_value[1])
                    if lightbulb_state == 1:
                        print("Action -> Turn Light Bulb On")
                    else:
                        print("Action -> Turn Light Bulb Off")

        if FLAG_CHECK_ACTIVATION:
            if (uptime % 10) == 0:
                # print("---")
                print("Device CIK may be expired or not available (not added to product) - trying to activate")
            act_response = ACTIVATE()
            if act_response is not None:
                cik = act_response
                STORE_CIK(cik)
                FLAG_CHECK_ACTIVATION = False
            else:
                # print("Wait 10 seconds and attempt to activate again")
                time.sleep(1)

# Catch 'Ctrl+C' to not print stack trace
except KeyboardInterrupt:
    pass

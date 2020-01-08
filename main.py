import requests
import argparse
import re
import threading
import random
import time


def random_data():
    res = ""
    for i in range(16):
        res += random.choice("aAbB01")
    return res

def randomize_entries(entries):
    res = {}
    for key in entries.keys():
        res[key] = random_data()
    return res

def spam_n_times(n, url, data, index, entries):
    print("[THREAD", index, "STARTED]")
    if endless_mode:
        while True:
            if random_mode:
                entries = randomize_entries(entries)
            requests.post(url, data={**data, **entries})

    for i in range(n):
        if random_mode:
            entries = randomize_entries(entries)
        requests.post(url, data={**data, **entries})
    print("[THREAD", index, "STOPPED]")

parser = argparse.ArgumentParser(description="Google Form Spammer CLI")
parser.add_argument("-u", help="url to google form", required=True)
parser.add_argument("-c", help="count", type=int, default=10)
parser.add_argument("-t", help="threads", type=int, default=1)
parser.add_argument("--endless", help="run always", action='store_true')
parser.add_argument("--random", help="will send random data", action='store_true')

args = parser.parse_args()

count = args.c

threads = args.t

endless_mode = args.endless
random_mode = args.random

url = args.u
url_response = url.replace('viewform', 'formResponse')

print("[SCRIPT STARTING]", url)


text = requests.get(url).text

# print(text)

# Get all input fields

input_fields = re.findall(r'\<input [^\>]*\>|\<textarea [^\>]*\>', text)


hidden_fields = {}
entries = {}

for input_field in input_fields:
    name = re.findall(r' name="([^\"]*)"', input_field)
    if len(name) > 0:
        name = name[0]
    else:
        name = None

    value = re.findall(r' value="([^\"]*)"', input_field)
    
    if len(value) > 0:
        value = value[0]
    else:
        value = None

    if 'hidden' in input_field:
        print("[HIDDEN FIELD]", name, "=", value)
        hidden_fields[name] = value
    else:
        print("[INPUT]", name)
        entries[name] = "FUZZ"

print("{SPAMMING} count=", count, ", threads=", threads, ", rpt=", count // threads, sep="")
start_time = time.time()

threads_list = []
for _ in range(threads):
    x = threading.Thread(target=spam_n_times, args=(count // threads, url_response, hidden_fields, _, entries))
    threads_list.append(x)
    x.start()

for thread in threads_list:
    thread.join()

end_time = time.time()

print("~ Took", end_time - start_time, "seconds ~")
print(" -= DONE =- ")

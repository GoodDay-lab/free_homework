import json
import sys


file = json.load(open("scoring.json"))


def walk(file):
    tests = file["scoring"]
    index = 0
    while index < len(tests):
        test = tests[index]
        num = len(test["required_tests"])
        point = test["points"] // num
        for _ in range(num):
            yield point
        index += 1

        
with sys.stdin as std:
    allPoints = 0
    for point in walk(file):
        allPoints += point * (std.readline().strip() == 'ok')
    print(allPoints)

# File for creating benchmarks for all tasks in one go
import os
import subprocess


"""
TODO LIST:
1. Call cli.py with one command string
2. Make multiple calls and save output (dunno how I'm gonna do that)
#. Add joint architectures in

"""

NUM_TASKS = 20

BoW_3HOPS = {
    "name": "BoW_3HOPS",
    "is_joint": False,
    "extra_options": ["--use_bow"]
}

PE_3HOPS = {
    "name": "PE_3HOPS",
    "is_joint": False,
    "extra_options": []
}

ARCHS = [BoW_3HOPS, PE_3HOPS] # Note: Not currently having PE_3HOPS_JOINT or PE_LS_3HOPS_JOINT 

results = {}

for arch in ARCHS:
    dir_str = arch["name"]
    results[arch["name"]] = []
    
    command_calls = []

    if arch["is_joint"]:
        for i in range(NUM_TASKS):
            task_num = i + 1
            file_str = dir_str + "/task" + str(task_num)
            command_str = "python3 cli.py --file " + file_str + " --task " + str(task_num) + " "
            for opt in arch["extra_options"]:
                command_str += opt + " "
            command_calls.append(command_str)
    else:
        for i in range(NUM_TASKS):
            task_num = i + 1

            file_str = dir_str + "/task" + str(task_num)
            command_str = "python3 cli.py --file " + file_str + " --task " + str(task_num) + " "
            for opt in arch["extra_options"]:
                command_str += opt + " "
            command_calls.append(command_str)

    task_counter = 1
    for call in command_calls:
        result = {}
        print("Command Call:", call)
        try:
            result_str = str(subprocess.check_output([call], shell=True))
            splits = result_str.split('\\n')
            avg_error = splits[-2].split(" ")[-1]
            print("Avg_error:", avg_error)
        except:
            print("Task", task_counter, "caused an error")
            avg_error = -1
        
        result["task_num"] = task_counter
        result["avg_error"] = avg_error

        task_counter += 1
        results[arch["name"]].append(result)

print(results)
    
    
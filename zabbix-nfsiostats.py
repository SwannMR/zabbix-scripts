#!/usr/bin/env python
"""
Process NFS stats
"""
import pickle
import time

def main():

    loop = True
    while loop:    
        procmountstats = open("/proc/self/mountstats", "r")
        
	
        mountstats = parse_stats_file(procmountstats)
        mountstats_dict = stats_dictionary(mountstats)
        # open pickle file and dump
        output = open("/tmp/nfs-mountstats", "wb")
        pickle.dump(mountstats_dict, output)
        output.close()
        
        procmountstats.close()
        time.sleep(29)
        

def parse_stats_file(f):
    """pop the contents of a mountstats file into a dictionary,
    keyed by mount point.  each value object is a list of the
    lines in the mountstats file corresponding to the mount
    point named in the key.
    """
    ms_dict = dict()
    key = ''

    f.seek(0)
    for line in f.readlines():
        words = line.split()
        if len(words) == 0:
            continue
        if words[0] == 'device':
            key = words[4]
            new = [ line.strip() ]
        elif 'nfs' in words or 'nfs4' in words:
            key = words[3]
            new = [ line.strip() ]
        else:
            new += [ line.strip() ]
        ms_dict[key] = new
    return ms_dict

def stats_dictionary(mountstats):
    """
    Convert the mountstats list into a
    nested dictionary
    """
    process = False
    ms_dict = {}
    for key, value in mountstats.items():
    	stats_dict = {}
        for line in value:
            words = line.split()
            if words[0] == 'per-op':
                process = True
                continue
            if process:
                stats = operation_stats(line)
                for k, v in stats.items():
                    stats_dict[k] = v
            if words[0] == 'COMMIT:':
                process = False
                continue
        ms_dict[key] = stats_dict

    return ms_dict


def operation_stats(stat):
    """
    return a dictionary of the per-op statistics
    """
    op_stats = {}
    stat =  stat.split(':')
    operation = stat[0].strip()
    stats = stat[1].split()

#  How many requests we've done for this operation
    op_stats['ops'] = float(stats[0])
# How many times we've actually transmitted a RPC request for this operation. As you might have gathered from the last entry, this can exceed the operation count due to timeouts and retries.  
    op_stats['tranmissions'] = int(stats[1])
# How many times a request has had a major timeout. Major timeouts produce 'nfs: server X not responding, still trying' messages. You can have timeouts and retries without having major timeouts (and my example lines do)
    op_stats['major_timeouts'] = int(stats[2])
# This includes not just the RPC payload but also the RPC headers and so on. It closely matches the on-the-wire size.
    op_stats['bytes_sent'] = int(stats[3])
# As with bytes sent, this is the full size
    op_stats['bytes_received'] = int(stats[4])
# How long (in milliseconds) all requests spent queued for transmission before they were sent.
    op_stats['cumulative_queue_time'] = int(stats[5])
#  How long (in milliseconds) it took to get a reply back after the request was transmitted. The kernel comments call this the RPC RTT.
    op_stats['cumulatative_response_time'] = int(stats[6])
# How long (in milliseconds) all requests took from when they were initially queued to when they were completely handled. The kernel calls this the RPC execution time.
    op_stats['cumulative_total_request_time'] = int(stats[7])
    if op_stats['ops'] != 0:
        op_stats['rtt'] = op_stats['cumulatative_response_time'] / op_stats['ops']
        op_stats['exe'] = op_stats['cumulative_total_request_time'] / op_stats['ops']
    else:
	op_stats['rtt'] = 0
	op_stats['exe'] = 0

    result = {operation: op_stats}
    return result


main()


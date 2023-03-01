from kubernetes import client, config
import re, time, json

class KubernetesDefaults():
    def __init__(self):
        self.interval = 300
        self.namespace = 'nginx'
        self.container_name = 'nginx'   
        self.context = 'docker-desktop'   # N.B! Your context might be different!!!
    def loadConfig(self):
        config.load_kube_config(context=self.context)
    def apiClient(self):
        self.client = client.CoreV1Api()

def listPods(k8s):
    pods = k8s.client.list_namespaced_pod(k8s.namespace)
    return [pod.metadata.name for pod in pods.items]

def readLogs(k8s, pod_name):
    # Check the logs of the container from the last 5 mins (what we set the interval to). No need to gather older logs that have
    # already been checked.
    logs = k8s.client.read_namespaced_pod_log(pod_name, k8s.namespace, since_seconds=k8s.interval, container=k8s.container_name)
    
    # Filter only for error_logs, and caputre only errors:
    pattern = r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[error\] (.*)'
    regex = re.compile(pattern)
    filtered_lines = []
    for line in logs.splitlines():
        match = regex.match(line)
        if match:
            filtered_lines.append(line)
    return filtered_lines

def logIt(error):
    pattern = r'(?P<dateTime>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})\s+\[(?P<severity>\w+)\]\s+(?P<pid>\d{1,2})#(?P<tid>\d{1,2}):.+\*(?P<connid>\d{1,4})\s(?P<message>.+),\sclient:\s(?P<client>.+),\sserver:\s(?P<server>.+),\srequest:\s(?P<request>.+),\shost:\s(?P<host>.+),\sreferrer:\s(?P<referrer>.+)'
    # Match pattern with incomming error log
    match = re.match(pattern, error)
    if match:
        regex = match.groupdict()
        error_dict = {
            "dateTime": regex['dateTime'],
            "severity": regex['severity'],
            "processID": regex['pid'],
            "threadID": regex['tid'],
            "connectionID": regex['connid'],
            "client": regex['client'],
            "server": regex['server'],
            "request": regex['request'].strip('"'),
            "host": regex['host'].strip('"'),
            "referrer": regex['referrer'].strip('"'),
            "message": regex['message'].strip('"')
        }
        return json.dumps(error_dict)
    else:
        return None

def main():
    # load kubernetes information
    k8s = KubernetesDefaults()
    # load the Kubernetes configuration into object
    k8s.loadConfig()
    # create API client and load it into object
    k8s.apiClient()

    while True:
        # get list of pods
        pods = listPods(k8s)
        
        # start reading through the pods
        errors = []
        for pod in pods:
            pod_logs = readLogs(k8s, pod_name=pod)
            if pod_logs:
                errors.extend(pod_logs)

        if errors:
            for error in errors:
                logIt(error)
        
        # Wait 300 seconds (5 mins)
        time.sleep(k8s.interval)
    
if __name__ == "__main__":
    main()
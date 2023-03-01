from kubernetes import client, config
import re, time

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

def logIt(errors):
    for error in errors:
        # Build out the error in parts, then assemble them in an easy to read dict
        parts = error.split()
        date = parts[0]
        time = parts[1]
        severity = parts[2].strip("[]")
        error_message = " ".join(parts[3:])
        log_dict = {
            "date": date,
            "time": time,
            "info": severity,
            "message": error_message
        }
        print(log_dict)

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
            logIt(errors)
        
        # Wait 300 seconds (5 mins)
        time.sleep(k8s.interval)
    
if __name__ == "__main__":
    main()
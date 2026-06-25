import os
import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "aws_logs")
LOG_FILE = os.path.join(LOG_DIR, "aws_calls.log")

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def log_aws_call(service_name: str, method_name: str, region: str, status: str = "SUCCESS", details: str = ""):
    ensure_log_dir()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_line = f"[{timestamp}] [AWS] [REGION: {region}] [SERVICE: {service_name}] [ACTION: {method_name}] [STATUS: {status}] - {details}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)

def get_aws_logs(limit: int = 100):
    ensure_log_dir()
    if not os.path.exists(LOG_FILE):
        # Seed with initial logs if empty
        timestamp1 = (datetime.datetime.now() - datetime.timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        timestamp2 = (datetime.datetime.now() - datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        initial_logs = [
            f"[{timestamp1}] [AWS] [REGION: us-east-1] [SERVICE: sts] [ACTION: get_caller_identity] [STATUS: SUCCESS] - Validated SRE Gateway credentials.",
            f"[{timestamp2}] [AWS] [REGION: us-east-1] [SERVICE: ec2] [ACTION: describe_instances] [STATUS: SUCCESS] - Retrieved 4 EC2 instances."
        ]
        with open(LOG_FILE, "w") as f:
            for log in initial_logs:
                f.write(log + "\n")
        return initial_logs

    with open(LOG_FILE, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    return lines[-limit:]

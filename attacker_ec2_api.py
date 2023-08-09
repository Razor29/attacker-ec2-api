from flask import Flask, request, jsonify
import subprocess
import os
import signal

app = Flask(__name__)

active_processes = []


@app.route('/run', methods=['POST'])
def run_script():
    params = request.json.get('params', [])
    script_path = request.json.get('script_path')
    instances = request.json.get('instances', 1)

    if not script_path:
        return jsonify(error="Script path is required."), 400

    # Note: Validation remains essential for script_path, instances, and params.

    # Construct the parallel command
    command = ["parallel", "-j", str(instances), "python3", script_path] + params
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)

    pid = proc.pid
    active_processes.append(pid)

    return jsonify(message=f"{instances} instances of script started.", pid=pid)


@app.route('/stop_last', methods=['POST'])
def stop_last_script():
    if active_processes:
        pid = active_processes[-1]
        os.killpg(pid, signal.SIGINT)
        active_processes.remove(pid)
        return jsonify(message=f"Stopped script with PID: {pid}.")
    else:
        return jsonify(error="No active processes."), 400


@app.route('/stop_all', methods=['POST'])
def stop_all_scripts():
    for pid in active_processes:
        os.killpg(pid, signal.SIGINT)

    stopped_pids = active_processes.copy()
    active_processes.clear()

    return jsonify(message=f"Stopped all scripts. PIDs: {stopped_pids}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

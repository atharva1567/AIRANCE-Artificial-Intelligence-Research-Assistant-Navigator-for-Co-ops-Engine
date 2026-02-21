from multiprocessing.connection import Listener
from job_fetcher import fetch_all_jobs

ADDRESS = ('localhost', 6000)

def run_server():
    listener = Listener(ADDRESS, authkey=b'secret')
    print("MCP Server running...")
    while True:
        conn = listener.accept()
        print("Connection accepted from", listener.last_accepted)
        request = conn.recv()
        if request.get("action") == "fetch_jobs":
            jobs = fetch_all_jobs(request['field'], request['location'], request['remote'], request['job_type'])
            conn.send(jobs)
        conn.close()

if __name__ == "__main__":
    run_server()

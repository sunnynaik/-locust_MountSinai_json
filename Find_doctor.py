import time
from itertools import cycle
import gevent
from locust import events, HttpUser, task, constant, SequentialTaskSet
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, MasterRunner, LocalRunner
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


fileObject = open("dname.json", "r")
jsonContent = fileObject.read()
aList = json.loads(jsonContent)
d_name = cycle(iter(list(aList.items())))


class MyScript(SequentialTaskSet):

    @task
    def get_homepage(self):
        expected_response = 200
        with self.client.get("/", catch_response=True, name="Homepage") as response:
            if response.status_code == expected_response:
                response.success()
                print("homepage")
                print(" status code: " + str(response.status_code))
            else:
                response.failure("response code: " + str(response.status_code))
                print(" error: " + str(response.status_code))

    @task
    def get_doctor(self):
        expected_response = 200
        with self.client.get("/find-a-doctor", catch_response=True, name="find doctor") as response:
            if response.status_code == expected_response:
                response.success()
                print("find doctor page")
                print(" status code: " + str(response.status_code))
            else:
                response.failure("response code: " + str(response.status_code))
                print(" error: " + str(response.status_code))

    @task
    def get_doctor2(self):
        expected_response = 200
        with self.client.get("/find-a-doctor/result?search-term=Cancer%20(Oncology)&type=specialty",
                             catch_response=True, name="find doctor speciality") as response:
            if response.status_code == expected_response:
                response.success()
                print("cancer specialty")
                print(" status code: " + str(response.status_code))
            else:
                response.failure("response code: " + str(response.status_code))
                print(" error: " + str(response.status_code))

    @task
    def get_doctor3(self):
        expected_response = 200
        doctor_name = next(d_name)
        with self.client.get("https://profiles.mountsinai.org/" + doctor_name[0], catch_response=True,
                             name="find doctor for cancer profile") as response:
            if response.status_code == expected_response:
                # response.success()
                print(" status code: " + str(response.status_code))
                if doctor_name[1] in response.text:
                    print(" doctor is found: "+doctor_name[1])
                    response.success()
                else:
                    print("doctor not found ")
                    response.failure("no doctor found")



            else:
                response.failure("response code: " + str(response.status_code))
                print(" error: " + str(response.status_code))


class MyLoadTest(HttpUser):
    host = "https://www.mountsinai.org"
    wait_time = constant(1)
    tasks = [MyScript]

def checker(environment):
        while not environment.runner.state in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
            time.sleep(1)
            if environment.runner.stats.total.fail_ratio > 0.91:
                print(f"fail ratio was {environment.runner.stats.total.fail_ratio}, quitting")
                environment.runner.quit()
                return

@events.init.add_listener
def on_locust_init(environment, **_kwargs):
        # dont run this on workers, we only care about the aggregated numbers
        if isinstance(environment.runner, MasterRunner) or isinstance(environment.runner, LocalRunner):
            gevent.spawn(checker, environment)
import time
from itertools import cycle
import gevent
from locust import events, HttpUser, task, constant, SequentialTaskSet
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, MasterRunner, LocalRunner
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

fileObject = open("care_name.json", "r")
jsonContent = fileObject.read()
aList = json.loads(jsonContent)
pc_name = cycle(iter(list(aList.items())))

class MyScript(SequentialTaskSet):

    @task
    def get_homepage(self):
        # self.client.get("/")
        expected_response = 200
        with self.client.get("/", catch_response=True, name="Homepage") as response:
            if response.status_code == expected_response:
                response.success()
                print("homepage")
                print(" status code: " + str(response.status_code))
            else:
                response.failure("response code: " + str(response.status_code))
                print(" error: "+str(response.status_code))


    @task
    def get_patientcare(self):
        # self.client.get("/")
        expected_response = 200
        with self.client.get("/care", catch_response=True, name="patient care") as response:
            if response.status_code == expected_response:
                response.success()
                print("patient care page")
                print(" status code: " + str(response.status_code))
            else:
                response.failure("response code: " + str(response.status_code))
                print(" error: "+str(response.status_code))

    @task
    def get_patientcare2(self):
        # self.client.get("/")
        expected_response = 200
        with self.client.get("/care/infectious-diseases", catch_response=True, name="infectious-disease page ") as response:
            if response.status_code == expected_response:
                response.success()
                print("infectious-disease page")
                print(" status code: " + str(response.status_code))
            else:
                response.failure("response code: " + str(response.status_code))
                print(" error: "+str(response.status_code))


    @task
    def get_patientcare3(self):
        # self.client.get("/")
        care_name = next(pc_name)
        expected_response = 200
        with self.client.get("/care/infectious-diseases/services/"+care_name[0], catch_response=True,
                             name="patient care for particular infectious-diseases") as response:
            if response.status_code == expected_response:
                # response.success()
                print(" status code: " + str(response.status_code))
                if care_name[1] in response.text:
                    print("patient care found for: " + care_name[1])
                    response.success()
                else:
                    print("patient care not found ")
                    response.failure(" no patient care found")
            else:
                response.failure("response code: " + str(response.status_code))
                print(" error: " + str(response.status_code))



class MyLoadTest(HttpUser):
    host = "https://www.mountsinai.org/"
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


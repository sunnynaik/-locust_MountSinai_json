import time
from itertools import cycle
import gevent
from locust import events, HttpUser, task, constant, SequentialTaskSet
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, MasterRunner, LocalRunner
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


fileObject = open("loc_name.json", "r")
jsonContent = fileObject.read()
aList = json.loads(jsonContent)
l_name = cycle(iter(list(aList.items())))

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
    def get_location(self):
        # self.client.get("/")
        expected_response = 200
        with self.client.get("/locations", catch_response=True, name="location page") as response:
            if response.status_code == expected_response:
                response.success()
                print("location page")
                print(" status code: " + str(response.status_code))
            else:
                response.failure("response code: " + str(response.status_code))
                print(" error: "+str(response.status_code))

    @task
    def get_location2(self):
        # self.client.get("/")
        expected_response = 200
        loc_name = next(l_name)
        with self.client.get("/locations/"+loc_name[0], catch_response=True, name="find particular location ") as response:
            if response.status_code == expected_response:
                print(" status code: " + str(response.status_code))
                if loc_name[1] in response.text:
                    print("location found: "+loc_name[1])
                    response.success()
                else:
                    print("location not found ")
                    response.failure("no location found")
            else:
                response.failure("response code: " + str(response.status_code))
                print(" error: "+str(response.status_code))






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
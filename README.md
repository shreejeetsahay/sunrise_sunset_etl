Author: Shreejeet Sahay
Task:
API Documentation: https://sunrise-sunset.org/api

The task is to build a dataset for Sunrise and Sunset timing for Pune( lat=18.5204, long=73.8567) using above api using Singer.io open source ETL. 

The tap should perform the following function:
-Historical Load : load historical data since 1 Jan 2020
-Incremental Load : Append today’s data in existing target
-Transform data : Transform the timestamp from UTC to IST 


To load data we use Target. Use the following pre-built target to load the data:

meltano / target-sqlite · GitLab : https://gitlab.com/meltano/target-sqlite

Explanation:
The "sunrise_sunset_DE/virtualenvs" folder contains 3 virtual environments-
1. tap_singer- This environment has all the dependencies for the custom tap as mentioned in the task.
2. target2_singer- This environment has all the dependencies for the target-sqlite as mentioned in the task

The custom tap has been developed using python and can be found at location "sunrise_sunset_DE/virtualenvs/tap_singer/bin/tap-api.py". Please refer the comments in tap-api.py file for explanation of the code.

Now, we have a state.json file in "sunrise_sunset_DE" which initially has the below entry:
{
	"last_record": 2019-12-31
}

As you will see in the paragraphs below, when running the etl pipeline using tap-api.py and target, we pass state.json as --state argument for the tap, and this particular json file contains the date for which last record was fetched. Hence, for the current invocation, we start from the date after this date in the last record in state.json, and fetch all the records from the tap till the current date, and once the etl pipeline completes, we update state.json with the last record's date of the current invocation, so that for the next invocation, data can be appended from the date after last record's date till the current date.

As the requirement in the task was to start from 1st Jan 2020, the date has been kept as 31st December 2019 in state.json.

The "sunrise_sunset_DE/config.json" file contains the configuration required for running the target-sqlite, which has target database name specified as "data_engineer_task.db".

How the ETL has been run to create the present data_engineer_task.db?
Assumption- We are in sunrise_sunset_DE directory. So <path_till_present_working_directory> will include sunrise_sunset_DE below.
1. Activate the tap_singer virtual environment so that tap_api.py can be run.

	$source virtualenvs/tap_singer/bin/activate

2. Run the below command(--state is a necessary requirement for tap_api.py to fetch the last_record's date).

	$python3 <path_till_present_working_directory>/virtualenvs/tap_singer/bin/tap-api.py --state <path_till_present_working_directory>/state.json | <path_till_present_working_directory>/virtualenvs/target2_singer/bin/target-sqlite -c <path_till_present_working_directory>/config.json

The below is the output of the above command showing the state written to state.json, which is the last record added's date. In this case records from 1 day after 2019-12-31, i.e., 2020-01-01 till present day were added so the last record's date is 2022-07-05.
	{"last_record": "2022-07-05"}


You can find the .db file created at-
sunrise_sunset_DE/data_engineer_task.db

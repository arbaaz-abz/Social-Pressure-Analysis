SOCIAL PRESSURE ANAYSIS - An Analytics Tool

This project is an implementation of the paper
Social Pressure Analysis of Local Events using Social Media Data

https://ieeexplore.ieee.org/document/8374751

Submitted as my Final Year Project for my Undergraduate Computer Science Degree

ABOUT: 
We use the concept of social pressure to assist human users to identify and track trends
that may potentially lead to violent events. We combine existing methods of analysing
social media data for event detection, with monitoring of the social pressure that may lead
to peace violating events in the country. Our idea is to detects words and phrases
appearing on social media (preferably Twitter) that may be of interest due to their
pertinence to real-world events or movements. After identifying words and phrases that
may correspond to news or events, the social pressure is interpreted from the topic’s as weights and we also evaluate their sentiment scores over time. The results of this analysis is able to consistently detect keywords related to events before they occur, and provide valuable insight into the nature of these events.


CONFIGURING DATASET:
For my project submission, i worked on the Travel Ban & Immigration Twitter Dataset that spans from Jan - April. This dataset is provided under directory/Generate_dataset which you can extract and play around with. If you want to use a custom dataset, make sure it conforms to the format in which the sample dataset is in.

To add your own dataset, paste the csv file under directory/Generate_dataset
RUN - python3 extract_attributes.py & python3 sort_split_by_date.py

INSTALLATION:
git clone directory
pip3 install -r requirements.txt
cd directory

RUNNING: 
python3 manage.py migrate
python3 manage.py runserver


ENJOY!
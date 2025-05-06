# Installation Instructions

> *Provide step-by-step installation instructions for those who visit your GitHub project and wish to install and run the system.*

# Installation Instructions

2 months ago

added installation for Dashboard and dir for dashboard
> *Provide step-by-step installation instructions for those who visit your GitHub project and wish to install and run the system.*


## Dashboard

The Dashboard will only return data if the cluster is up and running, so it should ideally be ran after the cluster (at the very least control 
plane)is up and running. 

To install the Dashboard you need to have python3 installed. It is best to create your own virtual environment before downloading any packages. 
First, install these packages by running 

```
(optional) python3 -m venv <name of your virtual environment>
(optional) source <name of your virtual environment>/bin/activate
pip3 install streamlit pandas altair
```

After installing, you can run the dashboard by: 

```
streamlit run Dashboard.py
```

As of now, the IP addresses are hard coded in the dashboard.py file. If you want to add/remove IP addresses from the dashboard, you need to stop the dashboard (cntrl + c) and edit the file where it has: 

```
# Define etcd node endpoints
NODES = {
    "etcd1": "http://localhost:2379",
    "etcd2": "http://localhost:22379",
    "etcd3": "http://localhost:32379"
    # You can add more nodes here and the dashboard will scale dynamically
    # "etcd4": "http://localhost:42379",
    # ...
    # "etcd12": "http://localhost:122379"
}
```

Then rerun the the dashboard with `streamlit run Dashboard.py`

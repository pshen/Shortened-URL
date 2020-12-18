# Code Challenge:

Write a web application that allows users to take a long URL and convert it to a shortened URL similar to https://goo.gl/.
- [x] The program should have a form that accepts the long URL.
- [x] The program should generate a short local URL like /abc1234 and store the short URL and the long URL together in a persistent data store.
- [x] The program should redirect visitors to the long URL when the short URL is visited.
- [x] The program should track the number of times the short URL is visited.
- [x] The program should have a statistics page for the short URL, such as /abc1234/stats. Visiting this URL should show the short URL, the long URL, and the number of times the short URL was accessed.


# Constraints

- [x] This app must use a persistent data store that others can use. That means a local, in-memory system isn’t appropriate.
- [x] Don’t allow an invalid URL to be entered into the form.


# Challenges

- [x] Detect duplicate URLs. Don’t create a new short URL if one already exists.
- [ ] Record the date and time each short URL was accessed, and use a graphing library to graph the requests.

# Example:

https://bit.ly/381YTZJ will redirect user to this repo

# Implementation

## Framework
To better support API, I used the Python Falcon framework, which is a lightweight Web Framework. [Link](https://falcon.readthedocs.io/en/stable/)

## Package Requirements
In order to run the application, you need to install additional packages from pip. The required packages are listed in the `requirements.txt`.

To install them, do the following step.
```buildoutcfg
pip install -r requirements.txt
```

## Start the application
We need `gunicorn` program to start the application, the following step is to start it.
```buildoutcfg
gunicorn -b 0.0.0.0 --timeout 1200 --log-level debug --reload "src.shortened_url:get_app()"
```
The application will run on 0.0.0.0 and default port 8000.

Then you just open the browser and enter following address.
```buildoutcfg
http://localhost:8000
```

To use the shortened url and be redirected to real url, enter the following address in the browser.
```buildoutcfg
http://localhost:8000/4c9d
```

To see the statistics of this shortened url, enter the following address
```buildoutcfg
http://localhost:8000/4c9d/stats
```

## Implementation Details
- Programming Language: Python
- Web Framework: Falcon
- Data Structure: Dict(Hashmap)
- Time Complexity: O(1), because I'm using Dict for storing the shortened url to real url mapping, and the vice versa.
- Backend Storage: The mapping data is currently stored to a json file, ideally it could be stored into a NOSQL db.
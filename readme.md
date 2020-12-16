# Code Challenge:

Write a web application that allows users to take a long URL and convert it to a shortened URL similar to https://goo.gl/.
- [ ] The program should have a form that accepts the long URL.
- [x] The program should generate a short local URL like /abc1234 and store the short URL and the long URL together in a persistent data store.
- [x] The program should redirect visitors to the long URL when the short URL is visited.
- [x] The program should track the number of times the short URL is visited.
- [ ] The program should have a statistics page for the short URL, such as /abc1234/stats. Visiting this URL should show the short URL, the long URL, and the number of times the short URL was accessed.


# Constraints

- [ ] This app must use a persistent data store that others can use. That means a local, in-memory system isn’t appropriate.
- [x] Don’t allow an invalid URL to be entered into the form.


# Challenges

- [x] Detect duplicate URLs. Don’t create a new short URL if one already exists.
- [ ] Record the date and time each short URL was accessed, and use a graphing library to graph the requests.

# Example:
https://bit.ly/381YTZJ will redirect user to this repo

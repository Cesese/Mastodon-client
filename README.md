# Introduction
Sometimes I call it niuclient, sometimes I call it bunclient, I will change that in the future anyway.

So, here's a messy program I made in python because I need a cli client.

I only tested it on linux, not sure if it works on other OS

![](https://cesese.github.io/resources/1574959165-sc.png)
![](https://cesese.github.io/resources/1574959144-sc.png)

# Dependencies
* python3
* curses
* logging
* threading
* time
* mastodon.py (https://github.com/halcy/Mastodon.py)
* html
* urllib
* PIL
* aalib (http://jwilk.net/software/python-aalib)

Most of them are by default in python3. I tried on a fresh ubuntu and I only needed to install Mastodon.py.
If it says an error for another one, please tell me (to fix it you just need to install it with pip3).

Also, on ubuntu I didn't have backspace working. If that happens to you, go to the debug menu and look at the number associated with backspace, and then change the corresponding variable in view.py (it's around the beginning of the file, I grouped all the global variables)

# How to install
* Download the folder
* Install Mastodon.py :
```sh
$ pip3 install Mastodon.py
```
* run view.py and enter your credentials


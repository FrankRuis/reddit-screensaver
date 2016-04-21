# Reddit screensaver
Download images and overlay a title or comment from any subreddit. Use a config file to create a list of possible text and image subreddits, optionally add a weight to the subreddits for a weighted random choice.

An example image: a title from /r/ShowerThoughts and an image from /r/Earthporn.
![example](http://i.imgur.com/rRH9fh3.png "Example image.")

## Requirements
For the python script you will need the following libraries:  
* Pillow
* Pyyaml

These can easily be installed with pip.  
For the bash script you will need:  
* feh
* xprintidle
* xbindkeys

You will also need a font file of your choice.

## Config
You can change from which subreddits you wish to get images or texts by changing the config.yaml file.  
Usage: 
```yaml
settings:           # settings section
  user-agent: .     # you need a user agent to be able to use the reddit API
  font: arial       # the name of your font file, store this file in the same directory as the script
  font-size: 26 
  formats:          # image formats to look for in image links
  - .jpg
  - .png
  - .jpeg
  - .tiff
  - .bmp
  img-height: 480
  img-width: 840
  chars-line: 58    # maximum amount of characters per line
  count: 10         # maximum amount of images to store in the img folder
  retries: 5        # amount of times to retry if the script fails to create an image

text:               # text subreddits section, you can add multiple subreddits
  crazyideas:       # subreddit name
    max: 5          # maximum position of the submission
    min: 0          # minimum position of the submission
    sort: hot       # sort type: hot, top, controversial, new, gilded or rising
    time: all       # time span: all, hour, day, week, month, year
    stickies: false # allow stickied posts: true or false
    title: true     # get the title if true, or a random comment if false
    weight: 15      # the weight of this possibility

images:             # image subreddits section
  earthporn:
    max: 10
    min: 0
    sort: hot
    time: all
    stickies: false
    weight: 50

current:            # this section is used to store used images and texts to avoid dupolicates.
  img: []
  text: []
```

## How to use as a screensaver
I use this on a raspberry pi touchscreen kiosk. You can use any way you want to start the ```screensaver.sh``` script on boot, I started mine from the LXSession autostart file.

I use a cron job to download a new image every 10 minutes by typing ```crontab -e``` and adding:  
```*/10 * * * * python /home/pi/reddit-screensaver/redditimg.py &```  

On windows you could select the image folder created by the python script as th target for the custom slideshow screensaver.

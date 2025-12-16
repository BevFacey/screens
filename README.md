# screens

Apps for controlling and displaying on the Media Lab screens.

## Photo Slideshow

In the [photos](photos) folder the `index.html` file provides an automatic photo slideshow that displays all photos in the current directory.

### Usage

1. Place your photos in the same directory as `slideshow.html`
2. Create a `photos.json` file listing your photos:
   ```json
   [
       "photo1.jpg",
       "photo2.jpg",
       "photo3.jpg"
   ]
   ```
3. Open `slideshow.html` in a web browser

### Features

- Automatic photo cycling (5 seconds per slide)
- Smooth fade transitions
- Full-screen display
- Supports common image formats: JPG, JPEG, PNG, GIF, WebP, BMP, SVG

## Python Control

The [python-control](python-control) folder contains scripts for controlling the screens locally.

## Remote Web App

The [remote](remote) folder contains a web app that should run on each screen, allowing content to be displayed on that screen from a main control screen.

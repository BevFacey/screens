# screens
A web app for displaying on the Media Lab screens

## Photo Slideshow

The `index.html` file provides an automatic photo slideshow that displays all photos in the current directory.

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

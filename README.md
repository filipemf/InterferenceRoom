<div align="center" id="top"> 
  <img src="./.github/app.gif" alt="InterferenceRoom" />

  &#xa0;

  <!-- <a href="https://interferenceroom.netlify.app">Demo</a> -->
</div>

<h1 align="center">Interference Room</h1>

<p align="center">
  <img alt="Github top language" src="https://img.shields.io/github/languages/top/filipemf/interferenceroom?color=56BEB8">

  <img alt="Github language count" src="https://img.shields.io/github/languages/count/filipemf/interferenceroom?color=56BEB8">

  <img alt="Repository size" src="https://img.shields.io/github/repo-size/filipemf/interferenceroom?color=56BEB8">

  <img alt="License" src="https://img.shields.io/github/license/filipemf/interferenceroom?color=56BEB8">

  <!-- <img alt="Github issues" src="https://img.shields.io/github/issues/{{YOUR_GITHUB_USERNAME}}/interferenceroom?color=56BEB8" /> -->

  <!-- <img alt="Github forks" src="https://img.shields.io/github/forks/{{YOUR_GITHUB_USERNAME}}/interferenceroom?color=56BEB8" /> -->

  <!-- <img alt="Github stars" src="https://img.shields.io/github/stars/{{YOUR_GITHUB_USERNAME}}/interferenceroom?color=56BEB8" /> -->
</p>

<!-- Status -->

<!-- <h4 align="center"> 
	🚧  InterferenceRoom 🚀 Under construction...  🚧
</h4> 

<hr> -->

<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0; 
  <a href="#sparkles-features">Features</a> &#xa0; | &#xa0;
  <a href="#rocket-technologies">Technologies</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="https://github.com/filipemf" target="_blank">Author</a>
</p>

<br>

## :dart: About ##

This project is based on a professional program developed by Filipe Ferreira. This program loads ONNX and YOLOv7 models, have the options to load a video, an image, a webcam video and a live camera video feed. You can change the model from a list, select which elements you want to load, change the confidence score and the detection color. After the detection is loaded, you can detect, count objects and export the elapsed time, the counted objects and framerate to a CSV file.

## :rocket: Technologies ##

The following tools were used in this project:

- [Python](https://www.python.org/)
- [Java](https://www.java.com/en/)
- [PostgreSQL](https://www.postgresql.org/docs/)

## :sparkles: Features ##

:heavy_check_mark: Login and Register

Login screen, where is possible to access the app, if not already have sign-up, you can change to the register option.
![Alt text](https://github.com/filipemf/InterferenceRoom/blob/main/assets/login.png)

Here is possible to sign up. These two options access the Java API using REST to both login and sign up.
![Alt text](https://github.com/filipemf/InterferenceRoom/blob/main/assets/register.png)

:heavy_check_mark: Detection

Home screen, where all the avaliable options are displayed.
![Alt text](https://github.com/filipemf/InterferenceRoom/blob/main/assets/home.png)

After inserting the image source, check the checkbox to start the detection.
![Alt text](https://github.com/filipemf/InterferenceRoom/blob/main/assets/detection-on-video.png)

:heavy_check_mark: Exporting to CSV

When you have already finished the desired information, you can export the information to a CSV file.
![Alt text](https://github.com/filipemf/InterferenceRoom/blob/main/assets/detection-on-video-2.png)


## :white_check_mark: Requirements ##

Before starting, you need to have [Java](https://git-scm.com), [Python](https://nodejs.org/en/) and [PostgreSQL](https://www.postgresql.org/docs/) installed.

## :checkered_flag: Starting ##

```bash
# Clone this project
$ git clone https://github.com/filipemf/interferenceroom

# Access
$ cd interferenceroom

# Install dependencies
$ cd Frontend

# Run the project
$ python -m venv .env

# Run the project
$ pip install requirements.txt

# Start the server
$ streamlit run app_java.py

# The server will initialize in the <http://localhost:8501>
```

## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.


&#xa0;

<a href="#top">Back to top</a>

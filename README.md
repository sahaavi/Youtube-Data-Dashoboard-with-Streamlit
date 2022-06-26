# Youtube-Data-Dashoboard-with-Streamlit
## APP Link
https://sahaavi-youtube-data-dashoboard-with-st-yt-ddashboard-st-5ewq2n.streamlitapp.com/

## Setting up the conda environment 
Open the command prompt in desired locaiton by typing ```cmd``` and press enter in windows explorer address bar. <br>
*Creating new Conda Environment* <br>
```conda create -n YT_Ddashboard_St python=3.8```
*Activating the conda environment* <br>
```conda activate YT_Ddashboard_St```

Now we are going to install a couple of things
- Streamlit: pip install streamlit [to check the version: streamlit --version] for hosting our dashboard
- plotly: pip install plotly [for visualization]
- spyder: pip install spyder [IDE use whatever you want such as jupyter or vs code]

Now open spyder : type spyter and hit enter in command prompt
To open streamlit open the anaconda prompt then go to the directory where you are working. After that run the command - streamlit run YT_Ddashboard_St.py

### Requirements
go to the cmd and enter into YT_Ddashboard_St environment
run the command pip freeze
after that run the command pip freeze > requirements.txt

then upload all the files on github

## Deploy on Streamlit
go to streamlit account. Connect your github with streamlit. click on new. Then choose the repository you want to deploy. Select the python file.
Click on advance settings. Choose python version then save. After that click on deploy.

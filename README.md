# 🎵📱 The "TikTokification" of Spotify

**AUTHOR:** Vienna (So Hoi Ling)

**CANDIDATE NUMBER:** 50646

<p align="center"> 
    <img src="https://routenote.com/blog/wp-content/uploads/2020/03/Spotify-x-TikTok.jpg" alt="Project Illustration" width="50%"> 
</p>
<p align="center"><i>Understanding the correlation of TikTok trends and Spotify listening preferences</i><p>
<p align="center"><small>Source: <a href="https://routenote.com/blog/spotify-x-tiktok/">link</a></small></p>



## 🗂️ Project Overview
### What is this about?
This project examines how TikTok’s music trends translate to Spotify’s platform. By analysing audio features, playlist data, and track metadata from Spotify’s API, the study aims to **quantify the correlation between "TikTok-like" features of tracks and music popularity on Spotify**.

## 🎶 Playlists used
A variety of playlists across regions were used. 

**Global**: Top 50-Global, Viral 50-Global, Today's Top Hits  

**UK**: Top 50-UK, Viral 50-UK, Hot Hits UK  

**USA**: Top 50-USA, Viral 50-USA, Top Songs-USA  

**Singapore**: Top 50-Singapore, Viral 50-Singapore, Top Songs-Singapore


## 📈 Analysis Features  
The project focuses on analysing the following Spotify audio features for each playlist:
|    | Metric          | Value Type     | Scale                                               | Description                                                                               |
|----|-----------------|----------------|-----------------------------------------------------|-------------------------------------------------------------------------------------------|
| 1  | **Energy**      | Float          | 0.0 (least energetic) to 1.0 (most energetic)       | Represents a perceptual measure of intensity and activity                                 |
| 2  | **Tempo**       | Float          | Beats per minute (BPM)                              | Represents the speed of a track                                                           |
| 3  | **Danceability**| Float          | 0.0 (least danceable) to 1.0 (most danceable)       | Represents how suitable a track is for dancing based on a combination of musical elements |
| 4  | **Mode**        | Integer        | 0 (minor), 1 (major)                                | Represents the modality (major or minor) of a track                                       |
| 5  | **Acousticness**| Float          | 0.0 (lowest confidence) to 1.0 (highest confidence) | Represents how likely a track is to be acoustic, based on its sound characteristics       |


## 🎯 Key Objective and Methodology
Objective: Analyse the **correlation** between a track's **TikTok score** and its **popularity**

To calculate a TikTok score, I define TikTok-like features as such: 

|   | Feature                      | Description                                                   |
|---|------------------------------|---------------------------------------------------------------|
| 1 | **High Energy (>0.5)**       | More lively and engaging (capture audience retention)         |
| 2 | **High Tempo (>109BPM\*)**     | Upbeat songs (capture audience retention)                     |
| 3 | **High Danceability (>0.5)** | More rhythmically suitable for dancing (TikTok dancing trends)|
| 4 | **Major Mode (1)**           | Major key (associated with more positive moods)               |
| 5 | **Low Acousticness (<0.5)**  | Less acoustic and more produced (more stimulating)            |

*[What constitutes a fast BPM?](https://symphonynovascotia.ca/faqs/symphony-101/how-do-musicians-know-how-fast-to-play-a-piece-and-why-are-the-terms-in-italian/#:~:text=Allegro%20%E2%80%93%20fast%2C%20quickly%20and%20bright,fast%20(168%E2%80%93177%20BPM))

Consequently, I use these metrics to find to **normalise** each feature, before taking a weighted average as the TikTok score.


## ✨ Re-formatting 
All python files were reformatted using [Black](https://black.readthedocs.io/en/stable/).
All other files were reformatted using VSCode reformatter.

## ⚙️ How to Set Up 
### Step 1: Python Environment 
Recreate the environment using **pyenv** or **conda**.

**With pyenv + venv:**
```
pyenv install 3.x.x
pyenv virtualenv 3.x.x spotify-tiktok
pyenv activate spotify-tiktok
pip install -r requirements.txt
```

**With conda:**
```
conda create --name spotify-tiktok python=3.x
conda activate spotify-tiktok
pip install -r requirements.txt
```

### Step 2: Obtain Spotify API Credentials 
1. Log in on [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create an app to retrieve your Client ID and Client Secret.
3. Add the credentials to a .env file in the root directory: 
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

### Step 3: Run the Code
1. Clone the repository:
```
git clone https://github.com/w10-summative-so-hl.git  
cd w10-summative-so-hl
```
2. Run the Jupyter notebooks in ../code 


## 🧠 Rationale
**`NBO1-Data_Collection.ipynb`**
1. **`chunk_list`** was used to split the list of tracks into **batches** of 20, to avoid exceeding the API limit
2. **Robust error-handling** included when API requests exceed the allowed rate, using functions such as `time.sleep`

**`NB02-Data_Processing.ipynb`**
1. The **`Track_to_Playlist`** table was created to **map tracks to playlists**, establishing a many-to-many relationship between tracks and playlists
* **Avoids duplicate tracks** in the primary `Tracks` table, reducing data redundancy 
2. **Dynamic generation of economical data types**: `analyse_column_limits` analyses the data types and limits of each column, while `create_table` determines SQL data type based on the given limits (with buffer added as well for certain data types such as "string")

**`NB03-Data_Visualisation.ipynb**
1. **Normalized** features to create a TikTok Score to improve comparability and enhance model performance (i.e. in linear regression and DBSCAN)
2. **DBSCAN** clustering was used due to its ability to handle arbitrary shaped clusters and identify noise well. The plot was also scaled to optimise clustering.

## ✨ Overview of Insights
### **"TikTokiness" and popularity are weakly correlated**

Based on my analysis, there is a **weak positive correlation** between how closely aligned a track is to TikTok-like features and its popularity, as shown by our scatter plot of popularity against TikTok scores and that against regions. This is further reinforced by our cluster analysis, which showed the majority of data points clustered at the high TikTok score and high popularity corner of the plot. However, further analysis by playlist showed that this trend varies in different playlists - Top50 playlists did not have such a correlation unlike Viral50. 

However, this conclusion suggests opportunities for further analysis to explore stronger correlations between "TikTokiness" and popularity. Our preliminary analysis, based on a limited dataset, has already indicated a weak correlation between these two factors. By integrating more data from Spotify and TikTok, perhaps more interesting trends can be identified.


## 🚀 Possible Extensions
This project can be taken further:
* Analysing trends over different time periods (integrating data over the years pre-TikTok and post-TikTok)
* Determining if the relationship between TikTok scores and popularity is causal or correlational 
* Expand sample size to include more regions
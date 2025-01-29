import os
import json
from datetime import datetime, time
import time
import requests
import pandas as pd


def fetch_playlist_tracks(playlist_id, token):
    """
    Fetches the tracks of a given Spotify playlist using the Spotify Web API.

    Parameters:
        playlist_id (str): The Spotify playlist ID.
        token (str): The authorisation token for the Spotify API.

    Returns:
        dict: A JSON object containing the playlist data if successful, None if the request fails.
    """

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch playlist tracks. Status code: {response.status_code}")
        print("Response:", response.text)
        return None


def save_response(response, playlist_name):
    """
    Saves the response from the Spotify API (playlist data) to a JSON file.

    Parameters:
        response (dict): The data to be saved (playlist information).
        playlist_name (str): The name of the playlist to be used in the filename.

    Side effect:
        Saves the data to a file in the `../data/raw/` directory.
    """
    os.makedirs("../data/raw", exist_ok=True)
    file_path = f"../data/raw/{playlist_name}_tracks.json"

    with open(file_path, "w") as f:
        json.dump(response, f, indent=4)  # indent=4 to format the JSON nicely
    print(f"Playlist data collected and saved to {file_path} at {datetime.now()}.")


def chunk_list(list, n):
    """
    Splits a list into smaller chunks of size n.

    Parameters:
        list (list): The list to be split.
        n (int): The size of each chunk.

    Yields:
        list: Chunks of the original list, each of size n.
    """
    for i in range(0, len(list), n):
        yield list[i : i + n]


def fetch_features(track_id, token):
    """
    Fetches the audio features for a list of track IDs from the Spotify API.

    Parameters:
        track_id (list): A list of track IDs for which to fetch the audio features.
        token (str): The authorisation token for the Spotify API.

    Returns:
        list: A list of audio features for the tracks if the request is successful,
              an empty list if there is a failure.
    """
    url = f"https://api.spotify.com/v1/audio-features"
    headers = {"Authorization": f"Bearer {token}"}
    features_list = []

    # Split track IDs into batches of 20 to avoid hitting Spotify's API limit
    for batch in chunk_list(track_id, 20):
        params = {"ids": ",".join(batch)}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            features_batch = response.json().get("audio_features", [])
            features_list.extend(features_batch)
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limited. Retrying after {retry_after} seconds...")
            time.sleep(
                retry_after
            )  # to pause and retry after the rate limit is exceeded
        else:
            print(
                f"Failed to fetch track {track_id}. Status code: {response.status_code}"
            )
            print("Response:", response.text)
    return features_list


def process_playlist(playlist_name, playlist_id, token):
    """
    Fetches playlist data and audio features, processes it, and saves it to files.

    Parameters:
        playlist_name (str): The name of the playlist for naming the output files.
        playlist_id (str): The Spotify playlist ID.
        token (str): The authorisation token for the Spotify API.

    Returns:
        str: A message indicating the success of saving audio features.
    """
    # Fetch playlist tracks
    playlist_fetched = fetch_playlist_tracks(playlist_id, token)
    save_response(playlist_fetched, playlist_name)

    # Normalize JSON into DataFrame
    items = playlist_fetched["items"]
    df_playlist = pd.json_normalize(
        items, meta=[["track", "name"], ["track", "id"]], record_path=None
    )

    # Clean and rename columns
    df_playlist_cleaned = df_playlist[["track.id", "track.name"]]
    df_playlist_cleaned.columns = ["Track ID", "Track Name"]

    # Collect all track IDs into a list
    track_ids = df_playlist_cleaned["Track ID"].tolist()

    # Fetch audio features for each track
    features_list = fetch_features(track_ids, token)

    # Save raw features JSON file
    raw_features_file = f"../data/raw/{playlist_name}_features.json"
    with open(raw_features_file, "w") as f:
        json.dump(features_list, f, indent=4)
    return f"Audio features saved to {raw_features_file}."

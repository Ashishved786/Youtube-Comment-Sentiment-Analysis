import streamlit as st
import os
from Senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from YoutubeCommentScrapper import save_video_comments_to_csv, get_channel_info, youtube, get_channel_id, get_video_stats

# Streamlit page configuration (MUST be the first Streamlit command)
st.set_page_config(page_title='YouTube Sentiment Analysis', page_icon='LOGO.png', initial_sidebar_state='expanded')

# Function to delete non-matching CSV files
def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))

# Custom CSS for hiding Streamlit's default UI elements and custom styles
hide_st_style = """
    <style>
        /* Hide Streamlit default header, footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Body background color */
        .stApp {
            background-color: #282c34;
        }

        /* Sidebar background color and text color */
        .stSidebar {
            background-color: #333;
            color: white;
        }
        
        /* Sidebar title and headers */
        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5 {
            color: #ffffff;
        }
        
        /* Main title and header colors */
        h1, h2, h3, h4, h5, h6 {
            color: #61dafb;
        }
        
        /* Change subheader text color */
        .stSubheader {
            color: #ffffff;
        }

        /* Customize buttons */
        .stButton>button {
            background-color: #61dafb;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 10px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #21a1f1;
            color: white;
        }

        /* Customize download button */
        .stDownloadButton>button {
            background-color: #61dafb;
            color: white;
            padding: 10px 24px;
            font-size: 16px;
            border-radius: 8px;
            border: none;
        }
        .stDownloadButton>button:hover {
            background-color: #21a1f1;
        }

        /* Custom padding and margins */
        .stContainer {
            padding: 20px;
            margin: 10px;
        }
        
        /* Text and other element colors */
        p, .stText, .stMarkdown {
            color: #ffffff;
        }

        .stMetric {
            color: #ffffff;
        }

        /* Add padding to channel info section */
        .channel-info {
            padding-left: 30px;
        }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Sidebar input for YouTube link
st.sidebar.title("YouTube Sentiment Analysis")
st.sidebar.header("Enter YouTube Link")
youtube_link = st.sidebar.text_input("YouTube Video Link")

directory_path = os.getcwd()

# Custom Header/Banner
st.markdown("""
    <div style="background-color: #61dafb; padding: 10px;">
        <h1 style="color:black; text-align:center;">YouTube Comment Sentiment Analysis</h1>
    </div>
""", unsafe_allow_html=True)

if youtube_link:
    video_id = extract_video_id(youtube_link)
    channel_id = get_channel_id(video_id)
    
    if video_id:
        st.sidebar.write("The video ID is:", video_id)
        csv_file = save_video_comments_to_csv(video_id)
        delete_non_matching_csv_files(directory_path, video_id)
        st.sidebar.write("Comments saved to CSV!")
        st.sidebar.download_button(label="Download Comments", data=open(csv_file, 'rb').read(), file_name=os.path.basename(csv_file), mime="text/csv")

        # Fetching channel information
        channel_info = get_channel_info(youtube, channel_id)

        # Channel Information Display
        st.title("YouTube Channel Information")
        col1, col2 = st.columns([1, 3])  # Adjusted column width (Logo takes 1/4, Text takes 3/4)

        with col1:
            st.image(channel_info['channel_logo_url'], width=200)

        with col2:
            st.markdown(f"""
            <div class="channel-info">
                <h2>Channel Name:</h2>
                <h1>{channel_info['channel_title']}</h1>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("Channel Details")
        col3, col4, col5 = st.columns(3)

        with col3:
            st.metric(label="Total Videos", value=channel_info['video_count'])

        with col4:
            created_date = channel_info['channel_created_date'][:10]
            st.metric(label="Channel Created", value=created_date)

        with col5:
            st.metric(label="Subscribers", value=channel_info['subscriber_count'])

        st.subheader("Channel Description")
        st.write(channel_info['channel_description'])

        # Fetching video statistics
        stats = get_video_stats(video_id)

        st.title("Video Information")
        col6, col7, col8 = st.columns(3)

        with col6:
            st.metric(label="Total Views", value=stats["viewCount"])

        with col7:
            st.metric(label="Like Count", value=stats["likeCount"])

        with col8:
            st.metric(label="Comment Count", value=stats["commentCount"])

        # Video player
        st.video(data=youtube_link)

        # Sentiment Analysis Results
        st.subheader("Sentiment Analysis Results")
        results = analyze_sentiment(csv_file)

        col9, col10, col11 = st.columns(3)

        with col9:
            st.metric(label="Positive Comments", value=results['num_positive'])

        with col10:
            st.metric(label="Negative Comments", value=results['num_negative'])

        with col11:
            st.metric(label="Neutral Comments", value=results['num_neutral'])

        # Plotting Sentiment Data
        bar_chart(csv_file)
        plot_sentiment(csv_file)

    else:
        st.error("Invalid YouTube link")

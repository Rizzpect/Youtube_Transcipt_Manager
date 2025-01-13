# 🎥 YouTube Transcript Manager

A tool to fetch, organize, and manage YouTube video transcripts for easy access and AI training.



## 📚 Overview

The **YouTube Transcript Manager** is a powerful tool that allows you to fetch, organize, and manage YouTube video transcripts. Designed to streamline the process of creating a searchable database, this tool is particularly useful for extracting insights from content-rich channels like **Andrew Huberman** . It enables users to search specific topics , integrate with tools like Obsidian and Notion, and even prepare data for AI chatbot training.

With this tool, you can access and organize transcripts of all videos on a channel, make the content easily searchable, and store it in Markdown files for optimal use. The project also offers a fallback solution for videos that lack automatic transcripts by providing a manual transcript generator.


# 🌟 Features
- **Fetch Transcripts**: Automatically fetch and save transcripts for all videos in a YouTube channel.
- **Keyword Search**: Search for specific topics across all transcripts to quickly find relevant information.
- **Obsidian Integration**: Store transcripts as Markdown files, making them ready for integration with [Obsidian](https://obsidian.md/) for efficient note-taking and organization.
- **Error Handling**: Handles videos that do not have auto-generated transcripts, offering a manual transcript generation option.
- **AI Chatbot Training**: Combine all transcripts into a single file for training AI models or performing data analysis.

---

## 🛠️ How It Works
1. **Fetch Video URLs**: Retrieve all video URLs for a given YouTube channel ID.
2. **Fetch Transcripts**: Use the YouTube API to fetch video transcripts. The script will attempt to fetch transcripts for each video.
3. **Organize Files**: Save transcripts as Markdown files, renamed with the video title for easy identification.
4. **Keyword Search**: Users can search for specific keywords in the transcripts, allowing them to quickly locate relevant content.
5. **AI Chatbot Training**: Combine all transcripts into a single file, making it ready for AI chatbot training.

---

## 🚀 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Rizzpect/Youtube_Transcipt_Manager.git
   cd Youtube_Transcipt_Manager
   ```

2. Install dependencies:The project requires the following Python libraries and modules:

Built-in Modules (pre-installed with Python):

os – For file and directory management.
sys – To manipulate Python runtime environment.
re – For regular expressions.
shutil – For advanced file operations.
Third-Party Libraries:

google-api-python-client – For interacting with Google APIs.
youtube-transcript-api – For fetching YouTube video transcripts.

 
4. Run the script step by step (FROM A to E) to fetch and save transcripts:


---

## 🔧 Dependencies
This project uses the following Python libraries:
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api): Used to fetch video transcripts from YouTube.


## 📝 Manual Transcript Generation
For videos that do not have auto-generated transcripts, you can use the **manual transcript generator**. This tool allows you to input transcripts manually.

The manual transcript generation code is borrowed from [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api), which is licensed under the MIT License. If required, you can find the full license and credit information in the original repository.

## 📑 License
The code in this repository is licensed under the MIT License..

## 🤝 Acknowledgments
- Special thanks to [jdepoix](https://github.com/jdepoix) for creating the [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) repository, which was used to fetch transcripts.
- Inspired by the insightful content on **Alok M. Kanojia** (Dr. K) and the potential of using video transcripts to create a powerful knowledge base.



## 📧 Contact
For any questions or suggestions, feel free to open an issue or contact me directly at rizwanrak272@gmail.com.

# Gemini-powered CareAd Creator

## Overview
The Gemini-powered CareAd Creator is a simple chat application tailored for streamlined ad creation, specifically catering to care seekers. This tool integrates state-of-the-art Gemini models, allowing users to effortlessly design and manage ad creation through simple and intuitive conversations.

![Chat Interface](img/app.png)

## Getting Started

### Prerequisites
Ensure you have Python 3 installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/arunpshankar/CareAd-Creator.git
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .caread-creator
   ```

3. **Activate the virtual environment**
   ```bash
   source .caread-creator/bin/activate
   ```

4. **Upgrade pip**
   ```bash
   pip install --upgrade pip
   ```

5. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

6. **Set environment variables**
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   ```

### Running the Application

Run the application using Streamlit by executing:
```bash
streamlit run src/playground/app.py
```
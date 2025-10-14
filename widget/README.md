# Chatminds-Chatbot Widget

Welcome to the Chatminds-Chatbot Widget repository! This widget allows you to integrate a customizable chatbot into your website effortlessly.

## Features

- Responsive design for various screen sizes.
- Typing effect for bot responses.
- Customizable appearance through CSS.
- Integration via iframe for easy deployment.

## Getting Started

### Prerequisites

- Node.js installed on your machine ([Download Node.js](https://nodejs.org)).

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd chatbot-widget

2. **Install dependencies:**

   ```bash
   npm install


### Usage

1. **Run the local server**

Use a local server to serve the widget files. You can use Python's built-in HTTP server or http-server npm package for this purpose.


- For Python:


    ```bash
    # Navigate to your project directory
    cd chatbot-widget

    # Start Python 3.x HTTP server
    python -m http.server 8080

- For http-server npm package:

    ```bash
    # Install http-server if not already installed
    npm install -g http-server

    # Navigate to your project directory
    cd chatbot-widget

    # Start http-server
    http-server -p 8080

Replace 8080 with the desired port number if needed.

2. **Access the widget:**

Open your web browser and go to http://localhost:8080/chatbot-widget.html to view the chatbot widget.

3. **Embed into your website:**

Copy the iframe embed code provided in chatbot-widget.html and paste it into your website's HTML where you want the chatbot to appear.

Example:
    
    <iframe src="http://localhost:8080/chatbot-widget.html" style="width: 350px; height: 500px; border: none;"></iframe>

Adjust the width and height attributes as per your website's layout.

### Customization
**Styling:** 
Modify the CSS in chatbot-widget.html to change the appearance of the chatbot widget to match your website's design.

**Behavior:** 
Adjust the JavaScript in chatbot-widget.html for additional functionalities or integrations with your backend services.

### Support
For any issues or questions, please contact our support team at support@chatminds.com.

Happy chatting!

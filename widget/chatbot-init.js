(function() {
    // Replace with the actual URL where the chatbot widget is hosted
    const chatbotUrl = '/widget/chatbot-widget.html';
const tenantId = 'a676ff7f-f5c4-4290-9d78-8abf5219f498'; // Replace with your tenant_id

// Create an iframe element
const chatbotIframe = document.createElement('iframe');
chatbotIframe.id = 'chatbot-iframe';
chatbotIframe.src = chatbotUrl;
chatbotIframe.style.position = 'fixed';
chatbotIframe.style.bottom = '20px';
chatbotIframe.style.right = '20px';
chatbotIframe.style.width = '350px'; // Adjust width as needed
chatbotIframe.style.height = '500px'; // Adjust height as needed
chatbotIframe.style.border = 'none';
chatbotIframe.style.zIndex = '9999';

// Send tenant_id to the iframe when it has loaded
chatbotIframe.addEventListener('load', () => {
    chatbotIframe.contentWindow.postMessage({ tenant_id: tenantId }, '*');
});

// Append the iframe to the body
document.body.appendChild(chatbotIframe);
})();


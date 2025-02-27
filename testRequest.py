import requests

# URL of the API
#url = "https://fzmppztbyb.eu-central-1.awsapprunner.com/process-pdf-detectron"
# For local tests
url = "http://127.0.0.1:5000/process-pdf-detectron"
# For EC2 tests
#url = "http://51.20.34.232:80/process-pdf-advanced"
# Path to the PDF file you want to upload
file_path = "D:/RAG Research/Code/Inputs/Oblitus Pyramid.pdf"

# Open the file in binary mode
with open(file_path, 'rb') as file:
    # Prepare the file to be uploaded using 'files' argument
    files = {'pdf': file}
    
    # Send the POST request with the file
    response = requests.post(url, files=files)
    print(response)

    # Print the response from the server
    if response.status_code == 200:
        print("File uploaded successfully!")
        print("Extracted Text:", response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

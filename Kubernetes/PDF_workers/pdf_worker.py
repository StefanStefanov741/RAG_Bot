import os
import json
import uuid
import base64
import pika
from typing import List



from Preprocessing.PDF.pdfminer import pdf_to_elements

# Use the environment variable for RabbitMQ host
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")  # Use "rabbitmq" as the default

#RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = 5672  
QUEUE_NAME = 'PDF_Queue'
RESULT_QUEUE_NAME = 'PDF_Results_Queue'

tempFolder = "/tmp"
os.makedirs(tempFolder, exist_ok=True)

def elements_to_json(elements: List) -> str:
    elements_list = [{"category": element.category, "text": element.text} for element in elements]
    return json.dumps(elements_list, indent=4)

def process_pdf(pdf_path: str) -> str:
    try:
        extracted_json = elements_to_json(pdf_to_elements(pdf_path))
        os.remove(pdf_path)
        return extracted_json
    except Exception as e:
        os.remove(pdf_path)
        return {"error": str(e)}

def callback(
    ch: pika.channel.Channel,
    method: pika.spec.Basic.Deliver,
    properties: pika.spec.BasicProperties,
    body: bytes
) -> None:
    message = json.loads(body)
    pdf_content = base64.b64decode(message['pdf_content'])
    pdf_id = message['pdf_id']  # Get the unique identifier from the message
    unique_filename = f"{uuid.uuid4()}.pdf"
    pdf_path = os.path.join(tempFolder, unique_filename)

    with open(pdf_path, 'wb') as pdf_file:
        pdf_file.write(pdf_content)

    result = process_pdf(pdf_path)
    print("Processing result:", result)
    # Publish the result back to the result queue
    
    result_message = json.dumps({
        'pdf_id': pdf_id,  # Include the original ID in the result
        'result': result
    })
    
    
    result_channel = ch.connection.channel()  # Get a new channel for result publishing
    result_channel.queue_declare(queue=RESULT_QUEUE_NAME,durable = True) # Ensure the result queue exists
    result_channel.basic_publish(
        exchange='',
        routing_key=RESULT_QUEUE_NAME,
        body=result_message,  # Send the result as a JSON string
        properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
    )
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    
    
    

#connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
connection_params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
print("Waiting for PDF processing tasks. To exit press CTRL+C")
channel.start_consuming()

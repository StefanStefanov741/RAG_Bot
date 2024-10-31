import os
import json
import pika
import base64
import uuid

from flask import Flask, request, jsonify

app = Flask(__name__)

# Use the environment variable for RabbitMQ host
#RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")  # Use "rabbitmq" as the default
#RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "host.docker.internal")
RABBITMQ_PORT = 5672  
QUEUE_NAME = 'PDF_Queue'

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def welcome():
    return jsonify({"message": "Welcome to the API Gateway"}), 200




@app.route("/process-pdf-fast", methods=["POST"])
def extract_pdf_fast():
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400

    pdf_file = request.files['pdf']

    if pdf_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
   # Encode the PDF content in base64
    pdf_content = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    # Generate a unique ID for tracking this request
    pdf_id = str(uuid.uuid4())
    
    
    
    message = json.dumps({
        'pdf_id': pdf_id,
        "pdf_content": pdf_content
                          })

    # Send the message to RabbitMQ
    try:
        
        connection_params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
        connection = pika.BlockingConnection(connection_params)
        #connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message)
        connection.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "PDF processing task submitted successfully", "pdf_id": pdf_id}), 200



@app.route('/get-pdf-result/<pdf_id>', methods=['GET'])
def get_pdf_result(pdf_id):
    
    connection_params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    method_frame, header_frame, body = channel.basic_get(queue='PDF_Results_Queue', auto_ack=True)
    
    if method_frame:
        result_message = json.loads(body)
        
        # Check if the result message has the requested `pdf_id`
        if result_message['pdf_id'] == pdf_id:
            return jsonify({"status": "success", "result": result_message['result']}), 200
        else:
            # If it doesn't match, requeue the message and keep searching
            channel.basic_nack(delivery_tag=method_frame.delivery_tag)
            return jsonify({"status": "error", "message": "Result not yet available for the provided pdf_id."}), 404
    else:
        return jsonify({"status": "error", "message": "No results available in the queue."}), 404


app.run(host="0.0.0.0", port=5000, debug=True)

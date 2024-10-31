# How to run the Kubernetes Cluster locally

Video: https://www.dropbox.com/s/8vaz8g68ymdvitk/Bildschirmaufnahme%202024-10-24%20um%2017.15.07.mov?st=psiaqt9r&dl=0

Before doing the steps below: Open docker desktop, click on Settings and enable Kubernetes. Then:

## 1st Navigate to API_Gateway and build the API container:


`docker build -t api_gateway . `

then push it to your local registry (because the Kubernetes yaml file will pull the image from that registry)

`docker tag api_gateway localhost:5000/api_gateway:latest`

`docker push localhost:5000/api_gateway:latest`

Then start the deployment for the API_Gateway by telling Kubernetes to execute the yaml file

`kubectl apply -f api_gateway_deployment.yaml`

Check: When running `kubectl get all` you should now see a deployment and a pod for api_gateway. Both should be 1/1 Ready and the Pod status should be Running.

---

## 2nd run the Queue

Here we do not need to build a container as we are using a pre-made image. Navigate to the Queue folder and open the rabbitmq.yaml. Replace the hostpath with your absolute path to the queue_storage folder. The absolute path here is unfortunately required for the local cluster. It tells the pod  where it may save data on your local machine. Then run

`kubectl apply -f rabbitmq.yaml`

Check: When running `kubectl get all` you should now see a deployment and a pod for rabbitmq. Both should be 1/1 Ready and the Pod status should be Running. If you want to investigate queue you can do so by forwarding a port

`kubectl port-forward service/rabbitmq 15672:15672  `

and then moving to http://localhost:15672 in your browser. The default access credential is guest guest. 

---

## 3rd Building the PDF Worker Container

To build the PDF Worker container, please navigate to highest level directory (same level as the folders Kubernetes and Preprocessing) and use the command 


`docker build -t pdf_worker -f Kubernetes/PDF_workers/Dockerfile . `      

Reason: PDF Worker requires methods from Preprocessing. Inside a dockerfile you cannot load things from parent directories. Navigating to the parent directory and starting the build from there solves that problem. 


After that perform the same steps as in (1)

`docker tag pdf_worker localhost:5000/pdf_worker:latest`

`docker push localhost:5000/pdf_worker:latest`

Navigate to the pdf_worker folder and:

`kubectl apply -f pdf_worker_deployment.yaml`


Check: When running `kubectl get all` you should now see a deployment and a pod for pdf_worker. Both should be 1/1 Ready and the Pod status should be Running.

---

## Testing the cluster

For testing you can use the command:

`curl -X POST http://localhost:30000/process-pdf-fast \
-H "Content-Type: multipart/form-data" \
-F "pdf=@/Users/mac/Downloads/biology_paper.pdf"`


where you replace the pdf path with your pdf, that you want to try out. You should see


{
  "message": "PDF processing task submitted successfully",
  "pdf_id": "e6fc83bb-5287-4c25-8e19-ac1350ea4483"
}

to then see the result run:

curl -X GET http://localhost:30000/get-pdf-result/your_pdf_id


 Have fun :) 


*Bounty:* If you find our how to make rabbitmq store the content of the PDF_Results_Queue in the folder Queue_storage (such that the data persists after  doing a `kubectl rollout restart deployment rabbitmq` ) I'll buy you an ice cream. 

*Troubleshooting:* If your pod is throwing an error look at its logs. You can get them by first copying the pod name from kubectl get all and then using

`kubectl logs <podname>`
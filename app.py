from flask import render_template,Flask,request,Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from flipkart.data_ingestion import DataIngestion
from flipkart.rag_chain import RAGchainBuilder
import uuid
from dotenv import load_dotenv

load_dotenv()

REQUEST_COUNT=Counter("http_requests_total","Total HTTP Requests") ##Custom matrix

PREDICTION_COUNT=Counter("answer_respone","Response Answer")

def create_app():
    
    app=Flask(__name__)
    vector_store=DataIngestion().ingest(load_existing=True)
    rag_chain=RAGchainBuilder(vector_store).build_chain()
    
    @app.route("/")
    def home():
        REQUEST_COUNT.inc()
        return render_template("index.html")
    
    @app.route("/get",methods=["POST"])
    def get_response():
        PREDICTION_COUNT.inc()
        user_input=request.form["msg"]
        
        response=rag_chain.invoke(
            {"question":user_input},
            config={"configurable":{"session_id":"user-session"}}
        )
        
        return response
    
    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(),mimetype="text/plain")

    return app

if __name__=="__main__":
    app=create_app()
    app.run(host="0.0.0.0",port=5000,debug=False)
        
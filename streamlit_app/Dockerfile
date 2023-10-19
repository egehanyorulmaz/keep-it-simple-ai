# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8
EXPOSE 8080
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
# RUN pip3 install streamlit
WORKDIR /app
COPY . ./
#CMD streamlit run app.py --server.port 8080
ENTRYPOINT ["sh", "-c", "streamlit run streamlit.py --server.port=8080 --server.address=0.0.0.0"]
#ENTRYPOINT [ "streamlit" , "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
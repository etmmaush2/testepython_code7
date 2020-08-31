#Pull image
FROM python:3
#Create a workdirectory
WORKDIR /usr/src/app
# copy requirements.txt into workdir created above
COPY dependencies ./
#Install dependencies
RUN python3 -m pip install --user --no-cache-dir -r dependencies
#Copy project to workdirectory
COPY . .
#Run app
CMD ["python", "app.py"]

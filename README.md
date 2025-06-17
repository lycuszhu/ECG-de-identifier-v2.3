This is the second version of the de-identifier

Instructions:

Go inside the folder with two requirement files and run:
	pip install -r requirements.txt
	conda install --yes --file requirements_2.txt
	
The root directory has two folders:
	input: it deals with temporary uploading of the ecg files
	output: it deals with the temporary storage of the ecg files
	
Once the pip installation are completed, launch the 'app.py' located inside the 'application' folder.

After launching the python app, go to:
	http://127.0.0.1:5000/upload

 For the key part you can either add a static key in the variable key inside "application/encrpt.py" or simply add the key in the file: "application/key/key.txt" or "cardio_deiden-main/key/key.txt"

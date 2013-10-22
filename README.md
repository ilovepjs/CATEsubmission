CATEsubmission
==============

Automates the process of submitting work via CATE. 

Will present you with a list of all assignments that have pending submissions.

When you select which assignment you want to hand in it will: 
  
   - Submit your declaration
       For GitLab assignments:
           - Grab your git token from your latest commit
           - Create the cate_token.txt file for you 
       For all others:
           - Provide the file as a command line argument
   - Upload it to CATE
   - Submit it for you
   
Making handing in work easy :) 

NOTE: Call the script from the folder with your git repository 

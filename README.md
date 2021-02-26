# Project 2 - FTP Client

### High Level Approach
- Initially, this project was a lot to take in. The project description just had so much in it to process.
- Step one was to read through the entire directions of the project multiple times.
- From here, because I have had previous experience using traditional ftp clients, I started in on the code.
- I started by writing the main method for the program. (Obviously)
- I wanted to ensure that the program would only the command and one or two parameters.
- From there, I made sure I was able to properly parse out all of the individual parts or the provided ftp server urls.
- After separating all of these out and making sure they were correct with print sttements for various values, I started in on the login() method.
- I figured that for every operation, they would need to login and quit, so I created these two methods and tested out bogus random commands.
- Using print statemments for the responses from the ftp server, I was able to see what was supposed to come next.
- From here, I implemented the different ftp commands that didn't require much back and forth communication. 
- Next, I implemented the mkdir and rmdir methods with ease.
- In order to get any more functionality I had to implement PASV and figure out how to convert the pasv response into a host ip and port number.
- I then went about implementing the ls functionality, as I needed it to sort of test our the rest of the methods.
- I set up the data channel and tested what the different responses would be from this server.
- After I got ls to work I went onto the cp method.
- The cp required multiple inputs parsed for their values so I had to add specification to the inputs parsing of whether it was handling an ftp address or a local path.
- After I got this portion working, I had to figure out how to use the data channel to send and recieve files.
- After I got cp working, I just added a bool field into the cp() function in my code of whether to remove from source and sent the mv request the same route mostly.
- From here, I started testing all various inputs and adding error handling wihtin the code!
- Lastly, added some helpful documentation to the code.

### Challenges Faced
- First major challenge was in the login() method where there was supposed to be mulitple consecutive sends to the server with the right info. 
- In the ls implementation, I was stuck for a while trying to figure out how to set up a data channel.
        - With this, I had to read a lot of the provided documentation.
        - Print statements of the responses, and a lot of guessing helped me overcome this obstacle.
        - Maybe I missed the part of class where we talked about (top << 8bits) + bottom, but this was also something that notation took a while to figure out.
- Sending and receiving files over the data channel was definitely a tough part that required a lot of googling to figure out how file writing worked again. (Rusty)
        - With this, I was struggling for a while to figure out where to place the file and how to specify this, but turns out that the STOR and RETR methods handle this.
- The requirements of this project were pretty vague for this assignment in certain areas. I had to wait on Piazza a few days for responses to my questions in order to implement some of the final functionality. This was also a challenge in my eyes.

### Testing Procedure
- I tested each individual portion very thouroughly before moving on, and also tested for a few hours at the end.
- Testing started with print statements literally everywhere. I was able to test if I was parsing the command line inputs this way as well as if the server was accepting my send()s the right way.
- I tried to add exception catching as I went but this was not enough in the end.
- Finally when I completed the code I went through and used the ls command to test most of the input functionality.
- Here are some examples of how I altered the inputs with ls to test what errors were being thrown and what was just breaking everything:
        - Correct implementation.
        - Not an ftp address.
        - Wrong username.
        - No username.
        - Wrong password.
        - No password.
        - No @ symbol.
        - Invalid hostname.
        - No hostname.
        - Invalid ports.
        - No port.
        - Invalid paths.
        - No paths.
- Then I switched to mv and tested with 2 params.
        - All tests listed for ls tested again for both.
        - One of the two has to be local and one has to be ftp url.
        - Files from and to sub-directories.
        - Renaming files.
        - To paths that do not exist.
        - etc.
- From here I tested all of the different commands and filled files with specific data to make sur ethey were sending over the proper info, not just garbage.
- As I did all of these tests, I went through the code I wrote and added try/catches for various invalid logins.
- I also implemented a method that would check responses for any 4XX, 5XX, or 6XX responses and error out gracefully instead of breaking when it tried to push through.

### Final Thoughts
- I enjoyed this project very much. I found this one to be much more challenging than the first project, just because it had so many moving parts. 
- I think we could have been breifed a little better on this assignment, because there were a lot of grey areas in the directions.
- I realize some of the reason for being vague in the instructions was to make us read the documentation, which I did, and found it to be useful but hard to read.
- I now feel like I know how ftp works very intimately and that these concepts will stick with me for a long time to come.

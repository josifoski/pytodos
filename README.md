# pytodos  
  
# Simple todos vim style and nutrition + analysis python program  

First y' need to change dir_in in code after else (few lines from top)  
  
<code>
elif username == 'mfp':  
    dir_in = '/home/' + username + '/Dropbox/pytodos/'  
else:  
    dir_in = ''  
</code>
  
  
then in ~/.bashrc add alias  
alias t='python3 /home/josifoski/Dropbox/pytodos/pytodos.py '  
but change path according to your dir_in  
  
Examples:  
t r t  
t rf tod  
t a t - doing something  
t a tom % let continue with doing something  
t + t 12  
t - y 0  
  
t del rec ed 0  
t fa 1 lentil 100  
t s Beko  
  
For more examples (fetching all sys.argv lines)  
cat pytodos.py | grep sys.argv > zexamples.txt  
  
  
Good luck  
Aleksandar Josifoski about.me/josifsk

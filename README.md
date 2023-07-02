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
but change path according to your dirin  
  
Examples:  
t r t  
t rf tod  
t a t - doing something  
t a tom % let continue with doing something  
t + t 12  
t - y 0  
  
  
  
Good luck  
Aleksandar Josifoski about.me/josifsk

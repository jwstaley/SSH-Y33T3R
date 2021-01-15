from tkinter import *
from datetime import date
import paramiko, tkinter.messagebox, re, threading
class connect:
    def __init__(self,username="",password="",hostnames=None,commands=None):
        self.hostnames = hostnames
        self.username = username
        self.password = password
        self.commands = commands
        if self.hostnames == None:
            self.hostnames = []
        if commands == None:
            self.commands = []
    def send_WOL(self, log, host, mac):
        self.hostnames = [str(host)]
        self.commands = ["echo "+self.password+" | sudo -S apt-get install wakeonlan -y",str("wakeonlan "+mac)]
        return self.ConnectAndEx(log)
    def apt_update(self,log):
        self.commands = ["echo "+self.password+" | sudo -S apt-get update -y","echo "+self.password+" | sudo -S apt-get upgrade -y"]
        return self.ConnectAndEx(log)
    def ConnectAndEx(self, log):
        output = ""
        for hostname in self.hostnames:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(hostname=hostname, username=self.username, password=self.password)
            except:
                return("[!] Cannot connect to the SSH Server")
            for command in self.commands:
                output+= ("="*10 + hostname+"="*10+"\n")
                stdin, stdout, stderr = client.exec_command(command)
                output+= stdout.read().decode() 
                err = stderr.read().decode()
                if err:
                    output += err + "\n"
            if(log):
                day = date.today()
                filename = str(day.strftime("%Y-%m-%d"))+"-log.txt"
                output = "="*10+" RUN "+"="*10+"\n"+output
                output += "\n"
                with open(filename, 'a+') as file:
                    file.write(output)
        return output
class UI:
    def __init__(self, win):
        self.menu(win)
        self.wol_screen(win)
    def menu(self, win):
        menubar = Menu(win)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='WOL', command= lambda: [self.clear_grid(win), self.wol_screen(win)])
        filemenu.add_command(label='apt-update', command= lambda: [self.clear_grid(win), self.update_screen(win)])
        menubar.add_cascade(labe="Commands",menu=filemenu)
        win.config(menu=menubar)
    def update_screen(self, win):
        self.ssh = connect()
        self.lblHost=Label(text='Host:')
        self.lblHost.grid(row=1,column=0,padx=5,pady=5) 
        self.txtHost=Entry()
        self.txtHost.grid(row=1,column=1,padx=5,pady=5)
        self.btnHost=Button(text=" Add", command= self.add_user)
        self.btnHost.grid(row=1,column=2,padx=5,pady=5)
        self.lblUser=Label(text='User:')
        self.lblUser.grid(row=0,column=0,padx=5,pady=5) 
        self.txtUser=Entry()
        self.txtUser.grid(row=0,column=1,padx=5,pady=5)
        self.lblPword=Label(text='Password:')
        self.lblPword.grid(row=0,column=2,padx=5,pady=5)
        self.txtPword=Entry(show="*")
        self.txtPword.grid(row=0,column=3,padx=5,pady=5)
        self.lblHostListLabel=Label(text="Current Hosts:")
        self.lblHostListLabel.grid(row=2,column=0,padx=5,pady=5,sticky=E)
        self.lblHostList=Label(text='')
        self.lblHostList.grid(row=2,column=1,padx=5,pady=5)
        self.lblSendUpdate=Button(text="   UPDATE!   ",bg="#ff0000",activebackground="#ff6600",command=self.apt_button)
        self.lblSendUpdate.grid(row=2,column=3,padx=5,pady=5,sticky=S)
    def wol_screen(self, win):
        self.lblHost=Label(text='Host:')
        self.lblHost.grid(row=0,column=0,padx=5,pady=5) 
        self.txtHost=Entry()
        self.txtHost.grid(row=0,column=1,padx=5,pady=5)
        self.lblMAC=Label(text='MAC:')
        self.lblMAC.grid(row=0,column=2,padx=5,pady=5) 
        self.txtMAC=Entry()
        self.txtMAC.grid(row=0,column=3,padx=5,pady=5)
        self.lblUser=Label(text='User:')
        self.lblUser.grid(row=1,column=0,padx=5,pady=5) 
        self.txtUser=Entry()
        self.txtUser.grid(row=1,column=1,padx=5,pady=5)
        self.lblPword=Label(text='Password:')
        self.lblPword.grid(row=1,column=2,padx=5,pady=5) 
        self.txtPword=Entry(show="*")
        self.txtPword.grid(row=1,column=3,padx=5,pady=5)
        self.btnWOL=Button(text="   WAKE UP!   ",bg="#ff0000",activebackground="#ff6600",command=self.wol_button)
        self.btnWOL.grid(row=2,column=0,columnspan=4,padx=5,pady=5)
    def check_ip(self, string):
        regexstring = "^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        return re.match(regexstring,string)
    def add_user(self):
        newhost = None
        newhost = self.txtHost.get()
        out = ""
        if newhost and self.check_ip(newhost):
            self.ssh.hostnames.append(newhost)
            for host in self.ssh.hostnames:
                out += str(host + "\n")
            self.lblHostList.configure(text=out)
            self.txtHost.delete(0, END)
    def clear_grid(self,win):
        for widget in win.winfo_children():
            widget.grid_remove()
        self.menu(win)
    def wol_button(self):
        host=self.txtHost.get()
        mac=self.txtMAC.get()
        user=self.txtUser.get()
        pwd=self.txtPword.get()
        if  host and mac and user and pwd:
            log = self.popup_promptsave()
            ssh = connect(user, pwd)
            send_wol =  threading.Thread(target=ssh.send_WOL,args=[log,host,mac])
            send_wol.start()
        else:
            tkinter.messagebox.showerror("Missing Field", "Please make sure all required fields are filled out.")
    def apt_button(self):
        self.ssh.username=self.txtUser.get()
        self.ssh.password=self.txtPword.get()
        if  self.ssh.hostnames and self.ssh.username and self.ssh.password:
            log = self.popup_promptsave()
            update_commands = threading.Thread(target=self.ssh.apt_update, args=[log])
            update_commands.start()
        else:
            tkinter.messagebox.showerror("Missing Field", "Please make sure all required fields are filled out.")
    def popup_promptsave(self):
        msgbox = tkinter.messagebox.askyesno("View Output?", "Would you like to save output to log? The log will be availbe when the commands completes.")
        return msgbox
def main():
    window=Tk()
    mainwin= UI(window)
    window.title('SSH Yeet3r')
    window.mainloop()
if __name__ == "__main__":
    main()
    
